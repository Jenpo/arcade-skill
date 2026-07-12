#!/usr/bin/env python3
"""Production health checks for arcade.fxpeek.com.

This is intentionally read-only. It verifies the public site, manifest, bundle
hashes, and monetization routing without touching external communities or
private credentials.
"""
import argparse
import hashlib
import json
import ssl
import sys
import time
import urllib.request
from dataclasses import dataclass


DEFAULT_BASE = "https://arcade.fxpeek.com"
ROUTES = [
    ("/", "Arcade Skill"),
    ("/play/", "Down 100 Floors"),
    ("/support/", "Stripe"),
    ("/about/", "About Arcade Skill"),
    ("/scenarios/", "Scenario pages with cabinet energy"),
    ("/robots.txt", "Sitemap: https://arcade.fxpeek.com/sitemap.xml"),
    ("/sitemap.xml", "https://arcade.fxpeek.com/scenarios/"),
    ("/llms.txt", "Arcade Skill"),
    ("/ai.txt", "Arcade Skill"),
    ("/docs/DESIGN.md", "Arcade Skill Design"),
    ("/docs/awesome-design-md-proposal.md", "Design MD Request"),
]
SCENARIO_ROUTES = [
    "/scenarios/games-while-ai-agent-runs-tests/",
    "/scenarios/claude-code-break-game/",
    "/scenarios/ai-agent-waiting-game-zh/",
]
SSL_CONTEXT = None


@dataclass
class Check:
    name: str
    ok: bool
    detail: str


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "arcade-skill-health/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
        body = resp.read()
        status = getattr(resp, "status", 200)
        final_url = resp.geturl()
    return status, final_url, body


def text(body):
    return body.decode("utf-8", errors="replace")


def add(checks, name, ok, detail):
    checks.append(Check(name, bool(ok), detail))


def check_route(checks, base, route, needle):
    url = base + route
    try:
        status, final_url, body = fetch(url)
        content = text(body)
        add(checks, f"route {route}", status == 200 and needle in content,
            f"status={status} final={final_url} needle={needle!r}")
    except Exception as exc:
        add(checks, f"route {route}", False, str(exc))


def check_manifest(checks, base, min_manifest_version=""):
    status, _, body = fetch(base + "/manifest.json")
    manifest = json.loads(text(body))
    add(checks, "manifest http", status == 200, f"status={status}")
    add(checks, "manifest schema", manifest.get("schema_version") == 2,
        f"schema_version={manifest.get('schema_version')}")
    add(checks, "kill switch", manifest.get("kill_switch") is False,
        f"kill_switch={manifest.get('kill_switch')}")
    if min_manifest_version:
        current = str(manifest.get("manifest_version", ""))
        add(checks, "manifest version",
            current >= min_manifest_version,
            f"current={current} minimum={min_manifest_version}")

    monetization = manifest.get("monetization", {})
    tips = monetization.get("tips", {})
    add(checks, "stripe support enabled",
        tips.get("enabled") is True and tips.get("provider") == "stripe" and tips.get("url", "").startswith(base + "/support"),
        f"provider={tips.get('provider')} url={tips.get('url')}")
    ads = monetization.get("ads", {})
    add(checks, "localhost-safe ads flag",
        ads.get("enabled") is False,
        f"ads.enabled={ads.get('enabled')}")

    games = manifest.get("games", [])
    add(checks, "manifest games", len(games) >= 1, f"games={len(games)}")
    for game in games:
        entry = game.get("entry", "")
        expected = game.get("sha256", "")
        try:
            status, _, bundle = fetch(entry)
            actual = hashlib.sha256(bundle).hexdigest()
            add(checks, f"bundle {game.get('id', '?')} sha256",
                status == 200 and actual == expected,
                f"status={status} expected={expected[:12]} actual={actual[:12]} size={len(bundle)}")
        except Exception as exc:
            add(checks, f"bundle {game.get('id', '?')} sha256", False, str(exc))


def run(base, min_manifest_version=""):
    checks = []
    for route, needle in ROUTES:
        check_route(checks, base, route, needle)
    for route in SCENARIO_ROUTES:
        check_route(checks, base, route, "FAQPage")
    try:
        check_manifest(checks, base, min_manifest_version)
    except Exception as exc:
        add(checks, "manifest parse", False, str(exc))
    return checks


def main():
    global SSL_CONTEXT
    ap = argparse.ArgumentParser(description="Arcade production health check")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--insecure", action="store_true", help="local smoke only: skip TLS verification")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--attempts", type=int, default=1)
    ap.add_argument("--retry-delay", type=int, default=10)
    ap.add_argument("--min-manifest-version", default="")
    args = ap.parse_args()
    if args.insecure:
        SSL_CONTEXT = ssl._create_unverified_context()
    base = args.base.rstrip("/")
    attempts = max(1, args.attempts)
    checks = []
    for attempt in range(1, attempts + 1):
        checks = run(base, args.min_manifest_version)
        if all(c.ok for c in checks) or attempt == attempts:
            break
        print(f"production health attempt {attempt}/{attempts} failed; retrying", file=sys.stderr)
        time.sleep(max(0, args.retry_delay))
    if args.json:
        print(json.dumps([c.__dict__ for c in checks], ensure_ascii=False, indent=2))
    else:
        for c in checks:
            status = "PASS" if c.ok else "FAIL"
            print(f"[{status}] {c.name}: {c.detail}")
    if not all(c.ok for c in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
