import json
import os
from urllib import error, request


def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    if not bot_token or not chat_id:
        return False, "Server not configured for Telegram"

    api_base = os.getenv("TELEGRAM_API_BASE", "https://api.telegram.org").rstrip("/")
    payload = json.dumps(
        {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")

    tg_req = request.Request(
        f"{api_base}/bot{bot_token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(tg_req, timeout=15) as tg_res:
            tg_data = json.loads(tg_res.read().decode("utf-8") or "{}")
    except error.URLError as exc:
        reason = str(getattr(exc, "reason", exc))
        return False, reason

    if not tg_data.get("ok"):
        description = tg_data.get("description")
        if isinstance(description, str) and description:
            return False, description
        return False, "Telegram API returned an unknown error"

    return True, ""
