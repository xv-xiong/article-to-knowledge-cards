# Changelog

本文件记录本项目所有值得使用者注意的变更。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [0.2.0] - 2026-10-11

### 新增

- 新增本文件，回溯记录 0.1.0 与 0.1.1 的变更。
- 新增 `CONTRIBUTING.md` 与 `.github/` 下的 Issue / PR 模板。
- 新增两项配套约定：**用户指令优先**（用户指定张数 / 字段时以用户为准）、**重要性判定准则**（减少取舍与排序的主观漂移）。
- 新增边缘情况处理：超长文本分块归并、结构化输入（表格 / 代码 / CSV）明确不适用、中英混排的语言策略。

### 变更

- 收紧「自测问题」规则：明确问题必须能由源文本支撑，禁止询问原文未解释的原因、未给出的后果，以及纯个人体验 / 偏好（`SKILL.md`、`agents/openai.yaml`）。
- 修正 8 处不符合该规则的自测问题：`listicle.cards.md` 卡 5 / 卡 7 / 卡 8、`essay.cards.md` 卡 2 / 卡 3、`short.cards.md` 卡 1 / 卡 2、`technical.cards.md` 卡 1（同时修正卡 1 自测题与所属卡片错位的问题）。
- `agents/openai.yaml`：删除未经验证的 `Agent(**cfg['agent'])` 写法，改为按目标框架的 schema 加载；补齐与 `SKILL.md` 一致的硬规则与语言规则。
- `README.md`：同步上述规则与能力边界；统一示例表格路径；补充仓库名与技能名的说明。

## [0.1.1] - 2026-10-10

### 文档

- 明确本技能遵循 Agent Skills 开放规范，**不限于 WorkBuddy**；列出可原生加载同一份目录的运行时（Claude Code / Codex CLI / DeepSeek Harness / GitHub Copilot / Cursor / Gemini CLI 等）。
- 修正一处误导表述：跨平台能力来自 `SKILL.md` 本身，`agents/openai.yaml` 只是**可选**的显式接入方式。
- 新增「方式二：作为其他兼容 Agent 的技能」安装说明，含各运行时技能目录对照表。
- `SKILL.md` 去掉运行时专有工具名（"Read 工具" → "当前运行时提供的文件读取工具"）。

### 说明

- 技能行为无变化：抽取规则、卡片结构、5 组示例（7 / 5 / 3 / 8 / 0 张）与 0.1.0 完全一致。

## [0.1.0] - 2026-10-10

### 新增

- 首个版本：把粘贴的文章或本地 Markdown / TXT 文件转换为 5~8 张知识卡片。
- 固定四字段卡片结构：标题 / 核心知识 / 简明解释 / 例子或自测问题。
- 六条硬性抽取规则：只取重要知识、一卡一点、去重、不编造、不凑数、语言一致。
- 5 类文本形态的适配规则（技术文 / 论述文 / 清单文 / 极短文 / 带外链广告文）。
- OpenAI 兼容智能体定义 `agents/openai.yaml`（可选，非使用前提）。
- 5 组真实输入输出示例、MIT 许可证。

[Unreleased]: https://github.com/xv-xiong/article-to-knowledge-cards/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/xv-xiong/article-to-knowledge-cards/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/xv-xiong/article-to-knowledge-cards/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/xv-xiong/article-to-knowledge-cards/releases/tag/v0.1.0
