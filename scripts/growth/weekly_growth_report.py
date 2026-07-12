#!/usr/bin/env python3
"""Assemble the weekly Arcade Skill growth operating report."""
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "growth/reports/weekly-growth-latest.md"


def read_optional(path: Path, fallback: str):
    if path.exists():
        return path.read_text(encoding="utf-8")
    return fallback


def count_cards(path: Path):
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("### "))


def count_files(path: Path, pattern: str):
    return len(list(path.rglob(pattern))) if path.exists() else 0


def main():
    ap = argparse.ArgumentParser(description="Arcade weekly growth report")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    radar = ROOT / "growth/radar/radar-latest.md"
    seo_dir = ROOT / "growth/drafts/seo"
    policy = json.loads((ROOT / "config/tier-a-policy.json").read_text(encoding="utf-8"))
    som = ROOT / "growth/reports/som-latest.md"
    telemetry = ROOT / "growth/reports/telemetry-latest.md"

    lines = [
        "# Arcade Skill Weekly Growth Report",
        "",
        f"Generated: {dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "## Operating Summary",
        "",
        f"- Radar review cards: {count_cards(radar)}",
        f"- SEO scenario drafts: {count_files(seo_dir, 'index.html')}",
        f"- P3 leaderboard publisher: {'enabled' if policy.get('p3_leaderboard_enabled') else 'disabled'}",
        f"- SoM report ready: {'yes' if som.exists() else 'no'}",
        f"- Telemetry report ready: {'yes' if telemetry.exists() else 'no'}",
        "",
        "## Human Review Queue",
        "",
        "- Review radar cards before any reply, PR, or social comment.",
        "- Third-party replies and repository submissions require one-click approval.",
        "- Tier A owned-channel items publish only after deterministic linter and fuse checks.",
        "- P3 stays disabled until a production global ranking exists.",
        "",
        "## Current SoM",
        "",
        read_optional(som, "_Run `python3 scripts/growth/som_tracker.py init` and score exported answers._"),
        "",
        "## Current Telemetry",
        "",
        read_optional(telemetry, "_Run `python3 scripts/growth/telemetry_report.py` after D1 has data._"),
        "",
    ]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
