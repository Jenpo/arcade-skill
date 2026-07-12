#!/usr/bin/env python3
"""Deterministic safety gate for Tier A owned-channel publishing."""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / "config/tier-a-policy.json"

CREDENTIAL_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"), "possible API key"),
    (re.compile(r"\bgh[opurs]_[A-Za-z0-9]{20,}\b"), "possible GitHub token"),
    (re.compile(r"\bBearer\s+[A-Za-z0-9._~-]{16,}\b", re.I), "possible bearer token"),
    (re.compile(r"\b(?:api[_-]?key|token|password|secret)\s*[=:]\s*\S+", re.I), "possible credential assignment"),
]
URL_PATTERN = re.compile(r"https?://[^\s<>()\[\]{}]+", re.I)


def load_policy(path=DEFAULT_POLICY):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def lint_text(text, channel, policy=None):
    policy = policy or load_policy()
    errors = []
    channel_policy = policy.get("channels", {}).get(channel)
    if not channel_policy:
        errors.append(f"unsupported channel: {channel}")
    else:
        limit = int(channel_policy.get("max_chars", 0))
        if limit and len(text) > limit:
            errors.append(f"text length {len(text)} exceeds {channel} limit {limit}")
    if not text.strip():
        errors.append("text is empty")
    for item in policy.get("blocked_claims", []):
        if re.search(item["pattern"], text, re.I):
            errors.append(f"blocked claim: {item['reason']}")
    for pattern, reason in CREDENTIAL_PATTERNS:
        if pattern.search(text):
            errors.append(reason)
    allowed = {host.lower() for host in policy.get("allowed_hosts", [])}
    for raw_url in URL_PATTERN.findall(text):
        host = (urlparse(raw_url.rstrip(".,;!?")).hostname or "").lower()
        if host not in allowed:
            errors.append(f"external host is not allowed: {host or raw_url}")
    return sorted(set(errors))


def main():
    ap = argparse.ArgumentParser(description="Arcade Tier A content linter")
    ap.add_argument("--channel", required=True, choices=["x", "jike"])
    ap.add_argument("--input", type=Path, help="text file; defaults to stdin")
    ap.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    text = args.input.read_text(encoding="utf-8") if args.input else sys.stdin.read()
    errors = lint_text(text, args.channel, load_policy(args.policy))
    result = {"status": "PASS" if not errors else "BLOCKED", "channel": args.channel, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result["status"])
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
