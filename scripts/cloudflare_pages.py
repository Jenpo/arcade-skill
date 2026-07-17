#!/usr/bin/env python3
"""Read Cloudflare Pages deployment metadata through authenticated Wrangler."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
DEPLOYMENT_ID = re.compile(r"^[a-f0-9]{8}-[a-f0-9-]{27}$")


def parse_deployments(raw):
    clean = ANSI.sub("", raw)
    start = clean.find("[")
    if start < 0:
        raise ValueError("Wrangler output did not contain a deployment list")
    rows = json.loads(clean[start:])
    if not isinstance(rows, list):
        raise ValueError("Wrangler deployment result is not a list")
    return rows


def current_production(project):
    proc = subprocess.run(
        [
            "npx", "wrangler", "pages", "deployment", "list",
            "--project-name", project,
            "--environment", "production",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=45,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError((proc.stderr or proc.stdout or "Wrangler failed")[-800:])
    rows = parse_deployments(proc.stdout)
    production = [row for row in rows if str(row.get("Environment", "")).lower() == "production"]
    if not production:
        raise RuntimeError("No Cloudflare Pages production deployment found")
    deployment_id = str(production[0].get("Id", ""))
    if not DEPLOYMENT_ID.fullmatch(deployment_id):
        raise RuntimeError("Cloudflare returned an invalid deployment id")
    return deployment_id


def main():
    ap = argparse.ArgumentParser(description="Read Cloudflare Pages production deployment id")
    ap.add_argument("--project", default="arcade-skill")
    ap.add_argument("--short", action="store_true", help="print the eight-character deployment prefix")
    args = ap.parse_args()
    deployment_id = current_production(args.project)
    print(deployment_id[:8] if args.short else deployment_id)


if __name__ == "__main__":
    main()
