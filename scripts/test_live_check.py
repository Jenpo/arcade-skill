#!/usr/bin/env python3
"""Offline regression tests for live-check callback generation and Pages parsing."""
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/growth"))

from cloudflare_pages import parse_deployments  # noqa: E402
from live_check import send_message  # noqa: E402


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    raw = '\x1b[33mwarning\x1b[0m\n[{"Id":"26fb917c-3940-4ce8-9b31-ecddb10fce7c","Environment":"Production"}]\n'
    rows = parse_deployments(raw)
    require(rows[0]["Id"].startswith("26fb917c"), "Wrangler JSON parser lost the deployment id")

    env = {
        "ARCADE_TELEGRAM_BOT_TOKEN": "test-token",
        "ARCADE_TELEGRAM_CHAT_ID": "-100123",
    }
    with patch.dict(os.environ, env, clear=False):
        invalid = send_message("test", "site", "not-a-deployment")
        require(invalid["status"] == "LIVE_CHECK_INVALID", "invalid site rollback ref was accepted")

        fake = SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"ok": True, "result": {"message_id": 7}}),
            stderr="",
        )
        with patch("live_check.subprocess.run", return_value=fake) as runner:
            result = send_message("test", "site", "26fb917c:a532983")
        require(result == {"status": "PASS", "message_id": 7}, "valid live-check message failed")
        command = runner.call_args.args[0]
        payload = json.loads(command[command.index("--data-binary") + 1])
        callback = payload["reply_markup"]["inline_keyboard"][0][0]["callback_data"]
        require(callback == "rollback:site:26fb917c:a532983", "dual rollback callback changed")

    print("live-check smoke ok: Pages parser, callback validation, compact dual target")


if __name__ == "__main__":
    main()
