#!/usr/bin/env python3
"""Run the offline growth-engine smoke suite."""
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(cmd, input_text=None):
    print("+ " + " ".join(str(x) for x in cmd))
    subprocess.run(cmd, cwd=ROOT, check=True, text=True, input=input_text)


def main():
    ap = argparse.ArgumentParser(description="Arcade growth smoke suite")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "growth/smoke")
    args = ap.parse_args()
    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    run(["python3", "scripts/growth/mention_radar.py", "--offline", "--no-llm-review", "--out", str(out / "radar.md")])
    run(["python3", "scripts/growth/seo_page_factory.py", "--dry-run", "--no-llm-review"])
    run(["python3", "scripts/growth/tier_a_smoke.py"])
    run(["python3", "scripts/test_live_check.py"])
    run(["node", "--test", "tests/live-check-worker.test.mjs"])
    run(["python3", "scripts/test_launcher_fallback.py"])
    run(["python3", "scripts/growth/weekly_growth_report.py", "--out", str(out / "weekly.md")])
    run(
        ["python3", "scripts/local_llm.py", "copy", "--json", "--max-tokens", "20", "--timeout", "45"],
        input_text="只输出OK",
    )
    print(f"growth smoke ok: {out}")


if __name__ == "__main__":
    main()
