#!/usr/bin/env python3
"""Generate reviewed SEO/GEO scenario-page drafts for Arcade Skill."""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KEYWORDS = ROOT / "scripts/growth/seo_keywords.json"
DEFAULT_OUT = ROOT / "growth/drafts/seo"
PUBLISH_ROOT = ROOT / "docs/scenarios"


def words(text):
    return re.findall(r"[\w\u4e00-\u9fff]+", text.lower())


def jaccard(a, b):
    sa, sb = set(words(a)), set(words(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def faq_schema(title):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"What is {title}?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "Arcade Skill is a tiny retro browser arcade break designed for developers waiting on coding agents, test runs, installs, or builds."
                }
            },
            {
                "@type": "Question",
                "name": "Does Arcade Skill show ads in localhost skill sessions?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "No. Localhost skill sessions keep ads disabled. Ads, if enabled later, belong only on the hosted arcade.fxpeek.com web version."
                }
            },
            {
                "@type": "Question",
                "name": "Can supporters buy leaderboard advantage?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "No. Stripe support and future supporter perks must not change ranked health, revives, or scoring."
                }
            }
        ]
    }


def render_page(row):
    title = row["title"]
    keyword = row["keyword"]
    intent = row["intent"]
    datapoint = row["datapoint"]
    generated = dt.date.today().isoformat()
    language_note = "This page is written for developer search intent." if row["locale"] == "en" else "这一页面向正在等待 AI 编程代理完成任务的开发者。"
    body = f"""<!doctype html>
<html lang="{row['locale']}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Arcade Skill</title>
  <meta name="description" content="{title}: a retro arcade break for Codex, Claude Code, and coding-agent wait time.">
  <script type="application/ld+json">{json.dumps(faq_schema(title), ensure_ascii=False)}</script>
</head>
<body>
<main>
  <p><a href="/">Arcade Skill</a> / <a href="/play/">Play</a> / <a href="/support/">Support</a></p>
  <h1>{title}</h1>
  <p><strong>Search intent:</strong> {intent}</p>
  <p><strong>Real datapoint:</strong> {datapoint}</p>
  <p><strong>Keyword focus:</strong> {keyword}</p>
  <p>{language_note}</p>
  <h2>The waiting-room problem</h2>
  <p>Modern coding agents changed the rhythm of programming. A developer asks Codex, Claude Code, or another assistant to install dependencies, run tests, inspect diffs, or regenerate code. For the next few minutes the human is present but not fully occupied. Opening a social feed breaks attention. Starting a large game is too heavy. Arcade Skill targets that narrow gap: a quick, local-first, retro-feeling arcade loop that ends before the agent has forgotten why it was working.</p>
  <p>The first game, Down 100 Floors, uses a tiny falling-platform challenge: move left and right, land on platforms, avoid spikes, and try to reach a deeper floor than last time. The character is intentionally simple and readable, closer to a nostalgic terminal toy than a modern gacha product. That is the point. The game should feel like something a developer can launch between test runs without guilt.</p>
  <h2>Why it is different from a generic browser-game portal</h2>
  <p>Arcade Skill is distributed as an agent skill and as a hosted web page. The installed skill opens a verified bundle through a thin Python loader. The loader fetches a manifest, checks sha256, swaps the local cache atomically, and falls back to the last good version when a network or hash check fails. This means new games, copy changes, support links, emergency notices, and kill switches can ship without asking every installed user to download a new package.</p>
  <p>The hosted version exists for sharing, search, screenshots, ranking, and future web-only ads. The local skill version deliberately keeps AdSense disabled because localhost sessions are not a real ad surface. That separation protects trust with developers and keeps the product honest: the installed skill is a tiny break and acquisition loop, while the public website is where discoverability and monetization experiments belong.</p>
  <h2>Fair-play rule</h2>
  <p>The ranking model is simple. Deeper floor wins. Time breaks ties. Stripe support, sponsorship, or future supporter perks must never buy health, revives, or leaderboard advantage. That rule matters because the social loop depends on score credibility. A nostalgic arcade challenge loses its charm the moment payment changes the run.</p>
  <h2>How to use it</h2>
  <p>Use the hosted route when you want to share a score or test the game immediately: <a href="/play/">arcade.fxpeek.com/play</a>. Use the skill package when you want your coding agent to open a quick local arcade break while it works. The ideal invocation is plain language: tell your agent that you are waiting on tests and want a quick game.</p>
  <h2>Frequently asked questions</h2>
  <h3>Is this for serious gaming?</h3>
  <p>No. It is a short-break arcade toy for developer wait time. The win condition is not hours of retention; it is a clean two-minute loop that does not derail the work session.</p>
  <h3>Does it collect telemetry?</h3>
  <p>Telemetry is used to understand game balance and growth loops: death floor, session length, share clicks, and support clicks. The roadmap keeps publishing and outreach human-reviewed.</p>
  <h3>Generated</h3>
  <p>{generated}. This draft is safe to review, edit, and publish through the normal repo flow.</p>
</main>
</body>
</html>
"""
    return body


def load_existing_texts():
    texts = []
    for folder in [ROOT / "docs", ROOT / "growth/drafts/seo"]:
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if path.suffix.lower() in {".html", ".md", ".txt"}:
                texts.append((path, path.read_text(encoding="utf-8", errors="ignore")))
    return texts


def qc_page(path: Path, text: str, datapoint: str, existing):
    plain = re.sub("<[^>]+>", " ", text)
    count = len(words(plain))
    max_sim = 0.0
    max_path = None
    for other_path, other_text in existing:
        if other_path == path:
            continue
        sim = jaccard(plain, re.sub("<[^>]+>", " ", other_text))
        if sim > max_sim:
            max_sim, max_path = sim, other_path
    checks = {
        "word_count": count >= 600,
        "datapoint": datapoint in text,
        "faq_schema": '"@type": "FAQPage"' in text,
        "jaccard_lt_0_40": max_sim < 0.40,
    }
    return checks, count, max_sim, max_path


def main():
    ap = argparse.ArgumentParser(description="Arcade SEO page factory")
    ap.add_argument("--keywords", type=Path, default=KEYWORDS)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--publish", action="store_true", help="write pages under docs/scenarios")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows = json.loads(args.keywords.read_text(encoding="utf-8"))
    out_dir = PUBLISH_ROOT if args.publish else args.out_dir
    existing = load_existing_texts()
    report = []
    failed = False
    for row in rows:
        text = render_page(row)
        path = out_dir / row["slug"] / "index.html"
        checks, count, sim, sim_path = qc_page(path, text, row["datapoint"], existing)
        status = "PASS" if all(checks.values()) else "FAIL"
        failed = failed or status == "FAIL"
        report.append({
            "status": status,
            "path": str(path),
            "words": count,
            "max_jaccard": round(sim, 3),
            "similar_to": str(sim_path) if sim_path else "",
            "checks": checks,
        })
        if not args.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    for row in report:
        print(json.dumps(row, ensure_ascii=False))
    if failed:
        raise SystemExit("SEO QC failed")


if __name__ == "__main__":
    main()
