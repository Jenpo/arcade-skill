#!/usr/bin/env python3
"""Idempotent Tier A publisher for explicitly approved owned-channel items."""
import argparse
import datetime as dt
import fcntl
import json
import os
import subprocess
import urllib.request
from pathlib import Path

from content_linter import lint_text, load_policy
from live_check import configured as live_check_configured
from live_check import send_message

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LEDGER = ROOT / "growth/state/own-channel-ledger.jsonl"


def read_ledger(path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def append_ledger(path, row):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        stream.flush()
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def send_x(text, image=""):
    cmd = ["twitter", "post", text, "--json"]
    if image:
        cmd.extend(["--image", image])
    proc = subprocess.run(cmd, text=True, capture_output=True, timeout=45, check=False)
    if proc.returncode:
        raise RuntimeError((proc.stderr or proc.stdout or "twitter post failed")[-800:])
    data = json.loads(proc.stdout)
    result = data.get("data", data)
    post_id = str(result.get("id") or result.get("rest_id") or "")
    if not post_id:
        raise RuntimeError("twitter CLI returned no post id")
    return {"post_id": post_id, "url": f"https://x.com/i/web/status/{post_id}"}


def send_jike(payload):
    url = os.environ.get("ARCADE_MULTIPOST_WEBHOOK_URL", "")
    token = os.environ.get("ARCADE_MULTIPOST_TOKEN", "")
    if not url or not token:
        raise RuntimeError("Jike MultiPost webhook is not configured")
    body = {**payload, "approved_live_send": True, "platform": "jike"}
    req = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    post_id = str(data.get("post_id") or data.get("id") or "")
    if not post_id:
        raise RuntimeError("Jike sender returned no post id")
    return {"post_id": post_id, "url": str(data.get("url") or "")}


def main():
    ap = argparse.ArgumentParser(description="Arcade Tier A owned-channel publisher")
    ap.add_argument("--input", type=Path, required=True, help="approved JSON queue item")
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--send", action="store_true", help="perform live send; default is dry-run")
    ap.add_argument("--require-notification", action="store_true")
    args = ap.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    required = ["content_id", "channel", "text", "approved_live_send"]
    missing = [name for name in required if name not in payload]
    if missing:
        raise SystemExit(f"missing payload fields: {', '.join(missing)}")
    if payload["channel"] not in {"x", "jike"}:
        raise SystemExit("Tier A publisher supports owned x and jike channels only")
    if payload["approved_live_send"] is not True:
        raise SystemExit("approved_live_send must be true")

    policy = load_policy()
    errors = lint_text(str(payload["text"]), payload["channel"], policy)
    if errors:
        raise SystemExit("content blocked: " + "; ".join(errors))

    today = dt.datetime.now(dt.UTC).date().isoformat()
    ledger = read_ledger(args.ledger)
    key = f"{payload['content_id']}:{payload['channel']}:{payload.get('account_id', 'default')}"
    if any(row.get("idempotency_key") == key and row.get("status") == "sent" for row in ledger):
        raise SystemExit(f"duplicate send blocked: {key}")
    sent_today = sum(1 for row in ledger if row.get("date") == today and row.get("status") == "sent")
    if sent_today >= int(policy["max_posts_per_day"]):
        raise SystemExit("daily owned-channel fuse is open")
    if args.require_notification and not live_check_configured():
        raise SystemExit("live-check Telegram is required but not configured")

    if not args.send:
        print(json.dumps({"status": "DRY_RUN_PASS", "idempotency_key": key}, ensure_ascii=False))
        return

    result = send_x(payload["text"], payload.get("image", "")) if payload["channel"] == "x" else send_jike(payload)
    row = {
        "date": today,
        "sent_at": dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "sent",
        "idempotency_key": key,
        "content_id": payload["content_id"],
        "channel": payload["channel"],
        **result,
    }
    append_ledger(args.ledger, row)
    receipt = send_message(
        f"Arcade Tier A publish PASS\n{payload['channel']}: {result.get('url') or result['post_id']}",
        payload["channel"],
        result["post_id"],
    )
    print(json.dumps({"status": "PASS", "publish": row, "live_check": receipt}, ensure_ascii=False))
    if args.require_notification and receipt["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
