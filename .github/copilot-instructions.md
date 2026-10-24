# 仓库约定

本仓库是毒性数据仓库。修改 `data/synthetic-compounds.yaml` 前必读 `AGENTS.md`。

- 字段定义以 `data/schema.yml` 为准，改数据前先看 schema
- 提交前运行 `python scripts/validate.py`，必须 0 错误
- 修改数据后运行 `python scripts/build_site.py` 重建网页
- 不得提交密钥；不得把犬或人的剂量写成猫的
- 每条来源必须有可打开的 URL
