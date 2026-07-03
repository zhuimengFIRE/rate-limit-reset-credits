#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${CODEX_HOME:-$HOME/.codex}/skills/rate-limit-reset-credits"

mkdir -p "$(dirname "$TARGET_DIR")"
rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"

copy_item() {
  local item="$1"
  if [ -e "$SOURCE_DIR/$item" ]; then
    cp -R "$SOURCE_DIR/$item" "$TARGET_DIR/$item"
  fi
}

copy_item "SKILL.md"
copy_item "README.md"
copy_item "agents"
copy_item "scripts"

chmod +x "$TARGET_DIR/scripts/check_rate_limit_reset_credits.py" 2>/dev/null || true

printf '已安装到：%s\n' "$TARGET_DIR"
printf '在 Codex 中输入“重置次数查询”即可使用。\n'
