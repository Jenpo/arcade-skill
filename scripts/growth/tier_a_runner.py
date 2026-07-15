#!/usr/bin/env python3
"""Mac-local Tier A scheduler; credentials never leave the machine."""
import argparse
import datetime as dt
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

from live_check import send_message

ROOT = Path(__file__).resolve().parents[2]
HERMES_ENV = Path(os.environ.get("ARCADE_HERMES_ENV", Path.home() / ".hermes/.env"))
ROUTER_SH = Path(os.environ.get(
    "ARCADE_LOCAL_LLM_KEY_SOURCE",
    Path.home() / "Library/Application Support/S8/run_s8_litellm_router.sh",
))


def load_env_file(path):
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.removeprefix("export ").split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def load_local_secrets():
    load_env_file(HERMES_ENV)
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat = os.environ.get("TELEGRAM_HOME_CHANNEL", "")
    if token and chat:
        os.environ.setdefault("ARCADE_TELEGRAM_BOT_TOKEN", token)
        os.environ.setdefault("ARCADE_TELEGRAM_CHAT_ID", chat)
    if ROUTER_SH.exists() and not os.environ.get("ARCADE_LOCAL_LLM_API_KEY"):
        assignments = {}
        master_value = ""
        for raw in ROUTER_SH.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            normalized = line.removeprefix("export ")
            key, value = normalized.split("=", 1)
            assignments[key.strip()] = shlex.split(f"x={value}")[0].split("=", 1)[1]
            if key.strip() == "LITELLM_MASTER_KEY":
                master_value = value
        if "KEY_FILE" in master_value and assignments.get("KEY_FILE"):
            key_path = Path(assignments["KEY_FILE"]).expanduser()
            if key_path.exists():
                master_value = key_path.read_text(encoding="utf-8").strip()
        else:
            master_value = assignments.get("LITELLM_MASTER_KEY", "")
        if master_value and "$" not in master_value:
            os.environ["ARCADE_LOCAL_LLM_API_KEY"] = master_value


def run(cmd, check=True):
    return subprocess.run(cmd, cwd=ROOT, text=True, check=check)


def capture(cmd):
    return subprocess.check_output(cmd, cwd=ROOT, text=True).strip()


def notify(message, rollback_kind="", rollback_ref=""):
    result = send_message(message, rollback_kind, rollback_ref)
    print(json.dumps(result, ensure_ascii=False))
    if result.get("status") != "PASS":
        raise SystemExit("Tier A live-check delivery failed")


def task_health():
    run([sys.executable, "scripts/production_health.py", "--insecure", "--attempts", "3", "--retry-delay", "10"])
    notify("Arcade Tier A health PASS\nhttps://arcade.fxpeek.com")


def task_seo():
    dirty = capture(["git", "status", "--porcelain"])
    if dirty:
        raise SystemExit("refusing Tier A SEO run on a dirty worktree")
    previous = capture(["git", "rev-parse", "HEAD"])
    run([sys.executable, "scripts/growth/seo_page_factory.py", "--publish"])
    run([sys.executable, "scripts/growth/tier_a_smoke.py"])
    run([sys.executable, "scripts/build_manifest.py"])
    changed = capture(["git", "status", "--porcelain"])
    if not changed:
        notify("Arcade Tier A SEO PASS\nNo publishable page changes this cycle.")
        return
    run(["git", "add", "docs/scenarios", "dist", "README.md"])
    run(["git", "commit", "-m", "chore: publish scheduled arcade scenarios"])
    run(["git", "push", "origin", "main"])
    manifest = json.loads((ROOT / "dist/manifest.json").read_text(encoding="utf-8"))["manifest_version"]
    run([
        sys.executable,
        "scripts/production_health.py",
        "--insecure",
        "--attempts", "12",
        "--retry-delay", "15",
        "--min-manifest-version", manifest,
    ])
    notify(f"Arcade Tier A SEO deploy PASS\nmanifest {manifest}", "site", previous[:40])


def task_som():
    source = None
    if os.environ.get("ARCADE_SOM_CODEX_ENABLED") == "1":
        target = ROOT / "growth/som" / f"{dt.date.today().isoformat()}-codex.jsonl"
        if not target.exists():
            run([sys.executable, "scripts/growth/som_codex_collector.py", "--out", str(target)])
        source = target
    candidates = sorted((ROOT / "growth/som").glob("*.jsonl")) if (ROOT / "growth/som").exists() else []
    if source is None and candidates:
        source = max(candidates, key=lambda path: path.stat().st_mtime)
    if source is None:
        notify("Arcade Tier A SoM PENDING\nNo reviewed weekly engine-response export is available.")
        return
    out = ROOT / "growth/reports" / f"som-{source.stem}.md"
    run([sys.executable, "scripts/growth/som_tracker.py", "score", "--input", str(source), "--out", str(out)])
    notify(f"Arcade Tier A SoM PASS\n{out.name}")


def task_weekly():
    telemetry = ROOT / "growth/reports/telemetry-latest.md"
    weekly = ROOT / "growth/reports/weekly-growth-latest.md"
    run([sys.executable, "scripts/growth/telemetry_report.py", "--out", str(telemetry)])
    run([sys.executable, "scripts/growth/weekly_growth_report.py", "--out", str(weekly)])
    notify("Arcade Tier A weekly report PASS\nTelemetry and growth reports refreshed.")


def task_queue():
    queue = ROOT / "growth/queue/owned"
    if not queue.exists():
        return
    for item in sorted(queue.glob("*.json")):
        run([
            sys.executable,
            "scripts/growth/own_channel_publisher.py",
            "--input", str(item),
            "--send",
            "--require-notification",
        ])
        sent = ROOT / "growth/queue/sent"
        sent.mkdir(parents=True, exist_ok=True)
        item.replace(sent / item.name)


TASKS = {
    "health": task_health,
    "seo": task_seo,
    "som": task_som,
    "weekly": task_weekly,
    "queue": task_queue,
}


def main():
    ap = argparse.ArgumentParser(description="Arcade Tier A Mac-local runner")
    ap.add_argument("task", choices=sorted(TASKS))
    args = ap.parse_args()
    load_local_secrets()
    TASKS[args.task]()


if __name__ == "__main__":
    main()
