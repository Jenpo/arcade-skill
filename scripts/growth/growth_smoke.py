#!/usr/bin/env python3
"""Run the offline growth-engine smoke suite."""
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(cmd):
    print("+ " + " ".join(str(x) for x in cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)


def main():
    ap = argparse.ArgumentParser(description="Arcade growth smoke suite")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "growth/smoke")
    args = ap.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    run(["python3", "scripts/growth/mention_radar.py", "--offline", "--out", str(out / "radar.md")])
    run(["python3", "scripts/growth/seo_page_factory.py", "--dry-run"])
    run(["python3", "scripts/growth/tier_a_smoke.py"])
    run(["python3", "scripts/growth/weekly_growth_report.py", "--out", str(out / "weekly.md")])
    run(["python3", "scripts/local_llm.py", "design-review", "--input", "docs/scenarios/index.html", "--json"])
    print(f"growth smoke ok: {out}")


if __name__ == "__main__":
    main()
