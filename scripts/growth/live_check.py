#!/usr/bin/env python3
"""Send owned-channel publish receipts and rollback actions to Telegram."""
import argparse
import json
import os
import re
import subprocess


def configured():
    return bool(os.environ.get("ARCADE_TELEGRAM_BOT_TOKEN") and os.environ.get("ARCADE_TELEGRAM_CHAT_ID"))


def send_message(text, rollback_kind="", rollback_ref=""):
    token = os.environ.get("ARCADE_TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("ARCADE_TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return {"status": "LIVE_CHECK_PENDING", "reason": "Telegram bot token or chat id is missing"}
    payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
    if rollback_kind and rollback_ref:
        patterns = {
            "site": r"[a-f0-9]{8}:[a-f0-9]{7,40}",
            "github": r"[a-f0-9]{7,40}",
            "x": r"[A-Za-z0-9._-]{1,40}",
            "jike": r"[A-Za-z0-9._-]{1,40}",
        }
        if rollback_kind not in patterns or not re.fullmatch(patterns[rollback_kind], rollback_ref):
            return {"status": "LIVE_CHECK_INVALID", "reason": "invalid rollback reference"}
        callback = f"rollback:{rollback_kind}:{rollback_ref}"
        if len(callback.encode("utf-8")) > 64:
            return {"status": "LIVE_CHECK_INVALID", "reason": "rollback callback exceeds Telegram limit"}
        payload["reply_markup"] = {
            "inline_keyboard": [[{"text": "Rollback", "callback_data": callback}]]
        }
    try:
        proc = subprocess.run(
            [
                "curl", "--silent", "--show-error", "--fail-with-body",
                "--noproxy", "*", "--max-time", "15",
                "--header", "Content-Type: application/json",
                "--data-binary", json.dumps(payload, ensure_ascii=False),
                f"https://api.telegram.org/bot{token}/sendMessage",
            ],
            text=True,
            capture_output=True,
            timeout=20,
            check=False,
        )
        if proc.returncode:
            raise RuntimeError((proc.stderr or proc.stdout or "curl failed")[-500:])
        data = json.loads(proc.stdout)
    except Exception as exc:
        return {"status": "LIVE_CHECK_UNAVAILABLE", "reason": str(exc)}
    if not data.get("ok"):
        return {"status": "LIVE_CHECK_UNAVAILABLE", "reason": data.get("description", "Telegram rejected message")}
    return {"status": "PASS", "message_id": data["result"]["message_id"]}


def main():
    ap = argparse.ArgumentParser(description="Arcade live-check Telegram notifier")
    ap.add_argument("--message", required=True)
    ap.add_argument("--rollback-kind", choices=["site", "github", "x", "jike"], default="")
    ap.add_argument("--rollback-ref", default="")
    ap.add_argument("--require-delivery", action="store_true")
    args = ap.parse_args()
    result = send_message(args.message, args.rollback_kind, args.rollback_ref)
    print(json.dumps(result, ensure_ascii=False))
    if args.require_delivery and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
