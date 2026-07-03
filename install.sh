#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills/rate-limit-reset-credits"
TARGET_PARENT="$(dirname "$TARGET_DIR")"

mkdir -p "$TARGET_PARENT"

if [ "$SOURCE_DIR" = "$TARGET_DIR" ]; then
  chmod +x "$TARGET_DIR/scripts/check_rate_limit_reset_credits.py" 2>/dev/null || true
  printf '已安装到：%s\n' "$TARGET_DIR"
  printf '在 Codex 中输入“重置次数查询”即可使用。\n'
  exit 0
fi

TMP_DIR="$(mktemp -d "$TARGET_PARENT/.rate-limit-reset-credits.XXXXXX")"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

copy_item() {
  local item="$1"
  if [ -e "$SOURCE_DIR/$item" ]; then
    cp -R "$SOURCE_DIR/$item" "$TMP_DIR/$item"
  fi
}

copy_item "SKILL.md"
copy_item "README.md"
copy_item "agents"
copy_item "scripts"

rm -rf "$TARGET_DIR"
mv "$TMP_DIR" "$TARGET_DIR"
trap - EXIT

chmod +x "$TARGET_DIR/scripts/check_rate_limit_reset_credits.py" 2>/dev/null || true

printf '已安装到：%s\n' "$TARGET_DIR"
printf '在 Codex 中输入“重置次数查询”即可使用。\n'
