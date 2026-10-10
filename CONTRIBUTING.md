# 贡献指南

感谢你改进 `make-knowledge-cards`。本项目刻意保持轻量：**技能本体只有 `SKILL.md` 与 `agents/openai.yaml` 两个文件，不含脚本、不引入任何依赖**。请勿为功能改进引入脚本或第三方库。

## 修改抽取规则时必须同步两份文件

抽取规则同时存在于两处，**必须一起改**，否则会出现规则漂移：

- `skills/make-knowledge-cards/SKILL.md` —— 完整规则（含"常见输入形态"等适配）
- `skills/make-knowledge-cards/agents/openai.yaml` —— 精简版（字段与硬规则一致）

## 改完规则后回查示例

`examples/make-knowledge-cards/outputs/` 下的 5 组输出是规则的"活样本"，改完规则要逐组复查：

- 是否符合「一卡一点 / 去重 / 不编造 / 不凑数」；
- **每条自测问题是否都能由对应输入的原文支撑** —— 不得询问原文未解释的原因、未给出的后果，或纯个人体验 / 偏好；
- 文件开头声明的张数是否与实际卡片块数一致（README 的示例表格也要同步）。

## 提交前自检

- [ ] `SKILL.md` 与 `agents/openai.yaml` 的规则描述一致
- [ ] 示例输出符合四条硬约束，自测问题均可由原文支撑
- [ ] 未新增脚本或第三方依赖
- [ ] 全仓库 UTF-8 无 BOM、LF 行尾

## 提交信息

使用 Conventional Commits 前缀：`docs:`、`feat:`、`fix:`、`chore:`。

示例：`docs: tighten self-test question rule`
