#!/usr/bin/env python3
"""使用本机 Codex 凭证安全查询重置次数。"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


AUTH_PATH = Path.home() / ".codex" / "auth.json"
ENDPOINT = "https://chatgpt.com/backend-api/wham/rate-limit-reset-credits"
STATUS_LABELS = {
    "available": "可用",
    "used": "已使用",
    "expired": "已过期",
    "unavailable": "不可用",
}
EMPTY = "无"


def load_access_token() -> str:
    try:
        payload = json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError("未找到 ~/.codex/auth.json。") from None
    except json.JSONDecodeError:
        raise RuntimeError("~/.codex/auth.json 不是有效 JSON。") from None

    token = payload.get("tokens", {}).get("access_token")
    if not isinstance(token, str) or not token.strip():
        raise RuntimeError("未找到 ~/.codex/auth.json 中的 tokens.access_token。")
    return token.strip()


def fetch_reset_credits(access_token: str) -> Any:
    request = urllib.request.Request(
        ENDPOINT,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "Codex reset credits checker",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            raise RuntimeError(
                "HTTP 401：凭证失效，或请求没有携带有效的 Authorization header。"
            ) from None
        raise RuntimeError(f"HTTP {exc.code}：接口请求失败。") from None
    except urllib.error.URLError as exc:
        raise RuntimeError(f"网络请求失败：{exc.reason}") from None

    try:
        return json.loads(body)
    except json.JSONDecodeError:
        raise RuntimeError("接口返回内容不是有效 JSON。") from None


def find_first_key(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            found = find_first_key(child, key)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_first_key(child, key)
            if found is not None:
                return found
    return None


def looks_like_credit(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    return bool({"status", "granted_at", "expires_at"} & item.keys())


def find_credits(value: Any) -> list[dict[str, Any]]:
    preferred_keys = (
        "credits",
        "reset_credits",
        "rate_limit_reset_credits",
        "items",
        "data",
    )
    if isinstance(value, dict):
        for key in preferred_keys:
            child = value.get(key)
            if isinstance(child, list) and any(looks_like_credit(item) for item in child):
                return [item for item in child if looks_like_credit(item)]
        for child in value.values():
            found = find_credits(child)
            if found:
                return found
    elif isinstance(value, list):
        if any(looks_like_credit(item) for item in value):
            return [item for item in value if looks_like_credit(item)]
        for child in value:
            found = find_credits(child)
            if found:
                return found
    return []


def to_local_time(value: Any) -> str | None:
    if value is None:
        return None

    parsed: datetime | None = None
    if isinstance(value, (int, float)):
        timestamp = float(value)
        if timestamp > 10_000_000_000:
            timestamp = timestamp / 1000
        parsed = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    elif isinstance(value, str) and value.strip():
        raw = value.strip()
        if raw.isdigit():
            timestamp = float(raw)
            if timestamp > 10_000_000_000:
                timestamp = timestamp / 1000
            parsed = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        else:
            normalized = raw.replace("Z", "+00:00")
            try:
                parsed = datetime.fromisoformat(normalized)
            except ValueError:
                return raw
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

    if parsed is None:
        return str(value)

    local = parsed.astimezone()
    return local.strftime("%Y-%m-%d %H:%M:%S %Z%z")


def localize_status(value: Any) -> str:
    if value is None:
        return EMPTY
    raw = str(value)
    return STATUS_LABELS.get(raw, raw)


def markdown_cell(value: Any) -> str:
    raw = EMPTY if value is None else str(value)
    return raw.replace("|", "\\|").replace("\r\n", "<br>").replace("\n", "<br>")


def print_summary(data: Any) -> None:
    available_count = find_first_key(data, "available_count")
    credits = find_credits(data)

    count = available_count if available_count is not None else EMPTY
    print(f"可用重置次数：{count}")
    print()
    print("重置次数明细：")
    print()
    print("| 序号 | 状态 | 发放时间 | 到期时间 |")
    print("| --- | --- | --- | --- |")
    if not credits:
        print(f"| 1 | {EMPTY} | {EMPTY} | {EMPTY} |")
        return

    for index, credit in enumerate(credits, start=1):
        status = markdown_cell(localize_status(credit.get("status")))
        granted_at = markdown_cell(to_local_time(credit.get("granted_at")) or EMPTY)
        expires_at = markdown_cell(to_local_time(credit.get("expires_at")) or EMPTY)
        print(f"| {index} | {status} | {granted_at} | {expires_at} |")


def main() -> int:
    try:
        access_token = load_access_token()
        data = fetch_reset_credits(access_token)
        print_summary(data)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
