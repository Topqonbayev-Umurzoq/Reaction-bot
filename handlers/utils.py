import re
from datetime import datetime, timedelta

from aiogram.types import ReactionTypeCustomEmoji, ReactionTypeEmoji


def parse_reaction_command(text: str | None):
    if not text:
        return "selector", None

    cleaned = text.strip()
    if not cleaned:
        return "selector", None

    parts = cleaned.split(maxsplit=1)
    if len(parts) == 1:
        return "selector", None

    command = parts[0]
    if command != "/reaksiya":
        return "selector", None

    payload = parts[1].strip()
    if not payload:
        return "selector", None

    normalized = payload.lower()
    if normalized in {"premium", "premium-emoji", "premium_emoji"}:
        return "premium", None

    return "react", payload


def parse_bos_command(text: str | None):
    if not text:
        return 1, None

    cleaned = text.strip()
    if not cleaned:
        return 1, None

    match = re.match(r"^/(?P<command>bos)(?P<count>\d+)?(?:\s+(?P<emoji>.+))?$", cleaned)
    if not match:
        return 1, None

    count = int(match.group("count") or 1)
    if count < 1:
        count = 1
    if count > 100:
        count = 100

    emoji = (match.group("emoji") or "").strip()
    return count, emoji or None


def parse_subscription_duration(text: str | None):
    if not text:
        return 1, "forever"

    cleaned = text.strip().lower()
    if not cleaned:
        return 1, "forever"

    if cleaned in {"bir umr", "umr", "forever", "abadiy", "abadi", "bir umri", "bir umr"}:
        return 1, "forever"

    match = re.match(r"^(?P<value>\d+|bir)\s*(?P<unit>oy|hafta|soat|hour|hours|week|weeks|month|months|day|days)$", cleaned)
    if not match:
        return 1, "forever"

    value = 1 if match.group("value") == "bir" else int(match.group("value"))
    unit = match.group("unit")
    if unit in {"oy", "month", "months"}:
        return value, "month"
    if unit in {"hafta", "week", "weeks"}:
        return value, "week"
    if unit in {"soat", "hour", "hours"}:
        return value, "hour"
    return value, "day"


def get_subscription_duration_seconds(value: int, unit: str):
    if not value or unit == "forever":
        return None
    if unit == "month":
        return value * 30 * 24 * 60 * 60
    if unit == "week":
        return value * 7 * 24 * 60 * 60
    if unit == "hour":
        return value * 60 * 60
    if unit == "day":
        return value * 24 * 60 * 60
    return None


def get_reaction_from_row(row, default: str = "random") -> str:
    if not row:
        return default
    if len(row) > 2:
        return row[2] or default
    return default


def get_auto_react_from_row(row, default: bool = False) -> bool:
    if not row:
        return default
    if len(row) > 3:
        return bool(row[3])
    return default


def build_reaction_payload(emoji: str | None):
    if not emoji or emoji == "random":
        return None

    if str(emoji).startswith("custom:"):
        custom_emoji_id = str(emoji).split(":", 1)[1].strip()
        if custom_emoji_id:
            return [ReactionTypeCustomEmoji(custom_emoji_id=custom_emoji_id)]

    return [ReactionTypeEmoji(emoji=str(emoji))]
