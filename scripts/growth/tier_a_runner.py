#!/usr/bin/env python3
"""Mac-local Tier A scheduler; credentials never leave the machine."""
import argparse
import datetime as dt
import fcntl
import json
import os
import re
import shlex
import subprocess
import sys
import uuid
from pathlib import Path

from live_check import send_message

ROOT = Path(__file__).resolve().parents[2]
LIVE_CHECK_ENV = Path(os.environ.get(
    "ARCADE_LIVE_CHECK_ENV",
    Path.home() / "Library/Application Support/ArcadeSkill/live-check.env",
))
HERMES_ENV = Path(os.environ.get("ARCADE_HERMES_ENV", Path.home() / ".hermes/.env"))
ROUTER_SH = Path(os.environ.get(
    "ARCADE_LOCAL_LLM_KEY_SOURCE",
    Path.home() / "Library/Application Support/S8/run_s8_litellm_router.sh",
))
AUDIT_LEDGER = Path(os.environ.get(
    "ARCADE_TIER_A_AUDIT_LEDGER",
    Path.home() / "Library/Logs/arcade-skill/tier-a-audit.jsonl",
))
NOTIFICATION_STATE = Path(os.environ.get(
    "ARCADE_TIER_A_NOTIFICATION_STATE",
    ROOT / "growth/state/tier-a-notification-signatures.json",
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
    load_env_file(LIVE_CHECK_ENV)
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


def append_audit(row):
    AUDIT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_LEDGER.open("a+", encoding="utf-8") as stream:
        fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
        stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def notify(message, rollback_kind="", rollback_ref=""):
    result = send_message(message, rollback_kind, rollback_ref)
    print(json.dumps(result, ensure_ascii=False))
    if result.get("status") != "PASS":
        raise SystemExit("Tier A live-check delivery failed")


def record_signature(key, signature, path=NOTIFICATION_STATE):
    state = {}
    if path.exists():
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            state = {}
    previous = state.get(key)
    if previous != signature:
        state[key] = signature
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(path)
    return previous is not None and previous != signature


def report_metric(text, label):
    match = re.search(rf"^- {re.escape(label)}: (.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else "unknown"


def task_health():
    result = subprocess.run(
        [sys.executable, "scripts/production_health.py", "--insecure", "--attempts", "3", "--retry-delay", "10"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode == 0:
        return

    output = "\n".join(
        (result.stdout + "\n" + result.stderr).strip().splitlines()[-12:]
    )
    message = (
        "❌ Arcade Tier A health FAIL\n"
        f"exit={result.returncode}\n"
        "https://arcade.fxpeek.com"
    )
    if output:
        message += f"\n\n{output}"
    notify(message)
    raise SystemExit(result.returncode)


def task_seo():
    dirty = capture(["git", "status", "--porcelain"])
    if dirty:
        raise SystemExit("refusing Tier A SEO run on a dirty worktree")
    run([sys.executable, "scripts/growth/seo_page_factory.py", "--publish"])
    run([sys.executable, "scripts/growth/tier_a_smoke.py"])
    run([sys.executable, "scripts/build_manifest.py"])
    changed = capture(["git", "status", "--porcelain"])
    if not changed:
        print("Arcade Tier A SEO: no publishable changes")
        return
    run(["git", "add", "docs/scenarios", "dist", "README.md"])
    run(["git", "commit", "-m", "chore: publish scheduled arcade scenarios"])
    run(["git", "push", "origin", "main"])
    manifest = json.loads((ROOT / "dist/manifest.json").read_text(encoding="utf-8"))["manifest_version"]
    run(["bash", "scripts/deploy_cloudflare_pages.sh"])
    run([
        sys.executable,
        "scripts/production_health.py",
        "--insecure",
        "--attempts", "12",
        "--retry-delay", "15",
        "--min-manifest-version", manifest,
    ])
    print(f"Arcade Tier A SEO deploy PASS: manifest {manifest}")


def som_direct_coverage(source):
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    direct = [
        row for row in rows
        if row.get("observation_status") == "observed_direct"
        and str(row.get("answer", "")).strip()
    ]
    return len(direct), len(rows)


def task_som():
    source = None
    if os.environ.get("ARCADE_SOM_CODEX_ENABLED") == "1":
        target = ROOT / "growth/som" / f"{dt.date.today().isoformat()}-codex.jsonl"
        if not target.exists():
            run([sys.executable, "scripts/growth/som_codex_collector.py", "--out", str(target)])
        source = target
    candidates = (
        sorted(
            path for path in (ROOT / "growth/som").glob("*.jsonl")
            if not path.name.startswith("._")
        )
        if (ROOT / "growth/som").exists()
        else []
    )
    if source is None and candidates:
        source = max(candidates, key=lambda path: path.stat().st_mtime)
    if source is None:
        print("Arcade Tier A SoM: no reviewed weekly engine-response export")
        return
    out = ROOT / "growth/reports" / f"som-{source.stem}.md"
    run([sys.executable, "scripts/growth/som_tracker.py", "score", "--input", str(source), "--out", str(out)])
    direct, total = som_direct_coverage(source)
    report = out.read_text(encoding="utf-8")
    signature = {
        "direct_coverage": f"{direct}/{total}",
        "mention_rate": report_metric(report, "Mention rate"),
        "citation_rate": report_metric(report, "Citation rate"),
    }
    if record_signature("som", signature):
        notify(
            "Arcade Tier A SoM changed\n"
            f"Direct coverage {direct}/{total}\n"
            f"Mention rate {signature['mention_rate']}\n"
            f"Citation rate {signature['citation_rate']}"
        )
    else:
        print(f"Arcade Tier A SoM unchanged: {signature}")


def task_weekly():
    telemetry = ROOT / "growth/reports/telemetry-latest.md"
    weekly = ROOT / "growth/reports/weekly-growth-latest.md"
    run([sys.executable, "scripts/growth/telemetry_report.py", "--out", str(telemetry)])
    run([sys.executable, "scripts/growth/weekly_growth_report.py", "--out", str(weekly)])
    print("Arcade Tier A weekly reports refreshed")


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
    started = dt.datetime.now(dt.UTC)
    base = {
        "run_id": uuid.uuid4().hex,
        "task": args.task,
        "trigger": os.environ.get("ARCADE_TIER_A_TRIGGER", "manual"),
        "pid": os.getpid(),
        "git_head": capture(["git", "rev-parse", "HEAD"]),
    }
    append_audit({**base, "status": "started", "timestamp": started.strftime("%Y-%m-%dT%H:%M:%SZ")})
    try:
        TASKS[args.task]()
    except BaseException as exc:
        finished = dt.datetime.now(dt.UTC)
        append_audit({
            **base,
            "status": "failed",
            "timestamp": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration_seconds": round((finished - started).total_seconds(), 3),
            "error_type": exc.__class__.__name__,
        })
        receipt = send_message(f"Arcade Tier A {args.task} FAIL\n{exc.__class__.__name__}")
        print(json.dumps(receipt, ensure_ascii=False))
        raise
    else:
        finished = dt.datetime.now(dt.UTC)
        append_audit({
            **base,
            "status": "pass",
            "timestamp": finished.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration_seconds": round((finished - started).total_seconds(), 3),
        })


if __name__ == "__main__":
    main()
