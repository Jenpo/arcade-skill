#!/usr/bin/env python3
"""Install Mac LaunchAgents for Arcade Tier A local automation."""
import argparse
import os
import plistlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAUNCH_AGENTS = Path.home() / "Library/LaunchAgents"
LOG_DIR = Path.home() / "Library/Logs/arcade-skill"
RUNNER = ROOT / "scripts/growth/tier_a_runner.py"

JOBS = {
    "som": {"Weekday": 1, "Hour": 11, "Minute": 5},
    "seo": {"Weekday": 3, "Hour": 11, "Minute": 15},
    "weekly": {"Weekday": 0, "Hour": 11, "Minute": 25},
    "health": {"StartInterval": 21600},
    "queue": {"StartInterval": 300},
}


def payload(task, schedule):
    label = f"com.fxpeek.arcade.tier-a.{task}"
    data = {
        "Label": label,
        "ProgramArguments": [sys.executable, str(RUNNER), task],
        "WorkingDirectory": str(ROOT),
        "RunAtLoad": False,
        "StandardOutPath": str(LOG_DIR / f"{task}.log"),
        "StandardErrorPath": str(LOG_DIR / f"{task}.error.log"),
        "EnvironmentVariables": {
            "PATH": os.environ.get("PATH", "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"),
            "NO_PROXY": "127.0.0.1,localhost,192.168.0.0/16,192.168.2.1,192.168.31.0/24",
        },
    }
    if "StartInterval" in schedule:
        data["StartInterval"] = schedule["StartInterval"]
    else:
        data["StartCalendarInterval"] = schedule
    return label, data


def main():
    ap = argparse.ArgumentParser(description="Install Arcade Tier A LaunchAgents")
    ap.add_argument("--install", action="store_true")
    args = ap.parse_args()
    LAUNCH_AGENTS.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    uid = os.getuid()
    for task, schedule in JOBS.items():
        label, data = payload(task, schedule)
        path = LAUNCH_AGENTS / f"{label}.plist"
        path.write_bytes(plistlib.dumps(data, sort_keys=False))
        print(path)
        if args.install:
            subprocess.run(["launchctl", "bootout", f"gui/{uid}/{label}"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["launchctl", "bootstrap", f"gui/{uid}", str(path)], check=True)
    if not args.install:
        print("Rendered only. Re-run with --install to load the jobs.")


if __name__ == "__main__":
    main()
