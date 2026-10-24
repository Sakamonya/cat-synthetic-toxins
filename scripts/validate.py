#!/usr/bin/env python3
"""cat-synthetic-toxins 数据校验脚本。

用法:
    python scripts/validate.py

依赖: PyYAML (pip install pyyaml)

校验内容:
  - YAML 可解析、顶层结构完整
  - 主库必填字段齐全、枚举取值合法、id 唯一
  - sources 至少一条且符合「库名: 关键词」格式
  - 争议条目必须有 controversy
  - 日期格式 YYYY-MM-DD
  - 候审区 status 固定为「待确认，默认避免」

退出码: 0 = 通过, 1 = 有错误
"""

from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("缺少依赖 PyYAML，请先执行: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
MAIN = ROOT / "data" / "synthetic-compounds.yaml"
QUAR = ROOT / "quarantine" / "observations.yaml"

CATEGORIES = {
    "人用药物-外用",
    "人用药物-内服",
    "消毒清洁剂",
    "农药驱虫",
    "个人护理",
    "食品添加剂",
    "家居化学品",
}
ROUTES = {"误食", "舔舐皮肤残留", "吸入", "经皮"}
RISKS = {"极高", "高", "中"}
COMMONNESS = {"常见", "一般", "少见"}
TIERS = {"专业", "二手"}
FORMS = {"固体", "半固体", "液体", "气体或气溶胶"}
FORM_RISK = {"固体": "中", "半固体": "高", "液体": "高", "气体或气溶胶": "极高"}
RANK = {"中": 1, "高": 2, "极高": 3}
STATUSES = {"已确认", "有争议但已确认有毒"}
LIBRARIES = (
    "ASPCA",
    "Pet Poison Helpline",
    "Plumb's",
    "Merck Vet Manual",
    "同行评议文献",
    "VCA Hospitals",
    "ACVP",
)
SOURCE_RE = re.compile(r"^(?:" + "|".join(map(re.escape, LIBRARIES)) + r"):\s*\S+")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

REQUIRED_MAIN = [
    "id",
    "compound",
    "aliases",
    "category",
    "cat_lethal_dose",
    "cat_toxicity_summary",
    "exposure_routes",
    "physical_form",
    "form_risk",
    "toxicity_level",
    "danger_level",
    "commonness",
    "sources",
    "confirmation_status",
    "last_reviewed",
]
REQUIRED_QUAR = [
    "id",
    "compound",
    "aliases",
    "category_guess",
    "why_quarantined",
    "status",
    "last_reviewed",
]

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load(path: Path) -> dict:
    if not path.exists():
        err(f"找不到文件: {path.relative_to(ROOT)}")
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        err(f"{path.relative_to(ROOT)} YAML 解析失败: {exc}")
        return {}
    if not isinstance(data, dict):
        err(f"{path.relative_to(ROOT)} 顶层必须是 mapping")
        return {}
    return data


def check_date(value: object, where: str) -> None:
    if not isinstance(value, str) or not DATE_RE.match(value):
        err(f"{where}: last_reviewed 必须是 YYYY-MM-DD 字符串，当前 {value!r}")
        return
    try:
        d = dt.date.fromisoformat(value)
    except ValueError:
        err(f"{where}: last_reviewed 不是合法日期 {value!r}")
        return
    if d > dt.date.today():
        err(f"{where}: last_reviewed 不能是未来日期 ({value})")


def check_main_entries(data: dict) -> None:
    entries = data.get("entries")
    if not isinstance(entries, list) or not entries:
        err("data/synthetic-compounds.yaml: entries 必须是非空列表")
        return

    seen: set[str] = set()
    for i, e in enumerate(entries):
        where = f"主库 entries[{i}]"
        if not isinstance(e, dict):
            err(f"{where}: 必须是 mapping")
            continue
        where = f"主库 entries[{i}]({e.get('id', '?')})"

        for field in REQUIRED_MAIN:
            if field not in e or e[field] in (None, "", []):
                err(f"{where}: 缺少必填字段 {field}")

        eid = e.get("id")
        if isinstance(eid, str):
            if not ID_RE.match(eid):
                err(f"{where}: id 不符合 slug 规则 (小写+连字符), 当前 {eid!r}")
            if eid in seen:
                err(f"{where}: id 重复 {eid!r}")
            seen.add(eid)

        if not isinstance(e.get("compound"), str):
            err(f"{where}: compound 必须是字符串")
        if not isinstance(e.get("cat_toxicity_summary"), str):
            err(f"{where}: cat_toxicity_summary 必须是字符串")
        elif len(e["cat_toxicity_summary"]) > 200:
            warn(f"{where}: cat_toxicity_summary 超过 200 字")

        aliases = e.get("aliases")
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            err(f"{where}: aliases 必须是字符串列表")

        if e.get("category") not in CATEGORIES:
            err(f"{where}: category 非法 {e.get('category')!r}")

        routes = e.get("exposure_routes")
        if not isinstance(routes, list) or not routes:
            err(f"{where}: exposure_routes 必须是非空列表")
        else:
            for r in routes:
                if r not in ROUTES:
                    err(f"{where}: exposure_routes 含非法取值 {r!r}")

        form = e.get("physical_form")
        if form not in FORMS:
            err(f"{where}: physical_form 非法 {form!r}")
        elif e.get("form_risk") != FORM_RISK[form]:
            err(f"{where}: form_risk 应为 {FORM_RISK[form]}（physical_form={form}），当前 {e.get('form_risk')!r}")
        for f in ("form_risk", "toxicity_level", "danger_level"):
            if e.get(f) not in RANK:
                err(f"{where}: {f} 非法 {e.get(f)!r}")
        expect = max((e.get("form_risk") or "中", e.get("toxicity_level") or "中"), key=lambda x: RANK.get(x, 0))
        if e.get("danger_level") != expect:
            err(f"{where}: danger_level 应为 {expect}（= max(form_risk, toxicity_level)），当前 {e.get('danger_level')!r}")
        if e.get("commonness") not in COMMONNESS:
            err(f"{where}: commonness 非法 {e.get('commonness')!r}")

        status = e.get("confirmation_status")
        if status not in STATUSES:
            err(f"{where}: confirmation_status 非法 {status!r}")
        elif status == "有争议但已确认有毒":
            if not isinstance(e.get("controversy"), str) or not e["controversy"].strip():
                err(f"{where}: 争议条目必须填写 controversy")

        src = e.get("sources")
        if not isinstance(src, list) or not src:
            err(f"{where}: sources 至少需要一条")
        else:
            for s in src:
                if not isinstance(s, str) or not SOURCE_RE.match(s):
                    err(f"{where}: 来源格式应为「库名: 条目关键词」，当前 {s!r}")

        dose = e.get("cat_lethal_dose")
        if isinstance(dose, str) and dose != "无可靠数值":
            if not re.search(r"(mg|mL|ml|g|μg|ug)\s*/\s*kg", dose, re.I):
                warn(f"{where}: cat_lethal_dose 带单位才可核对，当前 {dose!r}")

        check_date(e.get("last_reviewed"), where)


def check_quarantine(data: dict) -> None:
    entries = data.get("entries")
    if not isinstance(entries, list):
        err("quarantine/observations.yaml: entries 必须是列表")
        return

    seen: set[str] = set()
    for i, e in enumerate(entries):
        if not isinstance(e, dict):
            err(f"候审区 entries[{i}]: 必须是 mapping")
            continue
        where = f"候审区 entries[{i}]({e.get('id', '?')})"

        for field in REQUIRED_QUAR:
            if field not in e or e[field] in (None, "", []):
                err(f"{where}: 缺少必填字段 {field}")

        eid = e.get("id")
        if isinstance(eid, str):
            if not ID_RE.match(eid):
                err(f"{where}: id 不符合 slug 规则, 当前 {eid!r}")
            if eid in seen:
                err(f"{where}: id 重复 {eid!r}")
            seen.add(eid)

        if e.get("category_guess") not in CATEGORIES:
            err(f"{where}: category_guess 非法 {e.get('category_guess')!r}")

        if e.get("status") != "待确认，默认避免":
            err(f"{where}: status 必须固定为「待确认，默认避免」")

        check_date(e.get("last_reviewed"), where)


def check_cross(main: dict, quar: dict) -> None:
    main_ids = {
        e.get("id") for e in main.get("entries", []) if isinstance(e, dict)
    }
    quar_ids = {
        e.get("id") for e in quar.get("entries", []) if isinstance(e, dict)
    }
    for dup in sorted(main_ids & quar_ids):
        err(f"id 同时出现在主库与候审区: {dup}（同一化合物只能存在一处）")


def main() -> int:
    main_data = load(MAIN)
    quar_data = load(QUAR)

    if main_data:
        check_main_entries(main_data)
    if quar_data:
        check_quarantine(quar_data)
    if main_data and quar_data:
        check_cross(main_data, quar_data)

    n_main = len(main_data.get("entries") or [])
    n_quar = len(quar_data.get("entries") or [])

    for w in warnings:
        print(f"[warn] {w}")
    for e in errors:
        print(f"[error] {e}")

    print(f"\n主库 {n_main} 条，候审区 {n_quar} 条，错误 {len(errors)} 个，警告 {len(warnings)} 个。")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
