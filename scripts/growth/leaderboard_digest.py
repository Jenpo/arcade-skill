#!/usr/bin/env python3
"""Create human-reviewed leaderboard digest drafts."""
import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "scripts/growth/leaderboard_sample.json"
DEFAULT_OUT = ROOT / "growth/drafts/leaderboard-latest.md"


def fmt_time(ms):
    if ms is None:
        return "-"
    seconds = int(round(ms / 1000))
    return f"{seconds // 60}:{seconds % 60:02d}"


def render(data):
    rows = sorted(data.get("rows", []), key=lambda r: (r.get("rank", 999), -r.get("floor", 0)))
    if not rows:
        return "\n".join([
            "# Arcade Skill Leaderboard Digest",
            "",
            "M2 leaderboard is not live yet.",
            "",
            "Use this placeholder once Worker/D1 ranking rows are available:",
            "",
            "- Top 10 daily challenge",
            "- Best floor",
            "- Fastest time at deepest floor",
            "- Share CTA back to https://arcade.fxpeek.com/play/?daily=1",
            "",
        ])
    leader = rows[0]
    generated = dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    table = [
        "| Rank | Player | Floor | Time | Region |",
        "| ---: | --- | ---: | ---: | --- |",
    ]
    for row in rows[:10]:
        table.append(
            f"| {row.get('rank','')} | {row.get('player','???')} | {row.get('floor','')} | {fmt_time(row.get('elapsed_ms'))} | {row.get('country','')} |"
        )
    return "\n".join([
        "# Arcade Skill Leaderboard Digest",
        "",
        f"Generated: {generated}",
        f"Period: {data.get('period', 'latest')}",
        f"Mode: {data.get('mode', 'daily')}",
        "",
        "## Top 10",
        "",
        *table,
        "",
        "## English Draft",
        "",
        (
            f"The cabinet has a new ghost: {leader.get('player','???')} reached floor "
            f"{leader.get('floor','?')} in Down 100 Floors. Tiny retro break, clean rules, "
            "no paid revives. Try today's seed: https://arcade.fxpeek.com/play/?daily=1"
        ),
        "",
        "## 中文草稿",
        "",
        (
            f"今天的下 100 层榜首是 {leader.get('player','???')}，摸到了第 "
            f"{leader.get('floor','?')} 层。复古小机台，规则干净，不卖血量，不卖复活。"
            "来同一张每日种子试一把：https://arcade.fxpeek.com/play/?daily=1"
        ),
        "",
        "## Review Checklist",
        "",
        "- Confirm rows came from the production ranking query.",
        "- Confirm no private identifiers are included.",
        "- Publish manually only after review.",
        "",
    ])


def main():
    ap = argparse.ArgumentParser(description="Arcade leaderboard digest draft")
    ap.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8")) if args.input.exists() else {"rows": []}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render(data), encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
