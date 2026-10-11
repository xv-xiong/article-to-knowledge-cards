#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make-knowledge-cards 仓库一致性校验（纯标准库，无第三方依赖）。

把"能机器判定的"从人工检查里拿出来，人只保留机器判不了的部分。
校验项：

   1  编码 / 行尾        所有文件（含未跟踪但未被忽略的）为 UTF-8 无 BOM、LF 行尾
   2  frontmatter 白名单 SKILL.md 只允许 name / description / license
   3  name 格式与目录一致
   4  description       长度 <= 1024，且不含尖括号 < >
   5  规则条数一致       SKILL.md 的 Extraction Rules <-> README 第 2 节（含中文数字）
   6  两处内嵌示例逐字一致
   7  示例首行声明的张数 = 实际卡片数
   8  README 第 5 节表格张数与示例一致
   9  README 第 6 节目录树与真实文件一致
  10  兼容表每行都有出处（链接 / 实测 / 非官方来源 标注）
  11  自测问题不得使用被禁的个人体验 / 偏好句式
  12  AUDIT.md 锚点：依据片段须逐字出现在对应输入中，且行数 = 卡片数
  13  每张卡片四字段齐全且顺序正确
  14  文本形态条数一致   README「适配 N 类常见文本形态」标题 / 表格行数 / SKILL.md 条目
  15  能力边界条数一致   README 第 2 节的 ✗ 列表 <-> SKILL.md 的 Unsupported
  16  反面示例例数一致   README 第 8 节「下面 N 例」<-> 实际 ❌ 条目数
  17  校验项条数声明一致 本清单 / README「它覆盖：…」/ CHANGELOG「把 N 项」<-> 实际校验项数

用法：python tools/check_skill.py     退出码 0 = 全部通过，1 = 存在失败项
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SKILL = "skills/make-knowledge-cards/SKILL.md"
README = "README.md"
EX = "examples/make-knowledge-cards"
INPUTS = EX + "/inputs"
OUTPUTS = EX + "/outputs"
AUDIT = EX + "/AUDIT.md"

CN_NUM = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五",
          6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}

# 自测问题里禁止出现的句式（纯个人体验 / 偏好 / 复述）
BANNED_SELFTEST = [
    "你有没有", "你会不会", "你会选", "你会怎么做", "你更倾向",
    "你自己的话", "你平时", "你拖延", "结合你自己",
]


_results = []  # (ok: bool, title: str, details: list[str])


def report(ok, title, details=None):
    _results.append((bool(ok), title, list(details or [])))


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def write(rel, text):
    with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def tracked():
    """已跟踪 + 未跟踪但未被 .gitignore 忽略的文件（相对仓库根的 POSIX 路径）。"""
    try:
        out = subprocess.check_output(
            ["git", "-C", ROOT, "ls-files", "--cached", "--others", "--exclude-standard"],
            text=True,
        )
        return sorted({ln.strip() for ln in out.splitlines() if ln.strip()})
    except Exception:
        files = []
        for dp, dns, fns in os.walk(ROOT):
            dns[:] = [d for d in dns if d not in (".git",)]
            for fn in fns:
                files.append(os.path.relpath(os.path.join(dp, fn), ROOT).replace("\\", "/"))
        return sorted(files)


def normalize(s):
    return re.sub(r"\s+", "", s)


def card_count(text):
    return len(re.findall(r"^\*\*卡片 \d+\*\*\s*$", text, flags=re.M))


def section(text, start, end_prefix):
    i = text.index(start)
    j = text.find(end_prefix, i + len(start))
    return text[i: j if j != -1 else len(text)]


def example_pairs():
    pairs = []
    base = os.path.join(ROOT, INPUTS)
    if not os.path.isdir(base):
        return pairs
    for fn in sorted(os.listdir(base)):
        stem = os.path.splitext(fn)[0]
        out = "%s/%s.cards.md" % (OUTPUTS, stem)
        if os.path.exists(os.path.join(ROOT, out)):
            pairs.append(("%s/%s" % (INPUTS, fn), out))
    return pairs


# --------------------------------------------------------------------------
# 1. 编码 / 行尾
# --------------------------------------------------------------------------
def check_encoding():
    bad = []
    for f in tracked():
        try:
            data = open(os.path.join(ROOT, f), "rb").read()
        except OSError as exc:
            bad.append("%s: 无法读取 (%s)" % (f, exc))
            continue
        flags = []
        if data.startswith(b"\xef\xbb\xbf"):
            flags.append("BOM")
        if b"\r" in data:
            flags.append("CRLF/CR")
        if flags:
            bad.append("%s: %s" % (f, ", ".join(flags)))
    report(not bad, "1. 编码 / 行尾（UTF-8 无 BOM，LF）",
           bad or ["%d 个文件全部合规" % len(tracked())])


# --------------------------------------------------------------------------
# 2. frontmatter 白名单
# --------------------------------------------------------------------------
def skill_frontmatter():
    text = read(SKILL)
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return None, text
    fm = m.group(1)
    keys = re.findall(r"^([A-Za-z0-9_\-]+)\s*:", fm, re.M)
    return keys, text


def check_frontmatter():
    keys, _ = skill_frontmatter()
    if keys is None:
        report(False, "2. frontmatter 白名单", ["SKILL.md 缺少合法的 YAML frontmatter"])
        return
    allowed = {"name", "description", "license"}
    extra = [k for k in keys if k not in allowed]
    report(not extra, "2. frontmatter 白名单（仅 name / description / license）",
           (["出现规范外字段：%s" % ", ".join(extra)] if extra else ["字段：%s" % ", ".join(keys)]))


# --------------------------------------------------------------------------
# 3. name 格式与目录一致
# --------------------------------------------------------------------------
def check_name():
    keys, text = skill_frontmatter()
    details, ok = [], True
    if keys is None:
        report(False, "3. name 格式与目录一致", ["无 frontmatter"])
        return
    m = re.search(r"^name:\s*(\S+)\s*$", text, re.M)
    if not m:
        report(False, "3. name 格式与目录一致", ["frontmatter 缺少 name"])
        return
    name = m.group(1)
    dirname = os.path.basename(os.path.dirname(SKILL))
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        ok = False
        details.append("name「%s」不是 kebab-case" % name)
    if name != dirname:
        ok = False
        details.append("name「%s」与目录名「%s」不一致" % (name, dirname))
    report(ok, "3. name 格式与目录一致", details or ["name = %s，与目录名一致" % name])


# --------------------------------------------------------------------------
# 4. description
# --------------------------------------------------------------------------
def check_description():
    keys, text = skill_frontmatter()
    if keys is None:
        report(False, "4. description 长度与字符", ["无 frontmatter"])
        return
    m = re.search(r"^description:\s*(.+?)\s*$", text, re.M)
    if not m:
        report(False, "4. description 长度与字符", ["frontmatter 缺少 description"])
        return
    desc = m.group(1)
    details, ok = ["长度 %d 字符" % len(desc)], True
    if len(desc) > 1024:
        ok = False
        details.append("超过 1024 字符上限")
    if "<" in desc or ">" in desc:
        ok = False
        details.append("含尖括号 < 或 >")
    report(ok, "4. description 长度 <= 1024 且无尖括号", details)


# --------------------------------------------------------------------------
# 5. 规则条数一致
# --------------------------------------------------------------------------
def check_rule_count():
    sk = read(SKILL)
    rd = read(README)
    sk_sec = section(sk, "## Extraction Rules", "\n## ")
    sk_n = len(re.findall(r"^\d+\.\s+\*\*", sk_sec, re.M))

    m = re.search(r"\*\*([一二三四五六七八九十]+)条硬性抽取规则\*\*", rd)
    if not m:
        report(False, "5. 规则条数一致", ["README 第 2 节找不到「N条硬性抽取规则」标题"])
        return
    cn = m.group(1)
    rd_sec = section(rd, m.group(0), "**另有一项配套约定**")
    rd_n = len(re.findall(r"^\d+\.\s+", rd_sec, re.M))

    details, ok = ["SKILL.md = %d 条，README = %d 条" % (sk_n, rd_n)], True
    if sk_n != rd_n:
        ok = False
        details.append("两处条数不一致")
    expect_cn = CN_NUM.get(sk_n)
    if expect_cn and cn != expect_cn:
        ok = False
        details.append("README 标题写「%s条」，应为「%s条」" % (cn, expect_cn))
    report(ok, "5. 规则条数一致（SKILL.md <-> README 第 2 节）", details)


# --------------------------------------------------------------------------
# 6. 两处内嵌示例逐字一致
# --------------------------------------------------------------------------
def extract_skill_example(sk):
    sec = section(sk, "## Output Example", "\n## ")
    m = re.search(r"应输出：\s*(.*)$", sec, re.S)
    return normalize(m.group(1)) if m else None


def extract_readme_example(rd):
    m = re.search(r"### 输出\s*\n+```markdown\s*\n(.*?)```", rd, re.S)
    return normalize(m.group(1)) if m else None


def check_inline_example():
    a = extract_skill_example(read(SKILL))
    b = extract_readme_example(read(README))
    if a is None or b is None:
        report(False, "6. 两处内嵌示例逐字一致", ["无法提取示例（SKILL.md 或 README）"])
        return
    if a == b:
        report(True, "6. 两处内嵌示例逐字一致", ["%d 字符，完全一致" % len(a)])
        return
    i = next((k for k, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    report(False, "6. 两处内嵌示例逐字一致",
           ["首个差异 @%d" % i,
            "SKILL.md: ...%s..." % a[max(0, i - 30):i + 30],
            "README  : ...%s..." % b[max(0, i - 30):i + 30],
            "长度 SKILL=%d README=%d" % (len(a), len(b))])


# --------------------------------------------------------------------------
# 7. 示例首行声明张数 = 实际卡片数
# --------------------------------------------------------------------------
def declared_count(text):
    m = re.search(r"^共\s*(\d+)\s*张", text, re.M)
    return int(m.group(1)) if m else 0


def check_declared_counts():
    bad, rows = [], []
    for _inp, out in example_pairs():
        text = read(out)
        decl, act = declared_count(text), card_count(text)
        rows.append("%s: 声明 %d / 实际 %d" % (os.path.basename(out), decl, act))
        if decl != act:
            bad.append("%s: 声明 %d 张，实际 %d 张" % (out, decl, act))
    report(not bad, "7. 示例首行声明的张数 = 实际卡片数", bad or rows)


# --------------------------------------------------------------------------
# 8. README 第 5 节表格张数与示例一致
# --------------------------------------------------------------------------
def check_readme_table():
    rd = read(README)
    try:
        sec = section(rd, "### 更多测试用例", "\n## ")
    except ValueError:
        report(False, "8. README 第 5 节表格张数", ["找不到「更多测试用例」小节"])
        return
    bad, rows = [], []
    for line in sec.splitlines():
        if not line.strip().startswith("|"):
            continue
        m = re.search(r"outputs/([a-z_]+)\.cards\.md", line)
        if not m:
            continue
        name = m.group(1)
        nums = re.findall(r"(\d+)\s*张", line)
        if not nums:
            bad.append("%s 行内未声明张数" % name)
            continue
        decl = int(nums[-1])
        out = "%s/%s.cards.md" % (OUTPUTS, name)
        act = card_count(read(out))
        rows.append("%s: 表格声明 %d / 实际 %d" % (name, decl, act))
        if decl != act:
            bad.append("%s: 表格声明 %d 张，实际 %d 张" % (name, decl, act))
    report(not bad, "8. README 第 5 节表格张数与示例一致", bad or rows)


# --------------------------------------------------------------------------
# 9. README 第 6 节目录树
# --------------------------------------------------------------------------
def check_tree():
    rd = read(README)
    try:
        sec = section(rd, "## 6. 目录结构", "\n## ")
    except ValueError:
        report(False, "9. README 第 6 节目录树", ["找不到「目录结构」小节"])
        return
    files = tracked()
    basenames = {os.path.basename(f) for f in files}
    details, ok = [], True

    required = ["README.md", "CHANGELOG.md", "CONTRIBUTING.md", "LICENSE",
                ".gitignore", ".gitattributes", ".github", "skills", "examples", "tools"]
    for token in required:
        if token not in sec:
            ok = False
            details.append("目录树缺少顶层条目：%s" % token)

    for ghost in ("openai.yaml", "agents"):
        if ghost in sec:
            ok = False
            details.append("目录树出现已删除的条目：%s" % ghost)

    for token in re.findall(r"[A-Za-z0-9_.\-]+\.(?:md|py|ya?ml|txt)", sec):
        if token not in basenames:
            ok = False
            details.append("目录树引用了不存在的文件：%s" % token)

    report(ok, "9. README 第 6 节目录树与真实文件一致", details or ["顶层条目与文件名全部吻合"])


# --------------------------------------------------------------------------
# 10. 兼容表每行都有出处
# --------------------------------------------------------------------------
def check_compat_table():
    lines = read(README).splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.strip().startswith("| 运行时 |")), None)
    if start is None:
        report(False, "10. 兼容表每行都有出处", ["找不到以「| 运行时 |」开头的表头"])
        return
    details, ok = [], True
    for row in lines[start + 2:]:
        if not row.strip().startswith("|"):
            break
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cells) < 4:
            ok = False
            details.append("列数不足（应为 运行时/技能目录/出处/实测）：%s" % row.strip())
            continue
        runtime, src, tested = cells[0], cells[2], cells[3]
        has_src = ("http" in src) or ("非官方" in src) or ("实测" in tested)
        if not has_src:
            ok = False
            details.append("%s：出处栏既无链接、也无「实测 / 非官方」标注" % runtime)
    report(ok, "10. 兼容表每行都有出处（链接 / 实测 / 非官方）", details or ["所有行均满足出处要求"])


# --------------------------------------------------------------------------
# 11. 自测问题禁用句式
# --------------------------------------------------------------------------
def selftest_lines(text):
    return [ln.strip() for ln in text.splitlines()
            if ln.strip().startswith("- 例子或自测问题：自测")]


def check_selftest_phrases():
    bad, total = [], 0
    targets = [o for _i, o in example_pairs()] + [SKILL, README]
    for rel in targets:
        for line in selftest_lines(read(rel)):
            total += 1
            for phrase in BANNED_SELFTEST:
                if phrase in line:
                    bad.append("%s: 命中「%s」-> %s" % (rel, phrase, line[:80]))
    report(not bad, "11. 自测问题禁用句式", bad or ["检查 %d 条自测问题，无禁用句式" % total])


# --------------------------------------------------------------------------
# 12. AUDIT.md 锚点
# --------------------------------------------------------------------------
def parse_audit():
    """返回 {输入文件名: [(卡片号, 依据片段), ...]}"""
    if not os.path.exists(os.path.join(ROOT, AUDIT)):
        return None
    tables, cur = {}, None
    for line in read(AUDIT).splitlines():
        m = re.match(r"^##\s+(\S+)\s*$", line)
        if m:
            cur = m.group(1)
            tables[cur] = []
            continue
        if cur is None or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or set(cells[0]) <= set("-: ") or cells[0] == "卡片":
            continue
        frag = cells[2].strip()
        tables[cur].append((cells[0], frag))
    return tables


def check_audit():
    tables = parse_audit()
    if tables is None:
        report(False, "12. AUDIT.md 锚点", ["缺少 %s" % AUDIT])
        return
    bad, rows = [], 0
    for input_name, entries in tables.items():
        in_path = "%s/%s" % (INPUTS, input_name)
        if not os.path.exists(os.path.join(ROOT, in_path)):
            bad.append("AUDIT 引用了不存在的输入：%s" % input_name)
            continue
        src = read(in_path)
        stem = os.path.splitext(input_name)[0]
        out_path = "%s/%s.cards.md" % (OUTPUTS, stem)
        act = card_count(read(out_path)) if os.path.exists(os.path.join(ROOT, out_path)) else -1
        if act != len(entries):
            bad.append("%s：AUDIT %d 行，输出 %d 张卡片，数量不符" % (input_name, len(entries), act))
        for idx, frag in entries:
            rows += 1
            for part in frag.split("‖"):
                part = part.strip().strip("`").strip()
                if part in ("", "—", "-"):
                    continue
                if part not in src:
                    bad.append("%s 卡片 %s：依据片段未逐字出现在输入中 -> 「%s」" % (input_name, idx, part[:50]))
    report(not bad, "12. AUDIT.md 锚点（依据片段须逐字出现在输入中）",
           bad or ["%d 条锚点全部逐字命中" % rows])


# --------------------------------------------------------------------------
# 13. 卡片四字段齐全且顺序正确
# --------------------------------------------------------------------------
def check_card_schema():
    order = ["- 标题：", "- 核心知识：", "- 简明解释：", "- 例子或自测问题："]
    bad, checked = [], 0
    for _inp, out in example_pairs():
        blocks = re.split(r"^\*\*卡片 \d+\*\*\s*$", read(out), flags=re.M)[1:]
        for n, block in enumerate(blocks, 1):
            checked += 1
            pos = [block.find(k) for k in order]
            if any(p < 0 for p in pos):
                bad.append("%s 卡片 %d：缺字段" % (out, n))
            elif pos != sorted(pos):
                bad.append("%s 卡片 %d：字段顺序错误" % (out, n))
    report(not bad, "13. 每张卡片四字段齐全且顺序正确",
           bad or ["检查 %d 张卡片，字段齐全、顺序正确" % checked])


def check_text_shapes():
    rd, sk = read(README), read(SKILL)
    m = re.search(r"\*\*适配\s*(\d+)\s*类常见文本形态\*\*", rd)
    if not m:
        report(False, "14. 文本形态条数一致", ["README 找不到「适配 N 类常见文本形态」"])
        return
    n_title = int(m.group(1))
    rows, started = 0, False
    for ln in rd[m.end():].splitlines():
        s = ln.strip()
        if s.startswith("|"):
            started = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            if set("".join(cells)) <= set("-: ") or cells[0] == "文本形态":
                continue
            rows += 1
        elif started:
            break
    n_skill = len(re.findall(r"^- ", section(sk, "## Input Shape Notes", "\n## "), re.M))
    report(n_title == rows == n_skill, "14. 文本形态条数一致（README 标题 / 表格 / SKILL.md）",
           ["README 标题 %d，表格 %d 行，SKILL.md %d 条" % (n_title, rows, n_skill)])


def check_boundaries():
    rd, sk = read(README), read(SKILL)
    i = rd.index("**明确的能力边界**")
    seg = rd[i:rd.index("## 3. 安装方法", i)]
    n_readme = len(re.findall(r"^- ✗ ", seg, re.M))
    n_skill = len(re.findall(r"^- ", section(sk, "## Unsupported", "\n## "), re.M))
    report(n_readme == n_skill, "15. 能力边界条数一致（README / SKILL.md）",
           ["README %d 条，SKILL.md %d 条" % (n_readme, n_skill)])


def check_anti_examples():
    sec = section(read(README), "## 8. 反面示例", "\n## ")
    m = re.search(r"下面([一二三四五六七八九十]+)例", sec)
    if not m:
        report(False, "16. 反面示例例数一致", ["第 8 节找不到「下面 N 例」"])
        return
    cn = m.group(1)
    n_text = {v: k for k, v in CN_NUM.items()}.get(cn)
    n_actual = len(re.findall(r"^\*\*❌", sec, re.M))
    report(n_text == n_actual, "16. 反面示例例数一致（README 第 8 节）",
           ["标题写「%s例」，实际 %d 条 ❌" % (cn, n_actual)])


def check_self_description():
    """校验项总数与三处声明一致：本文件清单 / README 覆盖列表 / CHANGELOG。"""
    actual = len(CHECKS)
    bad = []

    doc = __doc__ or ""
    n_doc = len(re.findall(r"^\s*(\d+)\s{2,}\S", doc, re.M))
    if n_doc != actual:
        bad.append("脚本自身清单列了 %d 项，实际注册 %d 项" % (n_doc, actual))

    rd = read(README)
    m = re.search(r"它覆盖：(.+?)。", rd, re.S)
    if not m:
        bad.append("README 找不到「它覆盖：……」覆盖列表")
    else:
        items = [x.strip() for x in m.group(1).replace("\n", "").split("、") if x.strip()]
        if len(items) != actual:
            bad.append("README 覆盖列表写了 %d 项，实际 %d 项" % (len(items), actual))

    cl = read("CHANGELOG.md")
    m = re.search(r"把\s*(\d+)\s*项可机器判定的约定", cl)
    if not m:
        bad.append("CHANGELOG 找不到「把 N 项可机器判定的约定」")
    elif int(m.group(1)) != actual:
        bad.append("CHANGELOG 写「%s 项」，实际 %d 项" % (m.group(1), actual))

    report(not bad, "17. 校验项条数声明三处一致（脚本清单 / README / CHANGELOG）",
           bad or ["三处均为 %d 项" % actual])


CHECKS = (check_encoding, check_frontmatter, check_name, check_description,
          check_rule_count, check_inline_example, check_declared_counts,
          check_readme_table, check_tree, check_compat_table,
          check_selftest_phrases, check_audit, check_card_schema,
          check_text_shapes, check_boundaries, check_anti_examples,
          check_self_description)


def main():
    for fn in CHECKS:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            report(False, fn.__name__, ["检查过程抛出异常：%r" % exc])

    failed = sum(1 for ok, _t, _d in _results if not ok)
    print("=" * 72)
    print("make-knowledge-cards 一致性校验")
    print("=" * 72)
    for ok, title, details in _results:
        print("\n%s %s" % ("PASS" if ok else "FAIL", title))
        for d in details:
            print("      %s %s" % ("·" if ok else "!", d))
    print("\n" + "-" * 72)
    print("结果：%d 项通过，%d 项失败" % (len(_results) - failed, failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
