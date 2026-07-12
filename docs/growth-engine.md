# Arcade Growth Engine

The growth model has three layers:

1. Traditional search: focused landing pages, multilingual intros, and clear
   canonical project files.
2. GEO: earn third-party mentions that AI engines can cite.
3. Agent runtime: make the skill easy for coding agents to invoke when users
   are waiting on tests, installs, builds, or diffs.

The operating model has two tiers:

- Tier A owned surfaces can publish unattended after deterministic linter,
  idempotency, rate-limit, live-check, and rollback gates pass.
- Tier B third-party replies, issues, and pull requests remain one-click
  approved before sending.

## Weekly Runbook

```bash
python3 scripts/growth/growth_smoke.py
```

This offline suite is also scheduled in GitHub Actions. It does not touch
external communities and does not require production credentials.

Mac-local Tier A jobs keep Telegram, local LLM, Cloudflare, and browser-session
credentials on the Mac mini:

```bash
python3 scripts/install_tier_a_launchd.py --install
python3 scripts/growth/tier_a_runner.py health
```

The installer defines: SoM Monday, SEO Wednesday, weekly telemetry Sunday,
production health every six hours, and owned-channel queue polling every five
minutes.

Production health is separate:

```bash
python3 scripts/production_health.py
```

It verifies public pages, sitemap, manifest JSON, Stripe support routing,
localhost-safe ads flags, and bundle sha256 hashes.

## Local LLM Default

Before using a paid API for copy, SEO/GEO review, radar classification, or
weekly summaries, use the local router:

```bash
python3 scripts/local_llm.py design-review --input docs/scenarios/index.html
python3 scripts/local_llm.py seo --input docs/scenarios/games-while-ai-agent-runs-tests/index.html
```

If the local route is unavailable, record `LOCAL_LLM_PENDING` or
`LOCAL_LLM_UNAVAILABLE`; do not silently fallback to a paid API.

P1 and P2 invoke the local review layer by default after deterministic scoring
and quality gates. Use `--no-llm-review` only when intentionally testing the
deterministic path in isolation.

For a live radar pull, run:

```bash
python3 scripts/growth/mention_radar.py \
  --out growth/radar/radar-latest.md
```

## Status Matrix

| Pipeline | Script | Output | Automation boundary |
| --- | --- | --- | --- |
| P1 mention radar | `scripts/growth/mention_radar.py` | `growth/radar/radar-latest.md` | Finds opportunities only; replies and PRs are manual. |
| P2 SEO factory | `scripts/growth/seo_page_factory.py` | `growth/drafts/seo/*/index.html` | Drafts pages only; use `--publish` after review. |
| P3 leaderboard digest | `scripts/growth/leaderboard_digest.py` | disabled | Remains off until a production global ranking exists. |
| P4 Share of Model | `scripts/growth/som_tracker.py` | `growth/reports/som-latest.md` | Scores approved/exported answers. |
| P5 telemetry | `scripts/growth/telemetry_report.py` | `growth/reports/telemetry-latest.md` | Reads production D1 metrics. |

## P1: Mention Radar

Use the radar to find moments where a transparent maker reply is relevant:
developer wait-time threads, Claude/Codex skill lists, awesome repositories, and
"what do you do while tests run" discussions.

```bash
python3 scripts/growth/mention_radar.py \
  --out growth/radar/radar-latest.md
```

The script reads public sources and scores them into:

- `REPLY_WORTHY`: someone already has the problem; reply as the maker.
- `LIST_TARGET`: a directory or awesome list may accept a PR.
- `IGNORE`: weak fit or unsafe context.

No account action is automated.

## P2: Scenario Page Factory

Generate reviewed SEO/GEO page drafts from `scripts/growth/seo_keywords.json`.

```bash
python3 scripts/growth/seo_page_factory.py
```

Quality gates:

- at least 600 tokenized words
- real datapoint present
- FAQPage schema present
- maximum Jaccard similarity below 0.40

After human review:

```bash
python3 scripts/growth/seo_page_factory.py --publish
python3 scripts/build_manifest.py
```

## P3: Leaderboard Digest (Disabled)

The script can be tested with bundled sample data, but public output remains
disabled by `config/tier-a-policy.json` until global ranking is live:

```bash
python3 scripts/growth/leaderboard_digest.py
```

After ranking is wired, pass a production export:

```bash
python3 scripts/growth/leaderboard_digest.py \
  --input growth/leaderboard/latest.json \
  --out growth/drafts/leaderboard-latest.md
```

The output includes a Top 10 table plus English and Chinese social drafts. It
must be reviewed for privacy before publishing.

## P4: Share Of Model

SoM is the weekly GEO KPI. Run a fixed prompt set across target AI engines and
record whether Arcade Skill is mentioned and cited.

```bash
python3 scripts/growth/som_tracker.py init
python3 scripts/growth/som_tracker.py score \
  --input growth/som_responses.jsonl \
  --out growth/reports/som-latest.md
```

Fill `growth/som_responses.jsonl` manually or from approved exports. Do not
auto-post or scrape logged-in answers without review.

The scorer reports coverage separately and refuses to count empty answers as
misses. A missing engine export is `PENDING`, not a synthetic 0% mention rate.

## P5: Telemetry回流

Use D1 event data to answer:

- where players die
- whether daily mode is used
- whether share and Stripe support hooks fire
- whether hosted web traffic is replacing local-only usage

```bash
npx wrangler d1 execute arcade_telemetry \
  --remote \
  --file scripts/growth/telemetry_summary.sql
```

For a Markdown report:

```bash
python3 scripts/growth/telemetry_report.py \
  --out growth/reports/telemetry-latest.md
```

## Public AI Hints

The site publishes:

- `/robots.txt`
- `/sitemap.xml`
- `/llms.txt`
- `/ai.txt`
- `/about/`
- `/docs/project-intro.md`
- multilingual intros under `/docs/intro.*.md`

These files are descriptive, not spam pages. Third-party mentions remain the
main GEO fuel.
