#!/usr/bin/env python3
"""
文档质量检查：术语一致性 + 中英页面对等。

在 CI 里作为质量门禁运行，任何一项不通过就让构建失败。
    python3 tools/check_terms.py

三项检查：
  1. 禁用译法    —— 正文里出现 terminology.yml 里禁止的写法
  2. 页面对等    —— 每个 xxx.md 都必须有对应的 xxx.en.md，反之亦然
  3. 术语表对等  —— 中英文术语表必须定义同一批英文术语

为什么值得做：多语言文档最容易失守的不是翻译质量，是同一个概念在不同页面
出现不同译法。人工评审发现不了这类问题——它分散在几十个文件里，每处单看
都没错。只有机器扫得动。
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
RULES = Path(__file__).resolve().parent / "terminology.yml"

# 检查正文时要跳过的部分：代码块、行内代码、以及术语表自身
# （术语表里必须能写出错误译法，否则没法说明「不要这么写」）
FENCE = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`\n]+`")
SKIP_FILES = {"glossary.md", "glossary.en.md"}


def strip_code(text: str) -> str:
    """把代码块和行内代码替换成等长空白，保持行号不变。"""
    text = FENCE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    text = INLINE.sub(lambda m: " " * len(m.group(0)), text)
    return text


def real_hits(line: str, wrong: str, unless: list) -> int:
    """
    统计 line 里 wrong 的「真实」出现次数。

    中文没有空格分词，直接用子串匹配会误伤：规则禁止「线程组」时，
    「线程组织方式」也会被判为违规。所以这里先找出所有 unless 词
    （合法地包含 wrong 的更长词）占据的字符区间，落在区间里的匹配
    一律不算。
    """
    shielded = []
    for phrase in unless:
        start = line.find(phrase)
        while start != -1:
            shielded.append((start, start + len(phrase)))
            start = line.find(phrase, start + 1)

    hits = 0
    pos = line.find(wrong)
    while pos != -1:
        end = pos + len(wrong)
        if not any(s <= pos and end <= e for s, e in shielded):
            hits += 1
        pos = line.find(wrong, pos + 1)
    return hits


def check_forbidden(rules) -> list:
    """检查一：正文中是否出现被禁用的写法。"""
    problems = []
    for md in sorted(DOCS.rglob("*.md")):
        if md.name in SKIP_FILES:
            continue
        prose = strip_code(md.read_text(encoding="utf-8"))
        for lineno, line in enumerate(prose.splitlines(), 1):
            for rule in rules["forbidden"]:
                unless = rule.get("unless", [])
                if real_hits(line, rule["wrong"], unless):
                    rel = md.relative_to(ROOT)
                    problems.append(
                        f"{rel}:{lineno}  出现「{rule['wrong']}」\n"
                        f"      应改用：{rule['use']}\n"
                        f"      原因：  {rule['why']}"
                    )
    return problems


def check_page_parity() -> list:
    """检查二：中英页面是否一一对应。"""
    problems = []
    zh = {p.relative_to(DOCS) for p in DOCS.rglob("*.md")
          if not p.name.endswith(".en.md")}
    en = {p.relative_to(DOCS) for p in DOCS.rglob("*.en.md")}

    for page in sorted(zh):
        want = page.with_suffix("").with_suffix(".en.md") \
            if page.suffixes else page
        want = page.parent / (page.stem + ".en.md")
        if want not in en:
            problems.append(f"docs/{page}  缺少对应的英文版 docs/{want}")

    for page in sorted(en):
        want = page.parent / (page.name[: -len(".en.md")] + ".md")
        if want not in zh:
            problems.append(f"docs/{page}  缺少对应的中文版 docs/{want}")
    return problems


def glossary_terms(path: Path) -> set:
    """从术语表的 Markdown 表格里抽出所有英文词条。"""
    terms = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        head = cells[0]
        # 跳过表头和分隔行
        if not head or head in {"English", "中文"} or set(head) <= set("-: "):
            continue
        # 去掉行内代码标记和括号补充说明，只留主词
        head = head.replace("`", "")
        head = re.sub(r"\s*\(.*?\)", "", head)
        terms.add(head.strip().lower())
    return terms


def check_glossary_parity() -> list:
    """检查三：中英术语表是否定义了同一批术语。"""
    zh_path, en_path = DOCS / "glossary.md", DOCS / "glossary.en.md"
    if not (zh_path.exists() and en_path.exists()):
        return ["术语表缺失：docs/glossary.md 或 docs/glossary.en.md 不存在"]

    zh, en = glossary_terms(zh_path), glossary_terms(en_path)
    problems = []
    for t in sorted(zh - en):
        problems.append(f"术语「{t}」只在中文术语表里有，英文术语表缺失")
    for t in sorted(en - zh):
        problems.append(f"术语「{t}」只在英文术语表里有，中文术语表缺失")
    return problems


def main() -> int:
    rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))

    checks = [
        ("禁用译法", check_forbidden(rules)),
        ("中英页面对等", check_page_parity()),
        ("中英术语表对等", check_glossary_parity()),
    ]

    total = 0
    print("=" * 62)
    print("文档术语一致性检查")
    print("=" * 62)

    for name, problems in checks:
        if problems:
            total += len(problems)
            print(f"\n✗ {name}：发现 {len(problems)} 个问题\n")
            for p in problems:
                print(f"   {p}")
        else:
            print(f"✓ {name}")

    print("\n" + "-" * 62)
    if total:
        print(f"共 {total} 个问题，检查未通过。")
        print(f"术语规范见 {RULES.relative_to(ROOT)}")
        return 1
    print(f"全部通过。已按 {len(rules['forbidden'])} 条术语规则扫描 "
          f"{len(list(DOCS.rglob('*.md')))} 个文档。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
