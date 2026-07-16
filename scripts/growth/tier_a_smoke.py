#!/usr/bin/env python3
"""Offline contract tests for the Tier A owned-channel safety layer."""
import json
import datetime as dt
import subprocess
import sys
import tempfile
from pathlib import Path

from content_linter import lint_text, load_policy
from som_codex_collector import build_rows, exclusive_lock, write_jsonl_atomic
from telemetry_report import extract_results
from tier_a_audit import evaluate

ROOT = Path(__file__).resolve().parents[2]


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    policy = load_policy()
    safe = "Tests are running. One quick retro run: https://arcade.fxpeek.com/play/"
    require(not lint_text(safe, "x", policy), "safe owned-channel copy was blocked")
    require(lint_text("The global leaderboard is live", "x", policy), "unreleased leaderboard claim passed")
    require(lint_text("token=super-secret-value", "x", policy), "credential pattern passed")
    require(lint_text("Read https://example.com", "x", policy), "unapproved external host passed")
    require(policy.get("max_posts_per_day") == 3, "daily fuse must remain at 3")
    require(policy.get("p3_leaderboard_enabled") is False, "P3 must remain disabled before global ranking")

    with tempfile.TemporaryDirectory(prefix="arcade-tier-a-") as tmp:
        tmp_path = Path(tmp)
        ledger = tmp_path / "ledger.jsonl"
        proc = subprocess.run(
            [
                sys.executable,
                "scripts/growth/own_channel_publisher.py",
                "--input",
                "scripts/growth/own_channel_sample.json",
                "--ledger",
                str(ledger),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        require(proc.returncode == 0, proc.stderr or proc.stdout)
        result = json.loads(proc.stdout)
        require(result.get("status") == "DRY_RUN_PASS", "publisher dry-run did not pass")

        som_input = tmp_path / "som.jsonl"
        som_output = tmp_path / "som.md"
        som_input.write_text(
            json.dumps({"engine": "Example", "prompt_id": "seen", "answer": "No matching project."}) + "\n"
            + json.dumps({"engine": "Example", "prompt_id": "blank", "answer": ""}) + "\n",
            encoding="utf-8",
        )
        proc = subprocess.run(
            [sys.executable, "scripts/growth/som_tracker.py", "score", "--input", str(som_input), "--out", str(som_output)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        require(proc.returncode == 0, proc.stderr or proc.stdout)
        report = som_output.read_text(encoding="utf-8")
        require("Prompts observed: 1 (50.0% coverage)" in report, "SoM coverage gate is incorrect")
        require("not direct UI measurements" in report, "SoM proxy disclosure is missing")

        prompts = json.loads((ROOT / "scripts/growth/som_prompts.json").read_text(encoding="utf-8"))
        batch = {
            "answers": [
                {"prompt_id": row["id"], "answer": f"answer for {row['id']}", "citations": []}
                for row in prompts
            ]
        }
        collected = build_rows(prompts, batch, "2026-07-16")
        require(len(collected) == 25, "SoM collector must emit 25 rows")
        require(
            sum(row["observation_status"] == "observed_proxy" for row in collected) == 5,
            "SoM collector must emit exactly five proxy observations",
        )
        require(
            sum(row["observation_status"] == "unobserved" for row in collected) == 20,
            "SoM collector must preserve 20 unobserved rows",
        )
        collected_path = tmp_path / "collected.jsonl"
        write_jsonl_atomic(collected_path, collected)
        require(len(collected_path.read_text(encoding="utf-8").splitlines()) == 25, "atomic JSONL write failed")
        lock_path = tmp_path / ".collector.lock"
        with exclusive_lock(lock_path):
            try:
                with exclusive_lock(lock_path):
                    pass
            except SystemExit:
                pass
            else:
                raise SystemExit("collector concurrency lock did not block a duplicate run")

        now = dt.datetime(2026, 7, 16, 12, 0, tzinfo=dt.UTC)
        audit_rows = []
        for index in range(260):
            timestamp = now - dt.timedelta(hours=24) + dt.timedelta(seconds=index * 330)
            audit_rows.append({
                "run_id": f"queue-{index}",
                "task": "queue", "trigger": "launchd", "status": "pass",
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
            })
        for task, count in {"health": 4, "som": 1, "seo": 1, "weekly": 1}.items():
            for index in range(count):
                timestamp = now - dt.timedelta(hours=23, minutes=50) + dt.timedelta(minutes=index)
                audit_rows.append({
                    "run_id": f"{task}-{index}",
                    "task": task, "trigger": "launchd", "status": "pass",
                    "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
                })
        audit = evaluate(audit_rows, 1, now)
        require(audit["status"] == "PASS", "Tier A audit rejected complete evidence")
        audit_rows.append({
            "run_id": "failed-health",
            "task": "health", "trigger": "launchd", "status": "failed",
            "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        require(evaluate(audit_rows, 1, now)["status"] == "PENDING", "Tier A audit ignored a failure")
        audit_rows.pop()
        audit_rows.append({
            "run_id": "orphan", "task": "queue", "trigger": "launchd", "status": "started",
            "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
        require(evaluate(audit_rows, 1, now)["status"] == "PENDING", "Tier A audit ignored an incomplete run")

        noisy = "\x1b[33mWARNING proxy [not-json]\x1b[0m\n" + json.dumps([{"results": [{"ok": 1}]}])
        require(extract_results(noisy) == [{"ok": 1}], "D1 parser accepted Wrangler warning as JSON")

    print("tier a smoke ok: linter, fuse, dry-run, P3 disabled, SoM, collector, audit, D1 parser")


if __name__ == "__main__":
    main()
