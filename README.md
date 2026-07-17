# Arcade Skill

## Languages

[中文](docs/intro.zh.md) · [English](docs/intro.en.md) · [Français](docs/intro.fr.md) · [Italiano](docs/intro.it.md) · [العربية](docs/intro.ar.md)

An old-school browser arcade break for the age of coding agents.

When Claude Code, Codex, or another agent is compiling, installing, testing, or
thinking very hard, Arcade Skill opens a tiny nostalgic game in your browser:
fast to launch, easy to lose, annoyingly tempting to replay.

![Arcade Skill running beside a coding-agent session](docs/assets/screenshots/codex-claude-demo.svg)

## Quick Links

[Play hosted web version](https://arcade.fxpeek.com/play/) ·
[Daily challenge](https://arcade.fxpeek.com/play/?daily=1) ·
[Support via Stripe](https://arcade.fxpeek.com/support/) ·
[Download arcade.skill](https://github.com/Jenpo/arcade-skill/releases/latest) ·
[View manifest](https://arcade.fxpeek.com/manifest.json) ·
[llms.txt](https://arcade.fxpeek.com/llms.txt) ·
[Design notes](docs/DESIGN.md) ·
[Awesome Design MD proposal](docs/awesome-design-md-proposal.md) ·
[Local LLM policy](docs/local-llm-policy.md) ·
[Review action matrix](docs/review-action-matrix.md)

## Strategy

Arcade Skill is not trying to be another generic web games portal. The wedge is
specific: **your coding agent is working, so you get a tiny arcade break**.

The product has two channels:

| Channel | Where it runs | Job | Monetization |
| --- | --- | --- | --- |
| Skill | `127.0.0.1` local browser | Delight developers during agent wait time | Tips, share loop, future supporter perks |
| Hosted web | `arcade.fxpeek.com/play` | Receive shared scores and public traffic | Future AdSense, ranking, Stripe supporter flow |

Skill sessions force ads off because AdSense does not fill localhost. Ads belong
only on the hosted web surface.

## Play Modes

- **Normal run:** random quick break for agent wait time.
- **Daily challenge:** one shared date seed per day, so friends play the same
  shaft and can compare scores from the share link.
- **Ranked direction:** global ranking will separate normal and daily runs, with
  floor reached as the primary score and time as the tie-breaker.

## Payment And Support

The payment strategy is intentionally trust-first:

- **Stripe support now:** the repo, hosted play page, and game-over screen point
  to the Stripe support route. The final `buy.stripe.com` link can be swapped in
  through the manifest after account review.
- **Stripe later:** Pro is reserved for cosmetics, early access, supporter
  badges, or cloud features after real usage signal. No paid power.
- **Ads later:** AdSense can be enabled on the hosted web version after the site
  has enough content and review readiness. Local skill sessions stay ad-free.

Current support link:

> https://arcade.fxpeek.com/support/

## Ranking And Fair Play

The current release stores a local best score. Global ranking is planned, but
ranked mode must stay clean:

- Primary rank: deepest floor reached.
- Tie-breaker: faster time at the same floor.
- No paid health.
- No paid revives.
- No leaderboard advantage from Stripe, ads, or sponsorship.

The telemetry hook and Cloudflare Worker + D1 receiver are live. They capture
death floor, session length, replay rate, share clicks, and tip clicks.

## Project Intro

More launch copy, screenshots, positioning notes, and gallery assets live in
[docs/project-intro.md](docs/project-intro.md).

## Growth Measurement

Arcade Skill tracks growth through five measurement and draft loops:

- **P1 Mention radar:** public HN, Reddit, and GitHub opportunities are scored
  with `scripts/growth/mention_radar.py`; every reply or PR stays manual.
- **P2 Scenario page factory:** reviewed SEO/GEO page drafts come from
  `scripts/growth/seo_page_factory.py`.
- **P3 Leaderboard digest:** disabled in `config/tier-a-policy.json` until a
  production global ranking exists; sample data is test-only.
- **P4 Share of Model:** weekly prompt checks across AI engines are scored with
  `scripts/growth/som_tracker.py`.
- **P5 Telemetry feedback:** D1 event summaries from
  `scripts/growth/telemetry_summary.sql` or a Markdown report from
  `scripts/growth/telemetry_report.py`.

The public AI context files are `llms.txt` and `ai.txt`. They are generated into
the production root during `scripts/build_manifest.py`.

One-command local growth smoke test:

```bash
python3 scripts/growth/growth_smoke.py
```

The same offline suite runs in `.github/workflows/growth-smoke.yml` on pushes,
pull requests, manual dispatch, and a daily schedule.

Production health check:

```bash
python3 scripts/production_health.py
```

`.github/workflows/production-health.yml` runs the same read-only checks every
six hours: public routes, sitemap, manifest, Stripe support routing, ads flag,
and bundle sha256 verification.

The deploy workflow verifies the exact new manifest on the GitHub Pages
fallback. Production `arcade.fxpeek.com` remains a Cloudflare Pages deployment
from the Mac release command, followed by a strict minimum-version production
health check. Cloudflare credentials are not copied into GitHub.

Visual regression check:

```bash
npm ci
npx playwright install chromium
npm run test:visual
```

The Playwright suite captures `/scenarios/` at 1440x900 and 390x844, checks
overflow, mobile cabinet order, the pixel player, and keyboard focus, then
compares both pages with committed pixel baselines. CI uploads diff images from
`growth/reports/visual` when a threshold is exceeded.

Tier A owned-channel automation is guarded by
`config/tier-a-policy.json`: at most three posts per day, no unreleased ranking
or payment claims, no credential-shaped text, and only approved link hosts.
`scripts/growth/own_channel_publisher.py` is idempotent and emits Telegram
live-check receipts with rollback callback data. Third-party community replies
and repository submissions never enter this automatic publisher.

Live-check uses a dedicated Telegram bot. A site rollback button reverts the
Cloudflare Pages production deployment and queues the matching GitHub Pages
fallback rollback; callbacks are restricted to one chat and an explicit user
allowlist. Configure it without exposing secrets:

```bash
python3 scripts/provision_live_check.py configure
python3 scripts/provision_live_check.py check
```

Tier A schedules run through Mac LaunchAgents. Local LLM, X browser, and
Cloudflare deployment credentials stay on the Mac mini. The dedicated bot token
is stored only in the Mac mode-`0600` env, Cloudflare Worker secrets, and GitHub
Actions secrets so the same bot owns both messages and callbacks. Install the
jobs with:

```bash
python3 scripts/install_artifact_layout.py
python3 scripts/install_tier_a_launchd.py --install
python3 scripts/growth/tier_a_audit.py --days 7
```

The artifact installer keeps source code on the Mac and links generated SoM
inputs, reports, drafts, queues, state, radar results, and smoke output into the
current standard run under `/Volumes/S/Workplace/Codex-Workdir/arcade-skill/`.
It fails closed when the S volume is unavailable. Set `ARCADE_ARTIFACT_ROOT`
only when rotating the standard run directory.

The installer keeps the AC-powered scheduler awake and records append-only
task evidence under `~/Library/Logs/arcade-skill/`. A seven-day PASS requires
continuous launchd evidence; manual runs do not count.

## Local LLM Default

Ops tasks are local-first. Use `scripts/local_llm.py` for design review, copy,
SEO/GEO critique, radar classification, and weekly summaries. It reads the
local LiteLLM router key from environment variables and never silently falls
back to a paid API.

```bash
python3 scripts/local_llm.py design-review --input docs/scenarios/index.html
```

See [docs/local-llm-policy.md](docs/local-llm-policy.md).

## Screenshots

| Game menu | In game |
| --- | --- |
| ![Down 100 Floors start screen](docs/assets/screenshots/tower100-menu.svg) | ![Down 100 Floors gameplay](docs/assets/screenshots/tower100-run.svg) |

## What It Does

- Opens **Down 100 Floors** from a Claude/Codex skill command.
- Feels like a tiny Flash-era / feature-phone arcade game, but ships as a
  verified single-file HTML bundle.
- Uses zero-asset WebAudio for landing, damage, death, and chiptune BGM.
- Keeps the installed skill thin: Python launcher, manifest fetch, sha256 check,
  local cache, browser open.
- Ships new games, sponsor links, ads switches, notices, and kill switches
  through `https://arcade.fxpeek.com/manifest.json`.
- Works offline through a seed bundle and cached verified bundles. Loader v1.2
  also retries verified bundle mirrors on GitHub Pages, raw GitHub, and
  jsDelivr when the primary bundle host is unavailable.
- Uses original game code and art. No copied third-party source or assets.

## Install

Install the packaged `arcade.skill` from Releases, or copy the `skill/` folder
into your local skills directory. Then ask your coding agent:

> I'm waiting on tests. Open a quick game.

## Play Standalone

```bash
python3 skill/scripts/launcher.py            # zh UI
python3 skill/scripts/launcher.py --lang en  # en UI
```

Controls: arrow keys, A/D, or tap the left/right half of the screen. The loop is
deliberately retro: fall, panic, miss a platform, say “one more run.”

## Repo Layout

```text
skill/            distributable skill: SKILL.md, launcher, seed bundle
games/tower100/   game source: single self-contained HTML file
scripts/          build_manifest.py: hash bundles and write dist/manifest.json
dist/             GitHub Pages output
docs/             screenshots, language intros, launch copy
.github/          CI: push to main -> build -> deploy Pages
```

## Release Flow

1. Edit `games/tower100/tower100.html`.
2. Bump the version in `scripts/build_manifest.py`.
3. Push to `main`.
4. GitHub Actions rebuilds `dist/` for the repository fallback.
5. Deploy production:

```bash
python3 scripts/build_manifest.py
bash scripts/deploy_cloudflare_pages.sh
```

The deploy script publishes the existing `dist/` exactly and does not rebuild
it implicitly. Use `--build` only when a fresh timestamped manifest is intended.

6. Installed users receive the new bundle on next launch from
   `https://arcade.fxpeek.com/manifest.json`.

Optional manifest signing:

```bash
python3 -m pip install pynacl
python3 scripts/manifest_keygen.py
ARCADE_MANIFEST_SIGNING_KEY=... python3 scripts/build_manifest.py
```

Keep the signing key on the release runner only. Burn the public key into the
loader when you are ready to enforce manifest signatures.

## Roadmap

- [x] M1: Down 100 Floors + hot-update loader
- [x] M1.1: sharing, sponsor link, multilingual project intro
- [ ] M2: hub screen, second game, WeChat mini-game adapter
- [ ] M3: AdSense switch, Stripe Pro license flow, global leaderboard

## License

MIT.
