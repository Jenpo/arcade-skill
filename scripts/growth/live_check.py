#!/usr/bin/env python3
"""Send owned-channel publish receipts and rollback actions to Telegram."""
import argparse
import json
import os
import urllib.request


def configured():
    return bool(os.environ.get("ARCADE_TELEGRAM_BOT_TOKEN") and os.environ.get("ARCADE_TELEGRAM_CHAT_ID"))


def send_message(text, rollback_kind="", rollback_ref=""):
    token = os.environ.get("ARCADE_TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("ARCADE_TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return {"status": "LIVE_CHECK_PENDING", "reason": "Telegram bot token or chat id is missing"}
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if rollback_kind and rollback_ref:
        callback = f"rollback:{rollback_kind}:{rollback_ref}"[:64]
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": "Rollback", "callback_data": callback}]]
        }
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        return {"status": "LIVE_CHECK_UNAVAILABLE", "reason": str(exc)}
    if not data.get("ok"):
        return {"status": "LIVE_CHECK_UNAVAILABLE", "reason": data.get("description", "Telegram rejected message")}
    return {"status": "PASS", "message_id": data["result"]["message_id"]}


def main():
    ap = argparse.ArgumentParser(description="Arcade live-check Telegram notifier")
    ap.add_argument("--message", required=True)
    ap.add_argument("--rollback-kind", choices=["site", "x", "jike"], default="")
    ap.add_argument("--rollback-ref", default="")
    ap.add_argument("--require-delivery", action="store_true")
    args = ap.parse_args()
    result = send_message(args.message, args.rollback_kind, args.rollback_ref)
    print(json.dumps(result, ensure_ascii=False))
    if args.require_delivery and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
