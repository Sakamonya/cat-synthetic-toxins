# cat-synthetic-toxins · 养猫家庭人工合成化合物毒性速查库

> 一个结构化、可审核、来源可追溯的中文速查库，只收录**已确认对猫有毒**的人工合成化合物。

⚠️ **本项目不替代兽医诊断。** 怀疑中毒请立即联系兽医或宠物中毒热线，并带上产品包装。详见 [DISCLAIMER.md](DISCLAIMER.md)。

---

## 为什么做这个

养猫家庭里最危险的东西，往往不是「看起来有毒」的，而是**对人低毒、对猫剧毒**的合成化合物：一支生发水里的米诺地尔、一支犬用驱虫滴剂里的百灭宁、一片感冒药里的对乙酰氨基酚。这些信息目前分散在 ASPCA、Pet Poison Helpline、Plumb's、Merck Vet Manual 等英文来源里，中文世界缺少可核对的结构化版本。

本库做三件事：

1. **结构化** —— 每条记录字段固定，可机读、可搜索、可比对。
2. **可审核** —— 每条结论必须挂到权威来源条目上，AI 生成内容不作为证据。
3. **可追溯** —— 争议条目写明争议点，未核实的数据写「待核」而不是猜。

## 范围

**收录**（人工合成化合物）：

| 类别 | 举例 |
|---|---|
| 人用药物-外用 | 米诺地尔、5-氟尿嘧啶、卡泊三醇、外用 NSAID 凝胶 |
| 人用药物-内服 | 对乙酰氨基酚、布洛芬、伪麻黄碱、SSRI、ADHD 兴奋剂 |
| 消毒清洁剂 | PCMX、苯酚/甲酚、季铵盐、含氯漂白剂 |
| 农药驱虫 | 除虫菊酯/百灭宁、有机磷/氨基甲酸酯、聚乙醛、硼酸 |
| 个人护理 | 含合成香精的洗护产品（多在候审区） |
| 食品添加剂 | 木糖醇等（目前均在候审区） |
| 家居化学品 | 乙二醇防冻液、樟脑/萘防蛀剂 |

**不收录**：植物、纯天然草本、普通食品原料大清单。

## 准入规则

一条记录进入主库，必须满足：

- ✅ 是人工合成化合物
- ✅ 至少一个权威来源**明确认定对猫有毒 / 有害 / 致死**：
  `ASPCA APCC`、`Pet Poison Helpline`、`Plumb's Veterinary Drug Handbook`、`Merck Veterinary Manual`、同行评议兽医毒理学文献
- ✅ 每条来源写成 `库名: 条目关键词`
- ❌ 只有「数据有限」「理论推断」「谨慎使用」的 → 进 [`quarantine/observations.yaml`](quarantine/observations.yaml)
- ❌ 商品官方成分表只能作为「成分来源」，不能作为毒性结论来源

> 核心原则：**不确定 = 不安全**。成分表不全、含高风险结构、标注「犬用」、含精油香精的产品，默认不用于猫周围。

## 仓库结构

```
.
├── README.md
├── DISCLAIMER.md                     # 免责声明（必读）
├── CONTRIBUTING.md                   # 贡献与审核流程
├── data/
│   ├── schema.yml                    # 字段契约与准入检查清单
│   └── synthetic-compounds.yaml      # 主库：已确认对猫有毒
├── quarantine/
│   └── observations.yaml             # 候审区：待确认，默认避免
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── new-compound.yml          # 提交新化合物
    │   ├── correction.yml            # 报错 / 修正来源
    │   └── config.yml
    └── pull_request_template.md
```

## 数据字段

| 字段 | 说明 |
|---|---|
| `id` | 稳定英文 slug，合并后不改名 |
| `compound` | 中文通用名 |
| `aliases` | 英文名 / 商品常见成分名 |
| `category` | 七类之一 |
| `cat_lethal_dose` | 有出处才填；否则一律 `待核` |
| `cat_toxicity_summary` | 一句话机制或症状 |
| `exposure_routes` | 误食 / 舔舐皮肤残留 / 吸入 / 经皮 |
| `physical_form` | 固体 / 半固体 / 液体 / 气体或气溶胶 |
| `form_risk` | 形态基线风险：固体=中，半固体=高，液体=高，气体=极高 |
| `toxicity_level` | **毒性**：极高 / 高 / 中（与形态无关） |
| `danger_level` | **合成风险** = max(form_risk, toxicity_level)，由脚本校验 |
| `commonness` | **常见程度**：常见 / 一般 / 少见（中国普通养猫家庭的出现概率） |
| `cat_lethal_dose_url` | 剂量数字的直接出处链接 |
| `sources` | `库名: 条目关键词`，至少一条 |
| `confirmation_status` | 已确认 / 有争议但已确认有毒 |
| `controversy` | 争议条目必填，说明分歧点 |
| `last_reviewed` | 最近人工核对来源的日期 |

完整定义与取值枚举见 [`data/schema.yml`](data/schema.yml)。

## 当前状态

- **主库 21 条**，覆盖上述全部类别
- **候审区 8 条**，均标注「待确认，默认避免」
- **3 条有经核实的剂量数字**（对乙酰氨基酚、乙二醇、聚乙醛），其余 18 条为「待核」
- 公开权威来源（Merck 专题页）大多只给犬剂量或定性描述，猫的数值剂量本身稀缺，因此不强行填满

## 怎么用

```bash
# 查某个成分（需要 yq；没有的话直接搜文本也行）
yq '.entries[] | select(.aliases[] | test("Permethrin"; "i"))' data/synthetic-compounds.yaml

# 只看名称与风险等级
yq -r '.entries[] | "\(.compound)\t\(.household_risk)"' data/synthetic-compounds.yaml

# 找超过一年没复核的条目
yq -r '.entries[] | select(.last_reviewed < "2025-10-24") | .id' data/synthetic-compounds.yaml
```

## 参与贡献

欢迎补充条目、修正来源、指出错误。请先读 [CONTRIBUTING.md](CONTRIBUTING.md)，并确认你的改动符合准入规则。**报错也是贡献**——如果某条结论与权威来源不符，请开 `correction` issue。

## 路线图

- [ ] 为 `sources` 增加可点击 URL 字段，并逐条回源
- [ ] 补齐高优先级条目的 `cat_lethal_dose`（带单位与出处）
- [ ] 增加 `products_cn.yaml`：国内常见商品 → 成分 → 条目 id 的映射
- [ ] 生成静态网页版速查表（可离线、可打印）
- [ ] 中英文双语条目

## 许可

尚未确定（见 issue 讨论）。在确定前，请勿将本项目内容用于商业再分发。
