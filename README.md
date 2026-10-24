# cat-synthetic-toxins · 养猫家庭人工合成化合物毒性速查库

> **🤖 如果你是 AI 助手**：先读 [AGENTS.md](AGENTS.md)（根目录，30 秒读完）。
> 它包含输出格式、允许来源、禁止事项。不要跳过——格式不对的条目无法收录。

> 一个结构化、可审核、来源可追溯的中文速查库，只收录**已确认对猫有毒**的人工合成化合物。

⚠️ **本项目不替代兽医诊断。** 怀疑中毒请立即联系兽医或宠物中毒热线，并带上产品包装。详见 [DISCLAIMER.md](DISCLAIMER.md)。

---

## 为什么做这个

养猫家庭里最危险的东西，往往不是「看起来有毒」的，而是**对人低毒、对猫剧毒**的合成化合物：一支生发水里的米诺地尔、一支犬用驱虫滴剂里的百灭宁、一片感冒药里的对乙酰氨基酚。这些信息目前分散在 ASPCA、Pet Poison Helpline、Plumb's、Merck Vet Manual 等英文来源里，中文世界缺少可核对的结构化版本。

本库做三件事：

1. **结构化** —— 每条记录字段固定，可机读、可搜索、可比对。
2. **可审核** —— 每条结论必须挂到权威来源条目上，AI 生成内容不作为证据。
3. **可追溯** —— 争议条目写明争议点，未核实的数据写「无可靠数值」而不是猜。

## 范围

**收录**（人工合成化合物）：

| 类别 | 举例 |
|---|---|
| 人用药物 | 米诺地尔、对乙酰氨基酚、布洛芬、SSRI、沙丁胺醇——不按给药途径细分 |
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
| `category` | 六类之一 |
| `cat_lethal_dose` | 有出处才填；否则一律 `无可靠数值` |
| `cat_toxicity_summary` | 一句话机制或症状 |
| `exposure_routes` | 误食 / 舔舐皮肤残留 / 吸入 / 经皮 |
| `physical_form` | 固体 / 半固体 / 液体 / 气体或气溶胶 |
| `form_risk` | 形态基线风险：固体=中，半固体=高，液体=高，气体=极高 |
| `toxicity_level` | **毒性**：极高 / 高 / 中（与形态无关） |
| `danger_level` | **合成风险** = max(form_risk, toxicity_level)，由脚本校验 |
| `commonness` | **常见程度**：常见 / 一般 / 少见（中国普通养猫家庭的出现概率） |
| `cat_lethal_dose_url` | 剂量数字的直接出处链接 |
| `cat_dose_note` | 定性危险剂量（无数字时的一句话描述） |
| `cat_dose_note_sources` | 定性描述的出处，可多条交叉比对 |
| `cat_dose_note_tier` | 专业 / 二手（二手仅作补充，不得单独支撑「有毒」结论） |
| `sources` | 对象列表：`library` / `title` / `url` / `accessed` / `quote`，至少一条，链接必须可点开 |
| `sources[].quote` | 支撑该结论的原文句子，`scripts/check_quotes.py` 会抓页面逐字比对 |
| `confirmation_status` | 已确认 / 有争议但已确认有毒 |
| `controversy` | 争议条目必填，说明分歧点 |
| `last_reviewed` | 最近人工核对来源的日期 |

完整定义与取值枚举见 [`data/schema.yml`](data/schema.yml)。

## 怎么读这三列

风险不是拍脑袋给一个总分，而是三层相加：

| 层 | 字段 | 判据 |
|---|---|---|
| 1. 能不能碰到 | `physical_form` → `form_risk` | 固体=中（要主动咬）；半固体=高（舔毛带进去）；液体=高（打翻、溅洒）；气体/气溶胶=极高（吸入，防不住） |
| 2. 碰到会怎样 | `toxicity_level` | 极高=少量致死；高=严重损伤或可致死；中=多为可逆的消化道/刺激症状 |
| 3. 家里有没有 | `commonness` | 常见=多数家庭有；一般=部分家庭有；少见=特定人群/职业 |

`danger_level` 由前三列计算，规则固定（`scripts/validate.py` 强制校验）：

- **极高** = 形态风险 ≥ 高（非固体）+ `commonness` 为常见或一般 + `toxicity_level` 为极高
- **中** = 固体 + 毒性中
- **其余一律为高**

也就是说：**固体永远不可能评「极高」**；只有「少见」、或毒性不是极高，才最多到「高」。

**实用读法**：

- 常见 × 极高 → 今天就翻抽屉（对乙酰氨基酚、除虫菊酯/百灭宁）
- 常见 × 高 → 顺手收进柜子（布洛芬、感冒药、滴露、84、樟脑丸）
- 一般 × 极高 → 有车、有病人、有种菜的家庭重点看（乙二醇、米诺地尔、聚乙醛）
- 少见 × 极高 → 认识即可（5-氟尿嘧啶、有机磷、ADHD 药物）

## 当前状态

- **主库 21 条**，覆盖上述全部类别
- **候审区 8 条**，均标注「待确认，默认避免」
- `无可靠数值` 的含义是「查过了，公开来源没有可引用的数字」，**不是「毒性低」**
- **3 条有经核实的剂量数字**（对乙酰氨基酚、乙二醇、聚乙醛），其余 18 条为「无可靠数值」
- 公开权威来源（Merck 专题页）大多只给犬剂量或定性描述；NCBI/Europe PMC 摘要里也几乎查不到猫的数值剂量（2026-10-24 扫过 18 个化合物，0 命中），因此不强行填满



## 让 AI 助手帮你查

[docs/agent-task.md](docs/agent-task.md) 是一份给 AI 助手的工作说明书：白名单来源、检索步骤、
逐字引文要求、YAML 输出格式。把这份说明书和自己的问题一起丢给能上网的助手（手机端也可以），
她会产出一条符合本库结构、且带可核对来源的条目。

对应的机器可读版本是 [docs/agent-task.json](docs/agent-task.json)。

## 网页速查表

`docs/index.html` 是单文件离线页面，双击即可打开，无网络依赖，可直接打印或存 PDF。

```bash
python scripts/build_site.py   # 改完 YAML 后重新生成
```

功能：搜索（中英文/别名）、按危险程度/常见程度/类别筛选、来源一键跳转、打印样式适配。

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

## 许可与引用

本仓库采用**分许可**：

| 范围 | 协议 | 说明 |
|---|---|---|
| 数据与文档（`data/`、`quarantine/`、`*.md`、生成的网页） | [CC BY-SA 4.0](LICENSE-DATA) | 署名 + 衍生作品同协议开源 |
| 代码（`scripts/`） | [MIT](LICENSE) | 随便用，保留版权声明即可 |

引用格式建议：

```
cat-synthetic-toxins（养猫家庭人工合成化合物毒性速查库）
https://github.com/Sakamonya/cat-synthetic-toxins
许可：CC BY-SA 4.0
```

商业使用、二次分发、改造都允许，但**必须署名并保持相同协议**。
条目中引用的第三方来源（ASPCA、Merck Vet Manual 等）版权归各自权利人。
