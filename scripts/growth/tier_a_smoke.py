#!/usr/bin/env python3
"""Offline contract tests for the Tier A owned-channel safety layer."""
import json
import datetime as dt
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from content_linter import lint_text, load_policy
from som_codex_collector import build_rows, exclusive_lock, write_jsonl_atomic
from som_tracker import score_row
from telemetry_report import extract_results
from tier_a_audit import evaluate
from tier_a_runner import som_direct_coverage

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
    require(not score_row({"answer": "build your own arcade skill", "citations": []})[0], "generic arcade skill phrase counted as brand")
    require(score_row({"answer": "Arcade Skill by Jenpo", "citations": []})[0], "exact Arcade Skill brand was missed")

    with tempfile.TemporaryDirectory(prefix="arcade-p3-") as p3_tmp:
        p3_out = Path(p3_tmp) / "leaderboard.md"
        proc = subprocess.run(
            [sys.executable, "scripts/growth/leaderboard_digest.py", "--out", str(p3_out)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        require(proc.returncode != 0, "P3 generator ran while leaderboard was disabled")
        require(not p3_out.exists(), "disabled P3 generator wrote a draft")

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
            json.dumps({"engine": "Example", "prompt_id": "seen", "answer": "No matching project.", "observation_status": "observed_proxy"}) + "\n"
            + json.dumps({"engine": "Claude", "prompt_id": "contaminated", "answer": "Arcade Skill", "observation_status": "contaminated_local_install"}) + "\n"
            + json.dumps({"engine": "Example", "prompt_id": "blank", "answer": "", "observation_status": "unobserved"}) + "\n",
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
        require("Prompts observed: 1 (33.3% coverage)" in report, "SoM coverage gate is incorrect")
        require("Mention rate: 0/1" in report, "SoM scorer counted a contaminated local install")
        require("`contaminated_local_install`: 1" in report, "SoM report hid contaminated coverage")
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

        blocked_out = tmp_path / "blocked-seo"
        blocked_env = os.environ.copy()
        blocked_env.update({
            "ARCADE_LOCAL_LLM_API_KEY": "offline-smoke",
            "ARCADE_LOCAL_LLM_BASE_URL": "http://127.0.0.1:1/v1",
        })
        proc = subprocess.run(
            [
                sys.executable,
                "scripts/growth/seo_page_factory.py",
                "--out-dir", str(blocked_out),
                "--review-out", str(tmp_path / "blocked-review.md"),
            ],
            cwd=ROOT,
            env=blocked_env,
            text=True,
            capture_output=True,
            check=False,
        )
        require(proc.returncode != 0, "SEO publish gate ignored unavailable local LLM")
        require(not list(blocked_out.rglob("index.html")), "failed SEO review wrote publishable pages")

        som_coverage = tmp_path / "som-coverage.jsonl"
        som_coverage.write_text(
            "\n".join(json.dumps({
                "observation_status": "observed_direct" if index < 24 else "observed_proxy",
                "answer": "answer",
            }) for index in range(25)) + "\n",
            encoding="utf-8",
        )
        require(som_direct_coverage(som_coverage) == (24, 25), "SoM direct coverage gate is incorrect")

    print("tier a smoke ok: linter, fuse, dry-run, P3 disabled, SoM, collector, audit, D1 parser, local gate")


if __name__ == "__main__":
    main()
