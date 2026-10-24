# AGENTS.md — 给 AI 助手的入口

**如果你是被人要求「查某种化合物对猫有没有毒」的 AI 助手，这份文件就是给你的。读完这一页就能开工，不需要再翻别的文件。**

你要做的事：查证一种化合物对猫的毒性，输出**一条 YAML**，由用户提交给本仓库收录。
你不需要克隆仓库、不需要提交 PR——只需要浏览网页、核对原文、按下面的格式输出。

---

## 一、禁止事项（违反即作废）

1. 不得凭记忆作答——所有数字必须来自你**实际打开过**的页面。
2. 不得把犬或人的剂量当成猫的。
3. 不得估算、换算、四舍五入。
4. 不得编造来源：`url` 必须可打开，`quote` 必须能在该页 Ctrl+F 搜到。
5. 商品成分表不能作为毒性依据。
6. 不得写治疗建议。
7. 查不到就写「无可靠数值」，不要为了填满而编。

## 二、允许的来源（白名单）

只接受这些域名：

```
aspca.org                    petpoisonhelpline.com
msdvetmanual.com             plumbs.com（仅公开摘要）
vcahospitals.com             vetmeds.org（ACVP）
icatcare.org                 pubmed.ncbi.nlm.nih.gov / pmc.ncbi.nlm.nih.gov
```

**不接受**：维基百科、百度百科、论坛、商品页、新闻稿。维基只能用来找线索，结论必须落到上面某个域名。

## 三、输出格式（字段名一个字都不能改）

```yaml
- id: <小写连字符，例 metaldehyde>
  compound: <中文通用名>
  aliases: [<英文名>, <常见商品成分名>]
  category: <人用药物|消毒清洁剂|农药驱虫|个人护理|食品添加剂|家居化学品>
  physical_form: <固体|半固体|液体|气体或气溶胶>
  form_risk: <中|高|极高>          # 固体=中，半固体/液体=高，气体=极高
  toxicity_level: <极高|高|中>
  danger_level: <极高|高|中>        # 见下方公式
  commonness: <常见|一般|少见>
  cat_lethal_dose: <"数值 单位（途径，依据）" 或 无可靠数值>
  cat_lethal_dose_url: <剂量出处 URL；无剂量则删掉本行>
  cat_dose_note: <无数字时的定性描述；可省略>
  cat_toxicity_summary: <一句中文，≤200 字>
  exposure_routes: [误食|舔舐皮肤残留|吸入|经皮]
  sources:
    - library: <ASPCA|Pet Poison Helpline|Merck Vet Manual|VCA Hospitals|ACVP|ICAT|同行评议文献>
      title: <页面标题>
      url: <完整 URL>
      accessed: <YYYY-MM-DD>
  confirmation_status: <已确认|有争议但已确认有毒>
  last_reviewed: <YYYY-MM-DD>
```

**danger_level 公式**：极高 = 非固体 且 常见或一般 且 毒性极高；中 = 固体 且 毒性中；其余为高。

**毒性分级**：极高必须能在来源里找到「少量/单次接触即致死」；仅「需要就医」不足以判极高。

## 四、交付前自检

- [ ] 每个 `url` 我都打开过，能访问
- [ ] 每句引文都能在原页面逐字搜到
- [ ] 剂量只针对猫
- [ ] 字段名与上面完全一致，没有增删
- [ ] `danger_level` 符合公式

## 五、完整版说明书

更详细的检索步骤、示例与边界情况见 [`docs/agent-task.md`](docs/agent-task.md)，
机器可读版为 [`docs/agent-task.json`](docs/agent-task.json)。

## 六、把结果交给用户

输出 YAML 后告诉用户：把这段 YAML 发到 `sakamonya@qq.com`，或粘贴到
https://sakamonya.github.io/cat-synthetic-toxins/ 的「提交收录」里。
**不要声称你已经提交。**
