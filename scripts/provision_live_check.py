#!/usr/bin/env python3
"""Provision the dedicated Arcade live-check bot without echoing credentials."""
import argparse
import getpass
import json
import os
import re
import secrets
import stat
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKER_DIR = ROOT / "infra/live-check-worker"
LOCAL_ENV = Path.home() / "Library/Application Support/ArcadeSkill/live-check.env"
WORKER_URL = "https://arcade-live-check.fxpeek.workers.dev"
REPO = "Jenpo/arcade-skill"
RESERVED_BOTS = {"jabondbot", "workerpro001_bot", "not2investbot"}
DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))
DEFAULT = urllib.request.build_opener()


def api_json(url, *, token="", payload=None, timeout=20):
    headers = {"accept": "application/json", "user-agent": "arcade-live-check-provisioner"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    data = None
    method = "GET"
    if payload is not None:
        headers["content-type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")
        method = "POST"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        opener = DIRECT if "api.telegram.org" in url else DEFAULT
        with opener.open(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def required_secret(prompt):
    value = getpass.getpass(prompt).strip()
    if not value or any(char in value for char in "\r\n"):
        raise SystemExit("Secret cannot be empty or contain a newline")
    return value


def required_value(prompt, pattern):
    value = input(prompt).strip()
    if not re.fullmatch(pattern, value):
        raise SystemExit(f"Invalid value for: {prompt.strip()}")
    return value


def run(command, *, input_text=None, cwd=ROOT):
    subprocess.run(
        command,
        cwd=cwd,
        text=True,
        input=input_text,
        check=True,
    )


def capture(command, *, cwd=ROOT):
    return subprocess.check_output(command, cwd=cwd, text=True)


def json_list(raw):
    clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", raw)
    start = clean.find("[")
    if start < 0:
        raise RuntimeError("Command output did not contain a JSON list")
    value = json.loads(clean[start:])
    if not isinstance(value, list):
        raise RuntimeError("Expected a JSON list")
    return value


def put_worker_secret(name, value):
    run(
        ["npx", "wrangler", "secret", "put", name, "--config", "wrangler.toml"],
        input_text=value + "\n",
        cwd=WORKER_DIR,
    )


def write_local_env(values):
    LOCAL_ENV.parent.mkdir(parents=True, exist_ok=True)
    temp = LOCAL_ENV.with_suffix(".tmp")
    body = "".join(f"{name}={value}\n" for name, value in values.items())
    descriptor = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o600)
        os.replace(temp, LOCAL_ENV)
    finally:
        if temp.exists():
            temp.unlink()


def load_local_env():
    values = {}
    if not LOCAL_ENV.is_file():
        return values
    for raw in LOCAL_ENV.read_text(encoding="utf-8").splitlines():
        if raw and not raw.startswith("#") and "=" in raw:
            name, value = raw.split("=", 1)
            values[name] = value
    return values


def verify_bot(token):
    data = api_json(f"https://api.telegram.org/bot{token}/getMe")
    if not data.get("ok"):
        raise SystemExit("Telegram rejected the bot token")
    username = str(data["result"].get("username", ""))
    if username.lower() in RESERVED_BOTS:
        raise SystemExit(f"Refusing to reuse Hermes polling bot @{username}")
    return username


def verify_provider_tokens(github_token, cloudflare_token, account_id):
    repo = api_json(f"https://api.github.com/repos/{REPO}", token=github_token)
    if repo.get("full_name") != REPO:
        raise SystemExit("GitHub token cannot read the target repository")
    cf = api_json("https://api.cloudflare.com/client/v4/user/tokens/verify", token=cloudflare_token)
    if not cf.get("success") or cf.get("result", {}).get("status") != "active":
        raise SystemExit("Cloudflare token is not active")
    pages = api_json(
        f"https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/arcade-skill/deployments?env=production&per_page=1",
        token=cloudflare_token,
    )
    if not pages.get("success"):
        raise SystemExit("Cloudflare token cannot read arcade-skill Pages deployments")


def register_webhook(token, webhook_secret):
    result = api_json(
        f"https://api.telegram.org/bot{token}/setWebhook",
        payload={
            "url": f"{WORKER_URL}/telegram/webhook",
            "secret_token": webhook_secret,
            "allowed_updates": ["callback_query"],
            "drop_pending_updates": True,
        },
    )
    if not result.get("ok"):
        raise SystemExit("Telegram webhook registration failed")


def check():
    values = load_local_env()
    required = {"ARCADE_TELEGRAM_BOT_TOKEN", "ARCADE_TELEGRAM_CHAT_ID"}
    missing = sorted(required - values.keys())
    if missing:
        raise SystemExit("Local live-check env is missing: " + ", ".join(missing))
    mode = stat.S_IMODE(LOCAL_ENV.stat().st_mode)
    if mode != 0o600:
        raise SystemExit(f"Unsafe local env mode: {oct(mode)}")
    username = verify_bot(values["ARCADE_TELEGRAM_BOT_TOKEN"])
    webhook = api_json(f"https://api.telegram.org/bot{values['ARCADE_TELEGRAM_BOT_TOKEN']}/getWebhookInfo")
    expected = f"{WORKER_URL}/telegram/webhook"
    if webhook.get("result", {}).get("url") != expected:
        raise SystemExit("Telegram webhook is not registered to the live-check Worker")
    worker_names = {
        row.get("name")
        for row in json_list(capture(
            ["npx", "wrangler", "secret", "list", "--config", "wrangler.toml", "--format", "json"],
            cwd=WORKER_DIR,
        ))
    }
    required_worker = {
        "TELEGRAM_BOT_TOKEN", "TELEGRAM_WEBHOOK_SECRET", "TELEGRAM_CHAT_ID",
        "TELEGRAM_ALLOWED_USER_IDS", "GITHUB_ROLLBACK_TOKEN",
        "CLOUDFLARE_PAGES_TOKEN", "CLOUDFLARE_ACCOUNT_ID",
    }
    if required_worker - worker_names:
        raise SystemExit("Worker secrets are incomplete: " + ", ".join(sorted(required_worker - worker_names)))
    github_names = {
        row.get("name")
        for row in json.loads(capture([
            "gh", "secret", "list", "--repo", REPO, "--json", "name",
        ]))
    }
    required_github = {"ARCADE_TELEGRAM_BOT_TOKEN", "ARCADE_TELEGRAM_CHAT_ID"}
    if required_github - github_names:
        raise SystemExit("GitHub notification secrets are incomplete")
    health = api_json(f"{WORKER_URL}/health")
    if not health.get("ok"):
        raise SystemExit("Live-check Worker health failed")
    print(json.dumps({
        "status": "PASS",
        "bot": f"@{username}",
        "webhook": expected,
        "worker": health.get("service"),
        "local_env_mode": oct(mode),
        "worker_secrets": len(required_worker),
        "github_secrets": len(required_github),
    }, ensure_ascii=False, indent=2))


def configure():
    print("Create a new BotFather bot dedicated to Arcade Skill. Do not reuse a Hermes bot.")
    telegram_token = required_secret("Dedicated Telegram bot token: ")
    username = verify_bot(telegram_token)
    chat_id = required_value("Telegram live-check chat id: ", r"-?[0-9]{1,20}")
    user_ids = required_value("Allowed Telegram user ids (comma separated): ", r"[0-9]{1,20}(,[0-9]{1,20})*")
    github_token = required_secret("GitHub fine-grained token (Actions write, arcade-skill only): ")
    cloudflare_token = required_secret("Cloudflare API token (Pages Write, fxpeek account only): ")
    account_id = required_value("Cloudflare account id: ", r"[a-f0-9]{32}")
    verify_provider_tokens(github_token, cloudflare_token, account_id)
    webhook_secret = secrets.token_urlsafe(32)

    worker_secrets = {
        "TELEGRAM_BOT_TOKEN": telegram_token,
        "TELEGRAM_WEBHOOK_SECRET": webhook_secret,
        "TELEGRAM_CHAT_ID": chat_id,
        "TELEGRAM_ALLOWED_USER_IDS": user_ids,
        "GITHUB_ROLLBACK_TOKEN": github_token,
        "CLOUDFLARE_PAGES_TOKEN": cloudflare_token,
        "CLOUDFLARE_ACCOUNT_ID": account_id,
    }
    for name, value in worker_secrets.items():
        put_worker_secret(name, value)
    run(["npx", "wrangler", "deploy"], cwd=WORKER_DIR)

    run(["gh", "secret", "set", "ARCADE_TELEGRAM_BOT_TOKEN", "--repo", REPO], input_text=telegram_token)
    run(["gh", "secret", "set", "ARCADE_TELEGRAM_CHAT_ID", "--repo", REPO], input_text=chat_id)
    write_local_env({
        "ARCADE_TELEGRAM_BOT_TOKEN": telegram_token,
        "ARCADE_TELEGRAM_CHAT_ID": chat_id,
    })
    register_webhook(telegram_token, webhook_secret)
    run([sys.executable, "scripts/install_tier_a_launchd.py", "--install"])
    print(f"Configured dedicated live-check bot @{username}")
    check()


def main():
    ap = argparse.ArgumentParser(description="Provision Arcade live-check rollback credentials")
    ap.add_argument("command", choices=["configure", "check"])
    args = ap.parse_args()
    if args.command == "configure":
        configure()
    else:
        check()


if __name__ == "__main__":
    main()
