#!/usr/bin/env python3
"""Generate a Markdown P5 telemetry report from Cloudflare D1."""
import argparse, datetime as dt, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "growth/reports/telemetry-latest.md"

QUERIES = [
    ("Events last 7d",
     "SELECT COUNT(*) AS events_last_7d FROM arcade_events "
     "WHERE received_at >= datetime('now', '-7 days');"),
    ("Events by source/type",
     "SELECT source, type, COUNT(*) AS events FROM arcade_events "
     "WHERE received_at >= datetime('now', '-7 days') "
     "GROUP BY source, type ORDER BY events DESC;"),
    ("Game-over summary",
     "SELECT COUNT(*) AS game_overs, COALESCE(ROUND(AVG(floor), 1), 0) AS avg_floor, "
     "COALESCE(MAX(floor), 0) AS best_floor, "
     "COALESCE(ROUND(AVG(elapsed_ms) / 1000.0, 1), 0) AS avg_seconds "
     "FROM arcade_events WHERE type = 'game_over' "
     "AND received_at >= datetime('now', '-7 days');"),
    ("Top death floors",
     "SELECT floor, COUNT(*) AS deaths FROM arcade_events "
     "WHERE type = 'game_over' AND floor IS NOT NULL "
     "AND received_at >= datetime('now', '-7 days') "
     "GROUP BY floor ORDER BY deaths DESC, floor ASC LIMIT 20;"),
    ("Share and support hooks",
     "SELECT COALESCE(SUM(CASE WHEN type = 'share' THEN 1 ELSE 0 END), 0) AS shares, "
     "COALESCE(SUM(CASE WHEN type = 'tip_click' THEN 1 ELSE 0 END), 0) AS tip_clicks, "
     "COALESCE(SUM(CASE WHEN type = 'game_over' THEN 1 ELSE 0 END), 0) AS game_overs "
     "FROM arcade_events WHERE received_at >= datetime('now', '-7 days');"),
]


def extract_results(raw: str):
    decoder = json.JSONDecoder()
    for offset, char in enumerate(raw):
        if char != "[":
            continue
        try:
            data, _ = decoder.raw_decode(raw[offset:])
        except json.JSONDecodeError:
            continue
        if isinstance(data, list) and data and isinstance(data[0], dict) and "results" in data[0]:
            return data[0].get("results", [])
    raise ValueError("wrangler output did not include D1 JSON results")


def run_query(database: str, sql: str):
    proc = subprocess.run(
        ["npx", "wrangler", "d1", "execute", database, "--remote", "--command", sql],
        check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        return extract_results(proc.stdout)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def table(rows):
    if not rows:
        return "_No rows._\n"
    cols = list(rows[0].keys())
    out = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for row in rows:
        out.append("| " + " | ".join(str(row.get(c, "")) for c in cols) + " |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Arcade Skill telemetry report")
    ap.add_argument("--database", default="arcade_telemetry")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    lines = [
        "# Arcade Skill Telemetry Report",
        "",
        f"Generated: {dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
    ]
    for title, sql in QUERIES:
        rows = run_query(args.database, sql)
        lines.extend([f"## {title}", "", table(rows), ""])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(args.out)


if __name__ == "__main__":
    main()
