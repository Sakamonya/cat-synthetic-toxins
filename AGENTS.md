# 贡献指南 / CONTRIBUTING

感谢你愿意让这个库更可靠。本项目的价值不在「条目多」，而在**每条都能被核对**。

## 一、你可以贡献什么

| 类型 | 入口 |
|---|---|
| 新增化合物条目 | [new-compound issue](.github/ISSUE_TEMPLATE/new-compound.yml) 或直接 PR |
| 修正错误 / 补充来源 | [correction issue](.github/ISSUE_TEMPLATE/correction.yml) |
| 把候审条目升级进主库 | PR，并在描述中说明补齐了哪类证据 |
| 补商品成分映射 | 后续 `products_cn.yaml`，先开 issue 讨论 |

## 二、硬性规则

1. **必须有权威来源。** 至少一个：ASPCA APCC、Pet Poison Helpline、Plumb's、Merck Vet Manual、同行评议兽医毒理学文献。
   VCA、ACVP、ICAT 可作为补充来源，但不能单独支撑「有毒」结论。
2. **每条来源必须是对象**：`library` / `title` / `url` / `accessed`。
   `url` 必须是你**亲自打开过**的具体页面，不能是首页、搜索结果页、商品页。
3. **每条结论必须有逐字引文。** 引文必须能在你给出的 `url` 页面正文里**原样搜到**（用页面内 Ctrl+F 能命中），
   一个词都不能改。**搜不到就丢弃这条结论**——这是本项目最重要的一道门槛。
   引文写进 `sources` 的 `quote` 字段。`python scripts/check_quotes.py` 会抓取页面逐条比对。
4. **商品成分表 ≠ 毒性结论。** 官网成分表只能证明产品含什么，不能证明它对猫有毒。
5. **不确定就写 `无可靠数值`。** 不要估算、不要套用犬或人的剂量、不要留空。
   「无可靠数值」的意思是「查过了没有」，不是「没毒」。
6. **剂量数字必须标明依据**：LD50 / 最小致死剂量 / 中毒剂量 / 病例报告。
   只写数字不写依据，视为不合格。
7. **不把 AI 输出当证据。** 若使用 AI 辅助整理，必须在 PR 描述中声明，并说明你如何人工回源核对。
8. **争议必须显式化。** 来源之间结论不一致时，用 `confirmation_status: 有争议但已确认有毒` +
   `controversy` 字段写清分歧。
9. **不收录**植物、纯天然草本、普通食品原料。
10. **不提供治疗建议。** 条目不写「可用 XX 解毒」「建议催吐」之类内容。
11. **示例中的 URL、日期、编号都是占位符**，不得原样提交。照抄示例等于没有来源。

## 三、新增条目的流程

```bash
# 1. fork 并克隆
git clone https://github.com/<you>/cat-synthetic-toxins.git
cd cat-synthetic-toxins

# 2. 从 main 开分支
git switch -c add/compound-name

# 3. 编辑 data/synthetic-compounds.yaml（追加到对应 category 段落末尾）
#    字段定义见 data/schema.yml

# 4. 自检
python scripts/validate.py        # 若脚本尚未合入，请手工对照 data/schema.yml

# 5. 提交
git add data/synthetic-compounds.yaml
git commit -m "data: 新增 <化合物中文名>"
git push -u origin add/compound-name
```

然后开 PR，按模板填写。

## 四、条目写法示例

```yaml
  - id: compound-slug
    compound: 中文通用名
    aliases:
      - English Name
      - 商品常见写法
    category: 人用药物
    physical_form: 固体
    form_risk: 中
    toxicity_level: 高
    danger_level: 高
    commonness: 常见
    cat_lethal_dose: 无可靠数值
    cat_toxicity_summary: 一句话说明机制或主要症状，不超过 200 字。
    exposure_routes:
      - 误食
    sources:
      - library: ASPCA
        title: 条目标题
        url: https://example.com/替换成真实页面地址
        accessed: "2026-10-24"   # 填你实际访问的日期
        quote: "该页面中支撑本结论的那句英文原文，必须逐字一致"

    confirmation_status: 已确认
    last_reviewed: "2026-10-24"
```

注意事项：

- 缩进 2 空格，不用 Tab。
- 中文标点用全角，但 YAML 的 `:` 与 `-` 用半角。
- `id` 全小写、连字符分隔，一旦合并不得修改（外部可能已引用）。
- `last_reviewed` 填你**真正核对来源**的日期，不是 PR 提交日期。

## 五、审核标准

维护者会逐条检查 [`data/schema.yml`](data/schema.yml) 末尾的 `admission_checklist`：

- [ ] 是人工合成化合物
- [ ] 有至少一个权威来源明确认定对猫有毒/有害/致死
- [ ] 每个 `url` 都亲自打开过，且页面上确实写了该结论
- [ ] 每条结论都有逐字引文（`sources[].quote`），且 `check_quotes.py` 全部通过
- [ ] `cat_lethal_dose` 有出处或诚实标「无可靠数值」
- [ ] 剂量数字都标明了依据（LD50 / 最小致死 / 中毒剂量 / 病例报告）
- [ ] 暴露途径覆盖家庭主要场景
- [ ] 争议条目写清分歧与收录理由
- [ ] 没有把「可能」「据说」「理论上」当作唯一依据

不符合的不会被直接拒绝，而是**转到 `quarantine/observations.yaml`** 并说明缺哪类证据。这不是否定贡献，是维持主库的可信度。

## 六、Commit 约定

```
data: 新增 <化合物>
data: 修正 <化合物> 的 <字段>
quarantine: 将 <化合物> 移入候审区
docs: 更新 <文档>
schema: 变更 <字段> 定义
```

前缀：`data` / `quarantine` / `docs` / `schema` / `chore`。

## 七、复核机制

- 每条记录带 `last_reviewed`。
- 超过 **12 个月**未复核的条目视为「待复核」，欢迎开 PR 更新日期并确认来源仍有效。
- 权威来源若改版导致关键词失效，请更新关键词并在 PR 中说明。

## 八、行为准则

讨论聚焦证据，不针对人。涉及动物中毒的真实案例时，请移除个人信息。不要发布可能被误用的操作性细节（如具体致死剂量用于伤害动物）。
