#!/usr/bin/env python3
"""Verify append-only evidence for a continuous unattended Tier A window."""
import argparse
import datetime as dt
import json
import math
from pathlib import Path

DEFAULT_LEDGER = Path.home() / "Library/Logs/arcade-skill/tier-a-audit.jsonl"
SCHEDULED_MINIMUMS = {"som": 1, "seo": 1, "weekly": 1}


def parse_time(value):
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.UTC)


def load_rows(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def evaluate(rows, days, now):
    window = dt.timedelta(days=days)
    start = now - window
    relevant = [
        row for row in rows
        if row.get("trigger") == "launchd"
        and start <= parse_time(row["timestamp"]) <= now
    ]
    completed = [row for row in relevant if row.get("status") in {"pass", "failed"}]
    started_ids = {row.get("run_id") for row in relevant if row.get("status") == "started" and row.get("run_id")}
    completed_ids = {row.get("run_id") for row in completed if row.get("run_id")}
    incomplete_ids = sorted(started_ids - completed_ids)
    by_task = {}
    failures = []
    for row in completed:
        by_task.setdefault(row["task"], []).append(row)
        if row["status"] == "failed":
            failures.append(row)
    requirements = {
        "queue": max(1, days * 260),
        "health": max(1, math.ceil(days * 3.5)),
        **SCHEDULED_MINIMUMS,
    }
    counts = {task: sum(row["status"] == "pass" for row in by_task.get(task, [])) for task in requirements}
    timestamps = sorted(parse_time(row["timestamp"]) for row in completed)
    span_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600 if len(timestamps) > 1 else 0
    required_span = max(0, days * 24 - 1)
    checks = {
        "no_failures": not failures,
        "no_incomplete_runs": not incomplete_ids,
        "continuous_span": span_hours >= required_span,
        **{f"{task}_minimum": counts[task] >= minimum for task, minimum in requirements.items()},
    }
    return {
        "status": "PASS" if all(checks.values()) else "PENDING",
        "days": days,
        "window_start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_end": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "span_hours": round(span_hours, 2),
        "counts": counts,
        "requirements": requirements,
        "failures": len(failures),
        "incomplete_runs": len(incomplete_ids),
        "checks": checks,
    }


def main():
    ap = argparse.ArgumentParser(description="Audit Arcade Tier A unattended evidence")
    ap.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--require-pass", action="store_true")
    args = ap.parse_args()
    result = evaluate(load_rows(args.ledger), args.days, dt.datetime.now(dt.UTC))
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    if args.require_pass and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
