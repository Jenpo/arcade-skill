#!/usr/bin/env python3
"""Offline contract tests for the Tier A owned-channel safety layer."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from content_linter import lint_text, load_policy

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

    print("tier a smoke ok: linter, daily fuse, idempotent dry-run, P3 disabled, SoM coverage")


if __name__ == "__main__":
    main()
