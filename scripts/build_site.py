#!/usr/bin/env python3
"""把 data/synthetic-compounds.yaml 渲染成单页离线速查表 docs/index.html。"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "synthetic-compounds.yaml"
QUAR = ROOT / "quarantine" / "observations.yaml"
OUT = ROOT / "docs" / "index.html"

CSS = """
:root{
  --bg:#f6f7f9; --card:#fff; --ink:#1a1d21; --muted:#6b7280; --line:#e5e7eb;
  --red:#b42318; --redbg:#fef3f2; --orange:#b54708; --orangebg:#fffaeb;
  --yellow:#854d0e; --yellowbg:#fefce8; --blue:#175cd3; --bluebg:#eff8ff;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  line-height:1.6;font-size:15px}
.wrap{max-width:1080px;margin:0 auto;padding:28px 18px 64px}
header h1{font-size:26px;margin:0 0 6px;letter-spacing:-.3px}
header .sub{color:var(--muted);font-size:13px;margin:0}
.disclaimer{margin:18px 0 22px;padding:14px 16px;border-radius:10px;
  background:var(--redbg);border:1px solid #fecdca;color:#7a271a;font-size:13.5px}
.disclaimer b{color:var(--red)}
.toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:0 0 14px}
input[type=search]{flex:1 1 260px;min-width:200px;padding:9px 12px;border:1px solid var(--line);
  border-radius:8px;background:#fff;font-size:14px;outline:none}
input[type=search]:focus{border-color:#98a2b3;box-shadow:0 0 0 3px rgba(23,92,211,.08)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{padding:6px 11px;border-radius:999px;border:1px solid var(--line);background:#fff;
  font-size:12.5px;color:#344054;cursor:pointer;user-select:none;white-space:nowrap}
.chip:hover{border-color:#98a2b3}
.chip.on{background:#1a1d21;color:#fff;border-color:#1a1d21}
.count{color:var(--muted);font-size:12.5px;margin-left:auto}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;
  display:flex;flex-direction:column;gap:8px;break-inside:avoid}
.card h2{font-size:16.5px;margin:0;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.badge{font-size:11.5px;padding:2px 8px;border-radius:999px;font-weight:600;letter-spacing:.2px}
.b-extreme{background:var(--redbg);color:var(--red);border:1px solid #fecdca}
.b-high{background:var(--orangebg);color:var(--orange);border:1px solid #fedf89}
.b-mid{background:var(--yellowbg);color:var(--yellow);border:1px solid #fde68a}
.b-soft{background:#f2f4f7;color:#475467;border:1px solid var(--line)}
.meta{display:flex;flex-wrap:wrap;gap:6px;font-size:12px;color:var(--muted)}
.meta span{background:#f2f4f7;border-radius:6px;padding:2px 7px}
.aliases{font-size:12px;color:var(--muted);word-break:break-word}
.dose{font-size:13.5px;padding:9px 11px;border-radius:8px;background:var(--bluebg);
  border:1px solid #d1e9ff;color:#0b4a8f}
.dose.none{background:#f9fafb;border-color:var(--line);color:var(--muted)}
.summary{font-size:13.5px;margin:0}
.srcs{font-size:12px;border-top:1px dashed var(--line);padding-top:8px;display:flex;flex-direction:column;gap:3px}
.srcs a{color:var(--blue);text-decoration:none;word-break:break-all}
.srcs a:hover{text-decoration:underline}
.empty{padding:40px;text-align:center;color:var(--muted);display:none}
footer{margin-top:28px;color:var(--muted);font-size:12px;border-top:1px solid var(--line);padding-top:14px}
@media print{
  body{background:#fff;font-size:11pt}
  .toolbar,.chips,.count,footer .noprint{display:none!important}
  .wrap{max-width:none;padding:0}
  .grid{display:block}
  .card{border:1px solid #ddd;margin:0 0 8px;page-break-inside:avoid}
  a{color:#000;text-decoration:none}
  .disclaimer{background:#fff;border:1px solid #999}
}
"""

JS = """
const data = __DATA__;
const state = {q:'', danger:'', common:'', cat:''};
const dangerRank = {'极高':3,'高':2,'中':1};
const card = document.getElementById('grid');
const empty = document.getElementById('empty');
const countEl = document.getElementById('count');

function norm(s){return (s||'').toLowerCase()}
function match(e){
  const q = norm(state.q);
  if (q){
    const hay = norm([e.compound,...(e.aliases||[]),e.cat_toxicity_summary,e.cat_dose_note||''].join(' '));
    if (!hay.includes(q)) return false;
  }
  if (state.danger && e.danger_level !== state.danger) return false;
  if (state.common && e.commonness !== state.common) return false;
  if (state.cat && e.category !== state.cat) return false;
  return true;
}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function badge(level){
  const cls = level==='极高'?'b-extreme':level==='高'?'b-high':'b-mid';
  return `<span class="badge ${cls}">危险 ${esc(level)}</span>`;
}
function render(){
  const rows = data.filter(match).sort((a,b)=>
    (dangerRank[b.danger_level]-dangerRank[a.danger_level]) ||
    (b.commonness==='常见')-(a.commonness==='常见') ||
    a.compound.localeCompare(b.compound,'zh'));
  countEl.textContent = `显示 ${rows.length} / ${data.length} 条`;
  empty.style.display = rows.length? 'none':'block';
  card.innerHTML = rows.map(e=>{
    const dose = e.cat_lethal_dose && e.cat_lethal_dose!=='无可靠数值'
      ? `<div class="dose"><b>剂量：</b>${esc(e.cat_lethal_dose)}</div>`
      : e.cat_dose_note
        ? `<div class="dose"><b>危险剂量：</b>${esc(e.cat_dose_note)}</div>`
        : `<div class="dose none"><b>剂量：</b>无可靠数值（公开来源未给出猫的数值）</div>`;
    const srcs = (e.sources||[]).map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.library)} · ${esc(s.title)}</a>`).join('');
    return `<article class="card">
      <h2>${esc(e.compound)} ${badge(e.danger_level)}</h2>
      <div class="meta">
        <span>${esc(e.category)}</span>
        <span>${esc(e.physical_form)}</span>
        <span>常见程度：${esc(e.commonness)}</span>
        <span>毒性：${esc(e.toxicity_level)}</span>
      </div>
      <div class="aliases">${esc((e.aliases||[]).join(' / '))}</div>
      ${dose}
      <p class="summary">${esc(e.cat_toxicity_summary)}</p>
      <div class="meta">${(e.exposure_routes||[]).map(r=>`<span>${esc(r)}</span>`).join('')}</div>
      <div class="srcs">${srcs}</div>
    </article>`;
  }).join('');
}
document.querySelectorAll('.chip[data-filter]').forEach(chip=>{
  chip.addEventListener('click',()=>{
    const f = chip.dataset.filter, v = chip.dataset.value;
    state[f] = state[f]===v ? '' : v;
    document.querySelectorAll(`.chip[data-filter="${f}"]`).forEach(c=>{
      c.classList.toggle('on', c.dataset.value===state[f]);
    });
    render();
  });
});
document.getElementById('q').addEventListener('input', ev=>{ state.q = ev.target.value; render(); });
document.getElementById('print').addEventListener('click', ()=>window.print());
render();
"""


def build() -> None:
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    entries = data["entries"]
    quar = []
    if QUAR.exists():
        quar = (yaml.safe_load(QUAR.read_text(encoding="utf-8")) or {}).get("entries", [])

    cats = sorted({e["category"] for e in entries})
    dangers = ["极高", "高", "中"]
    commons = ["常见", "一般", "少见"]

    def chips(field, values):
        return "".join(
            f'<button class="chip" data-filter="{field}" data-value="{v}">{v}</button>' for v in values
        )

    payload = [
        {
            "compound": e["compound"],
            "aliases": e.get("aliases", []),
            "category": e["category"],
            "physical_form": e["physical_form"],
            "danger_level": e["danger_level"],
            "toxicity_level": e["toxicity_level"],
            "commonness": e["commonness"],
            "exposure_routes": e.get("exposure_routes", []),
            "cat_lethal_dose": e.get("cat_lethal_dose", ""),
            "cat_dose_note": e.get("cat_dose_note", ""),
            "cat_toxicity_summary": e.get("cat_toxicity_summary", ""),
            "sources": e.get("sources", []),
        }
        for e in entries
    ]

    rows = "".join(
        f'<tr><td>{q["compound"]}</td><td>{q["category_guess"]}</td>'
        f'<td>{q["why_quarantined"]}</td></tr>'
        for q in quar
    )

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>养猫家庭人工合成化合物毒性速查库</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>养猫家庭 · 人工合成化合物速查</h1>
  <p class="sub">仅收录已确认对猫有毒的人工合成化合物 · 共 {len(entries)} 条 · 最后复核 2026-10-24</p>
</header>

<div class="disclaimer">
  <b>⚠ 不替代兽医诊断。</b>怀疑中毒请立即联系兽医或宠物中毒热线，带上产品包装。
  本页为建议性参考，不担保完整或最新；剂量与结论均标注来源，请以来源原文为准。
  <b>查不到数值 ≠ 安全</b>——标「无可靠数值」的条目同样需要避开。<br>危险程度规则：非固体 <b>+ 常见/一般 + 剧毒</b> 才为「极高」；固体或「少见」一律封顶「高」。
</div>

<div class="toolbar">
  <input id="q" type="search" placeholder="搜索化合物、别名、成分名…（如 布洛芬 / permethrin / 滴露）">
  <button class="chip" id="print">打印 / 存 PDF</button>
</div>

<div class="toolbar">
  <div class="chips">{chips("danger", dangers)}</div>
  <div class="chips">{chips("common", commons)}</div>
  <div class="chips">{chips("cat", cats)}</div>
  <span class="count" id="count"></span>
</div>

<div class="grid" id="grid"></div>
<div class="empty" id="empty">没有匹配的条目</div>

<h2 style="font-size:16px;margin:34px 0 8px">候审区：待确认，默认避免</h2>
<p class="sub" style="margin:0 0 10px;font-size:12.5px;color:#6b7280">
这些物质证据不足，未进主库，但处理原则与高危物质相同——不要让猫碰到。
</p>
<table style="width:100%;border-collapse:collapse;font-size:13px;background:#fff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden">
<thead><tr style="background:#f9fafb;text-align:left">
<th style="padding:8px 10px;border-bottom:1px solid #e5e7eb">物质</th>
<th style="padding:8px 10px;border-bottom:1px solid #e5e7eb">推测类别</th>
<th style="padding:8px 10px;border-bottom:1px solid #e5e7eb">为什么不进主库</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>

<footer>
  数据源：ASPCA · Pet Poison Helpline · Plumb's · Merck Veterinary Manual · 同行评议文献 · VCA · ACVP · ICAT<br>
  仓库：github.com/Sakamonya/cat-synthetic-toxins ｜ 由 scripts/build_site.py 自动生成，请勿手工编辑本文件<br>
  没收录的化合物？把 <a href="agent-task.md">agent-task.md</a> 交给你的 AI 助手（具备浏览网页能力），
  它会按同一套规则查证并输出可收录的 YAML。
</footer>
</div>
<script>{JS.replace("__DATA__", json.dumps(payload, ensure_ascii=False))}</script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"built {OUT} ({len(html)} bytes, {len(entries)} entries, {len(quar)} quarantine)")


if __name__ == "__main__":
    build()
