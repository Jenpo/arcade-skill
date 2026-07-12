#!/usr/bin/env python3
"""Wait for a public manifest endpoint to reach an expected version."""
import argparse
import json
import time
import urllib.request


def fetch_version(url):
    req = urllib.request.Request(url, headers={"User-Agent": "arcade-manifest-wait/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data.get("manifest_version", ""))


def main():
    ap = argparse.ArgumentParser(description="Wait for Arcade manifest version")
    ap.add_argument("--url", required=True)
    ap.add_argument("--minimum", required=True)
    ap.add_argument("--attempts", type=int, default=12)
    ap.add_argument("--retry-delay", type=int, default=10)
    args = ap.parse_args()
    last = ""
    for attempt in range(1, max(1, args.attempts) + 1):
        try:
            last = fetch_version(args.url)
            if last >= args.minimum:
                print(f"manifest ready: {last} >= {args.minimum}")
                return
        except Exception as exc:
            last = str(exc)
        if attempt < args.attempts:
            time.sleep(max(0, args.retry_delay))
    raise SystemExit(f"manifest not ready: last={last!r} minimum={args.minimum!r}")


if __name__ == "__main__":
    main()
