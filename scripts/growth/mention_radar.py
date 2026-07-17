#!/usr/bin/env python3
"""Find human-reviewed Arcade Skill growth opportunities.

Radar is automated; publishing is not. This script fetches or reads public
items, scores them, and writes reply/list-target cards for a person to approve.
"""
import argparse
import datetime as dt
import html
import json
import re
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from local_review import append_review, run_local_review

ROOT = Path(__file__).resolve().parents[2]
KEYWORDS = ROOT / "scripts/growth/radar_keywords.json"
DEFAULT_OUT = ROOT / "growth/radar/radar-latest.md"
DEFAULT_SAMPLE = ROOT / "scripts/growth/radar_sample.json"
WARNINGS = []
SSL_CONTEXT = None


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_json(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers={"User-Agent": "arcade-skill-radar/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_text(url: str, timeout: int = 15):
    req = urllib.request.Request(url, headers={"User-Agent": "arcade-skill-radar/1.0"})
    with urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def norm_item(source, title, url, text=""):
    return {
        "source": source,
        "title": html.unescape(str(title or "")).strip(),
        "url": str(url or "").strip(),
        "text": html.unescape(str(text or "")).strip(),
    }


def fetch_hn(query: str, limit: int):
    params = urllib.parse.urlencode({
        "query": query,
        "tags": "story,comment",
        "hitsPerPage": min(limit, 20),
    })
    data = fetch_json(f"https://hn.algolia.com/api/v1/search?{params}")
    out = []
    for hit in data.get("hits", [])[:limit]:
        title = hit.get("title") or hit.get("story_title") or hit.get("comment_text", "")
        url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        out.append(norm_item("hn", title, url, hit.get("comment_text", "")))
    return out


def fetch_reddit(subreddit: str, limit: int):
    xml = fetch_text(f"https://www.reddit.com/r/{subreddit}/search.rss?q=claude%20codex%20agent&restrict_sr=1&sort=new")
    root = ET.fromstring(xml)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    out = []
    for entry in root.findall("atom:entry", ns)[:limit]:
        title = entry.findtext("atom:title", default="", namespaces=ns)
        link = entry.find("atom:link", ns)
        url = link.attrib.get("href", "") if link is not None else ""
        text = entry.findtext("atom:content", default="", namespaces=ns)
        out.append(norm_item(f"reddit/r/{subreddit}", title, url, re.sub("<[^>]+>", " ", text)))
    return out


def fetch_github(query: str, limit: int):
    params = urllib.parse.urlencode({"q": query, "per_page": min(limit, 10)})
    data = fetch_json(f"https://api.github.com/search/repositories?{params}")
    out = []
    for repo in data.get("items", [])[:limit]:
        out.append(norm_item(
            "github",
            repo.get("full_name", ""),
            repo.get("html_url", ""),
            repo.get("description", ""),
        ))
    return out


def load_items(args):
    if args.sample:
        return [norm_item(i.get("source"), i.get("title"), i.get("url"), i.get("text")) for i in read_json(args.sample)]
    if args.offline:
        return [norm_item(i.get("source"), i.get("title"), i.get("url"), i.get("text")) for i in read_json(DEFAULT_SAMPLE)]
    items = []
    for q in args.hn_query:
        try:
            items.extend(fetch_hn(q, args.limit))
        except Exception as exc:
            WARNINGS.append(f"HN query failed ({q}): {exc}")
    for sub in args.reddit:
        try:
            items.extend(fetch_reddit(sub, args.limit))
        except Exception as exc:
            WARNINGS.append(f"Reddit source failed ({sub}): {exc}")
    for q in args.github_query:
        try:
            items.extend(fetch_github(q, args.limit))
        except Exception as exc:
            WARNINGS.append(f"GitHub query failed ({q}): {exc}")
    return items


def score_item(item, cfg):
    hay = f"{item['title']} {item['text']}".lower()
    if any(term.lower() in hay for term in cfg["negative_terms"]):
        return "IGNORE", 0, "negative term"
    if any(term.lower() in hay for term in cfg["product_terms"]):
        return "REPLY_WORTHY", 95, "already mentions Arcade Skill"
    reply_hits = [t for t in cfg["reply_terms"] if t.lower() in hay]
    list_hits = [t for t in cfg["list_terms"] if t.lower() in hay]
    if reply_hits and ("agent" in hay or "claude" in hay or "codex" in hay):
        return "REPLY_WORTHY", min(90, 50 + 10 * len(reply_hits)), ", ".join(reply_hits[:3])
    if list_hits and ("skill" in hay or "codex" in hay or "claude" in hay or "agent" in hay):
        return "LIST_TARGET", min(85, 45 + 10 * len(list_hits)), ", ".join(list_hits[:3])
    return "IGNORE", 10, "weak match"


def draft_reply(item):
    return (
        "Transparent maker reply angle: this is exactly the idle-time gap Arcade "
        "Skill targets. Mention it as a tiny local/hosted arcade break for Codex "
        "or Claude waits, link the hosted demo, and disclose maker status."
    )


def write_report(items, out: Path):
    cfg = read_json(KEYWORDS)
    scored = []
    seen = set()
    for item in items:
        key = item["url"].rstrip("/").lower() or f"{item['source']}:{item['title'].lower()}"
        if key in seen:
            continue
        seen.add(key)
        label, score, reason = score_item(item, cfg)
        scored.append({**item, "label": label, "score": score, "reason": reason})
    scored.sort(key=lambda x: (x["label"] == "IGNORE", -x["score"], x["source"]))
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Arcade Skill Mention Radar",
        "",
        f"Generated: {dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        "Rule: radar is automated; every reply, PR, or post requires human review.",
        "",
    ]
    if WARNINGS:
        lines.extend(["## Source Warnings", ""])
        for warning in WARNINGS:
            lines.append(f"- {warning}")
        lines.append("")
    lines.extend([
        "| Label | Score | Source | Opportunity | Reason |",
        "| --- | ---: | --- | --- | --- |",
    ])
    for row in scored:
        title = row["title"].replace("|", " ")
        reason = row["reason"].replace("|", " ")
        lines.append(f"| {row['label']} | {row['score']} | {row['source']} | [{title}]({row['url']}) | {reason} |")
    lines.extend(["", "## Draft Cards", ""])
    for row in scored:
        if row["label"] == "IGNORE":
            continue
        lines.extend([
            f"### {row['label']}: {row['title']}",
            "",
            f"- URL: {row['url']}",
            f"- Score: {row['score']}",
            f"- Why: {row['reason']}",
            f"- Suggested angle: {draft_reply(row)}",
            "",
        ])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)
    return scored


def review_payload(scored):
    candidates = [row for row in scored if row["label"] != "IGNORE"][:12]
    return json.dumps(
        [
            {
                "label": row["label"],
                "score": row["score"],
                "source": row["source"],
                "title": row["title"][:240],
                "url": row["url"],
                "reason": row["reason"],
            }
            for row in candidates
        ],
        ensure_ascii=False,
        indent=2,
    )


def main():
    global SSL_CONTEXT
    ap = argparse.ArgumentParser(description="Arcade Skill mention radar")
    ap.add_argument("--offline", action="store_true", help="use bundled sample data")
    ap.add_argument("--insecure", action="store_true", help="network smoke test only: skip TLS verification")
    ap.add_argument("--sample", type=Path, help="read public items from JSON")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--no-llm-review",
        action="store_true",
        help="skip the default local-only opportunity review",
    )
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--hn-query", action="append", default=[
        "Claude Code waiting tests",
        "Codex coding agent terminal game",
    ])
    ap.add_argument("--reddit", action="append", default=["ClaudeAI", "LocalLLaMA"])
    ap.add_argument("--github-query", action="append", default=[
        "awesome codex skills",
        "awesome claude skills",
    ])
    args = ap.parse_args()
    if args.insecure:
        SSL_CONTEXT = ssl._create_unverified_context()
        WARNINGS.append("TLS verification was disabled for this smoke test.")
    items = load_items(args)
    if not items:
        raise SystemExit("no radar items found")
    scored = write_report(items, args.out)
    if not args.no_llm_review:
        result = run_local_review(
            "radar",
            review_payload(scored),
            max_tokens=550,
        )
        append_review(args.out, "Local LLM Opportunity Review", result)
        print(f"local review: {result.get('status')}")


if __name__ == "__main__":
    main()
