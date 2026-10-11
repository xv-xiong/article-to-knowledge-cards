# 贡献指南

感谢你改进 `make-knowledge-cards`。本项目刻意保持轻量：**技能本体只有一份 `SKILL.md`，不含脚本、不引入任何依赖**。请勿为**技能功能**引入脚本或第三方库。

`tools/check_skill.py` 与 `.github/workflows/ci.yml` 是**仓库维护设施**（不属于技能本体）——它们的存在意义正是替代人工逐项核对，扩展它们是被鼓励的。

## 先跑一遍校验

```bash
python tools/check_skill.py
```

CI 会在每次 push / PR 时自动跑同一条命令。它**纯标准库**，无需安装任何依赖。

## 修改抽取规则时必须同步多处副本

抽取规则**唯一源头是 `skills/make-knowledge-cards/SKILL.md`**，但仓库里还有几处副本，**必须一起改**，否则会出现规则漂移：

- `README.md` —— 第 2 节复述硬规则，第 5 节内嵌一份完整示例；
- `examples/make-knowledge-cards/outputs/` —— 11 组输出的"活样本"；
- `examples/make-knowledge-cards/AUDIT.md` —— 示例断言的锚点表；
- `CONTRIBUTING.md` 本文件与 `.github/pull_request_template.md` —— 自检清单。

历史教训：v0.2.0 收紧「自测问题」规则时只回查了 `examples/`，漏掉 `SKILL.md` 与 `README.md` 的内嵌示例，导致旗舰示例里仍留着"原文未给出的后果"式提问和一个原文没有的类比。

## 改完规则后回查示例与锚点

- 是否符合「一卡一点 / 去重 / 不编造 / 不凑数」；
- **每条自测问题是否都能由对应输入的原文支撑** —— 不得询问原文未解释的原因、未给出的后果，或纯个人体验 / 偏好；
- 文件开头声明的张数是否与实际卡片块数一致（README 的示例表格也要同步）；
- `AUDIT.md` 中对应卡片的依据片段是否仍然**逐字**出现在输入里——**改过任何一张卡的断言，就重写它的依据**。

## 硬约定：每个缺陷都要追问一次"能否变成一条断言"

修好一个缺陷后，请追问：**"它能不能变成 `tools/check_skill.py` 里的一条检查？"**

- **能** → 加进去，并在 PR 里说明新增了哪条检查；
- **不能**（属语义判断）→ 写进 `README.md` 第 9 节的"人工只该看这些"。

规则靠人记会漂移，断言不会。本仓库已经因为"靠人记住改四处"栽过两次跟头。

## 提交前自检

- [ ] `python tools/check_skill.py` 通过
- [ ] `SKILL.md`、`README.md`、`examples/`、`AUDIT.md` 的规则描述与示例内容一致
- [ ] 示例输出符合硬约束，自测问题均可由原文支撑，且锚点已同步
- [ ] 未为技能功能新增脚本或第三方依赖
- [ ] 全仓库 UTF-8 无 BOM、LF 行尾

## 提交信息

使用 Conventional Commits 前缀：`docs:`、`feat:`、`fix:`、`chore:`。

示例：`docs: tighten self-test question rule`
