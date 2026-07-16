#!/usr/bin/env python3
"""Generate reviewed SEO/GEO scenario-page drafts for Arcade Skill."""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

from local_review import run_local_review, write_review

ROOT = Path(__file__).resolve().parents[2]
KEYWORDS = ROOT / "scripts/growth/seo_keywords.json"
DEFAULT_OUT = ROOT / "growth/drafts/seo"
DEFAULT_REVIEW_OUT = ROOT / "growth/reports/seo-local-review-latest.md"
PUBLISH_ROOT = ROOT / "docs/scenarios"


def words(text):
    return re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", text.lower())


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


def scenario_sections(row):
    slug = row["slug"]
    if slug == "games-while-ai-agent-runs-tests":
        return [
            ("The test-run waiting room",
             "The best moment for Arcade Skill is not a lunch break or the end of the day. It is the awkward interval after a developer has asked an AI agent to run the boring part of the loop: install packages, regenerate a file, run unit tests, wait for a browser test suite, or inspect a long diff. The terminal is still the center of attention, but there is no useful human action for a minute or two. That is where a tiny browser arcade game belongs."),
            ("Why this beats opening a feed",
             "Social feeds are optimized to steal the whole session. A heavy game asks for commitment. Arcade Skill sits between those extremes. Down 100 Floors starts quickly, ends quickly, and returns the player to the coding context with a score instead of a lost afternoon. The design target is one more run, not one more hour."),
            ("A developer-shaped loop",
             "The installed skill keeps the mechanics small: a Python launcher, a manifest URL, sha256 verification, a local cache, and a browser window. The user can trigger it with plain language while Codex, Claude Code, or another agent keeps working. That makes the product feel like a sidecar for programming rather than a general arcade portal."),
            ("Measurement discipline",
             "This scenario page is useful only if it leads to real behavior. The telemetry loop watches deaths, session length, replay intent, share clicks, and support clicks. If players bounce before learning the controls, the fix is game feel. If they play but never share, the fix is the score loop. Search traffic is treated as product signal, not just page views."),
            ("Search phrases this page owns",
             "The language here is deliberately about CI pauses, Jest runs, Playwright retries, npm dependency installs, Python virtualenv rebuilds, package-lock churn, TypeScript checks, flaky assertions, local regression loops, green bars, terminal focus, pull-request review gaps, and the two-minute boredom that appears before a test suite finishes."),
            ("What a good session looks like",
             "A good session starts after the command is already running. The player opens the game, drops through a few platforms, maybe reaches a new floor, copies a score, then returns to the terminal when the agent is ready. No login, no loot box, no live-service calendar, no notification permission, no giant asset download."),
            ("Why the bundle matters",
             "The small verified bundle is part of the promise. A developer waiting on tests does not want another toolchain. The launcher checks the manifest, downloads a single HTML file, verifies the digest, and keeps a last-known-good cache. The technical shape supports the emotional goal: quick, trusted, disposable fun."),
        ]
    if slug == "claude-code-break-game":
        return [
            ("Claude Code has a rhythm",
             "Claude Code often creates a strange little pause: the agent is active, the human is nearby, and the work is not done yet. The player does not want a new project, a new tab spiral, or a modern game with accounts and notifications. They want a small cabinet next to the terminal, something that feels like it could have lived on an old web page or a feature phone."),
            ("Retro is the interface",
             "The nostalgic style is not decoration. It tells the user what kind of commitment is expected. Simple platforms, immediate failure, readable hazards, and a blunt score all say the same thing: this is a break between commands. You can lose in ten seconds, laugh at the miss, and go back to the diff."),
            ("Local-first trust",
             "The skill route opens a localhost browser session, so the product refuses to pretend that AdSense belongs there. Ads are for the hosted web version after review readiness. The skill channel uses Stripe support and sharing instead, which fits developers better than interruption-based monetization."),
            ("A clean maker story",
             "For GEO and community discovery, the honest explanation matters: Arcade Skill is a maker-built arcade toy for the Claude and Codex waiting room. It does not claim to replace real games and does not buy engagement with paid revives. That makes it suitable for transparent replies, awesome-list PRs, and build-in-public posts."),
            ("The Claude-specific promise",
             "Claude Code users already understand small rituals: read the plan, approve the change, wait for tests, inspect the diff, ask for a smaller patch. This page speaks to that cadence. The game is a pocket-sized intermission between review moments, closer to a desk toy than an entertainment platform."),
            ("Tone and presentation",
             "The copy should feel like a hacker found an old arcade cabinet inside a terminal window. Useful words here include patch review, local agent, repo context, terminal session, diff generation, dependency repair, lint pass, background run, thinking time, prompt loop, and command-line companion."),
            ("Monetization fit",
             "Claude Code users are sensitive to trust. The support link is positioned like a coffee button, not a pressure gate. Future supporter features should look like badges, early cabinets, cosmetic flourishes, or maker notes. The page avoids revive economics because that would turn a delightful wait into a transaction trap."),
        ]
    return [
        ("AI 编程代理带来的新空档",
         "以前写代码的等待时间通常来自编译、测试、依赖安装。现在多了一种更微妙的等待：你把任务交给 Codex、Claude Code 或其他 agent，它正在跑、正在想、正在改文件，而你暂时不该打断它。这个时间不长，却很容易被信息流吞掉。Arcade Skill 瞄准的就是这个缝隙。"),
        ("为什么是复古小游戏",
         "复古不是怀旧滤镜，而是一种产品约束。画面简单，规则立刻懂，失败很快发生，重开也没有负担。下 100 层这种玩法适合等测试的场景：左右移动、找平台、躲尖刺、看自己能下到第几层。它不需要账号、不需要教程，也不应该把你从工作流里拖走。"),
        ("技能壳和网页版分工",
         "本地技能运行在 localhost，负责快速打开游戏、校验 bundle、缓存可用版本；网页版负责承接分享、搜索、截图、介绍页和未来广告。这个分工很关键：localhost 不做 AdSense 幻觉，网页端才是公开增长和商业化实验的地方。"),
            ("公平和变现边界",
             "Stripe 打赏可以存在，支持者徽章可以以后做，但排行榜不能卖血量、不能卖复活、不能让付费者有分数优势。开发者愿意为一个有趣的小工具付钱，但不喜欢被挫败感勒索。这个边界会一直写进产品和文案。"),
            ("中文场景词",
             "这一页覆盖的不是泛泛的小游戏，而是等测试、等编译、等 agent 改代码、等依赖安装、等差异生成、等 lint、等 CI、等本地回归、等网页自动化测试、等终端输出、等模型思考这些开发者场景。关键词应该贴近工作流，而不是贴近游戏站。"),
            ("一次理想使用",
             "理想的一局很短：命令已经跑起来，用户打开小游戏，掉几层，躲几次尖刺，复制一个战绩，然后回到终端继续看结果。它不要求登录，不弹广告，不要你充值买命，也不会把工作时间改造成长时间娱乐。"),
            ("为什么适合中文开发者",
             "中文开发者同样在使用 Codex、Claude Code、本地 LLM、自动化脚本和各种 agent 工作流。这个产品的表达要像一个懂终端的人做的小玩具：轻、快、能分享、有一点复古味，但不装成大型游戏平台。"),
    ]


def tail_sections(row):
    slug = row["slug"]
    if slug == "games-while-ai-agent-runs-tests":
        return [
            ("Fair scoring during test waits",
             "In this context, score credibility is the product. If two developers compare runs while the same test suite is still running, the result has to mean something. Deeper floor wins, time breaks ties, and support payments must not add health, slow hazards, remove spikes, or change the daily seed."),
            ("How to use it with a test command",
             "Start the boring command first, then open the game: run the test suite, wait for the package install, or let the agent finish its verification step. Use the hosted page for sharing and the installed skill for a local sidecar. When the command finishes, close the tab and go back to the terminal."),
            ("FAQ: test-run edition",
             "Use this page when the query is about games during tests, CI waiting time, dependency install boredom, or small browser games for developers. Do not use it for broad gaming keywords; the intent is programming downtime."),
        ]
    if slug == "claude-code-break-game":
        return [
            ("Fair scoring for Claude users",
             "The Claude Code audience will notice if the rules are crooked. Support can fund the maker, but it cannot buy a better run. That keeps the product closer to an open-source utility than a mobile monetization funnel."),
            ("How to use it with Claude Code",
             "Ask Claude to run tests or inspect a change, then open Arcade Skill while the agent works. The best session is short enough to fit between approval checkpoints: one run, maybe two, then back to reading the patch."),
            ("FAQ: Claude edition",
             "Use this page for Claude Code, Claude skills, agent-side tools, and terminal companion searches. The claim is narrow: Arcade Skill is a retro break for the agent waiting room, not a replacement for full games or project management tools."),
        ]
    return [
        ("中文排行榜公平性",
         "中文用户同样会在意排行榜是否可信。打赏可以支持作者，不能购买更高血量、不能购买复活、不能降低尖刺难度，也不能改变每日种子。能比较，才有人愿意分享战绩。"),
        ("如何配合 agent 使用",
         "先让 agent 开始工作：跑测试、装依赖、改文件、生成 diff。然后打开 Arcade Skill 玩一两局。命令结束后回到终端继续看结果。这个流程应该像喝一口水一样轻，而不是打开另一个大型娱乐入口。"),
        ("FAQ：中文场景",
         "这一页适合承接中文搜索里的 AI 编程代理等待、Codex 小游戏、Claude Code 等测试、开发者复古小游戏等意图。不追泛娱乐大词，不冒充 4399 式游戏站。"),
    ]


def render_page(row):
    title = row["title"]
    keyword = row["keyword"]
    intent = row["intent"]
    datapoint = row["datapoint"]
    generated = dt.date.today().isoformat()
    language_note = "This page is written for developer search intent." if row["locale"] == "en" else "这一页面向正在等待 AI 编程代理完成任务的开发者。"
    sections = "\n".join(
        f"  <h2>{heading}</h2>\n  <p>{body}</p>"
        for heading, body in scenario_sections(row)
    )
    tail = "\n".join(
        f"  <h2>{heading}</h2>\n  <p>{body}</p>"
        for heading, body in tail_sections(row)
    )
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
{sections}
{tail}
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
        if other_path.name == "index.html" and other_path.parent.name == path.parent.name:
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
    ap.add_argument(
        "--no-llm-review",
        action="store_true",
        help="skip the default local-only SEO review",
    )
    ap.add_argument("--review-out", type=Path, default=DEFAULT_REVIEW_OUT)
    args = ap.parse_args()

    rows = json.loads(args.keywords.read_text(encoding="utf-8"))
    out_dir = PUBLISH_ROOT if args.publish else args.out_dir
    existing = load_existing_texts()
    report = []
    generated_pages = []
    generated_outputs = []
    failed = False
    for row in rows:
        text = render_page(row)
        path = out_dir / row["slug"] / "index.html"
        checks, count, sim, sim_path = qc_page(path, text, row["datapoint"], existing)
        status = "PASS" if all(checks.values()) else "FAIL"
        failed = failed or status == "FAIL"
        generated_pages.append(f"## {row['title']}\n\n{text}")
        report.append({
            "status": status,
            "path": str(path),
            "words": count,
            "max_jaccard": round(sim, 3),
            "similar_to": str(sim_path) if sim_path else "",
            "checks": checks,
        })
        generated_outputs.append((path, text))

    for row in report:
        print(json.dumps(row, ensure_ascii=False))
    if not args.no_llm_review:
        review_input = (
            "Deterministic QC:\n"
            + json.dumps(report, ensure_ascii=False, indent=2)
            + "\n\nGenerated scenario pages:\n"
            + "\n\n".join(generated_pages)
        )
        result = run_local_review("seo", review_input, max_tokens=800)
        write_review(args.review_out, "Local LLM SEO Review", result)
        print(f"local review: {result.get('status')} -> {args.review_out}")
        failed = failed or result.get("status") != "PASS"
    if failed:
        raise SystemExit("SEO gate failed: deterministic QC or local LLM review unavailable")
    if not args.dry_run:
        for path, text in generated_outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
