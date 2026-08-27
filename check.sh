#!/usr/bin/env bash
#
# 本地跑一遍 CI 里的全部质量门禁。
#
#   ./check.sh
#
# 这三项和 .github/workflows/deploy.yml 里跑的完全一样。
# 本地绿了再推，就不会出现「推上去才发现 CI 挂了」。

set -uo pipefail
cd "$(dirname "$0")"

PY=.venv/bin/python
MKDOCS=.venv/bin/mkdocs
fail=0

line() { printf '%s\n' "──────────────────────────────────────────────"; }

line
echo "① 示例脚本能否跑通"
line
if "$PY" examples/tiled_reduction.py > /dev/null 2>&1; then
  echo "   ✓ 通过"
else
  echo "   ✗ 失败 —— 完整输出："
  "$PY" examples/tiled_reduction.py
  fail=1
fi

echo
line
echo "② 术语一致性"
line
if "$PY" tools/check_terms.py; then
  :
else
  fail=1
fi

echo
line
echo "③ 死链与构建（--strict）"
line
if "$MKDOCS" build --strict > /tmp/mkdocs_build.log 2>&1; then
  echo "   ✓ 通过"
else
  echo "   ✗ 失败 —— 相关输出："
  grep -E "WARNING|ERROR" /tmp/mkdocs_build.log || cat /tmp/mkdocs_build.log
  fail=1
fi

echo
line
if [ "$fail" -eq 0 ]; then
  echo "全部通过 ✓  可以提交推送了。"
else
  echo "有检查未通过 ✗  修好再推，否则 CI 也会挂。"
fi
line
exit "$fail"
