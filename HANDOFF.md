---
type: project-handoff
status: active
updated: 2026-07-16
project: arcade-skill
---

# Arcade Skill Handoff

## Current State

- Active checkout: `/Users/zhanbo/Documents/Codex/2026-06-22/x-2`
- GitHub: `https://github.com/Jenpo/arcade-skill`
- Verified branch: `main`; use the production manifest and current Actions runs
  below as deployment evidence instead of a handoff-embedded commit pointer.
- Production: `https://arcade.fxpeek.com`
- Production manifest: `2026.07.16-0851`
- Game bundle: `tower100-1.5.1.html`, sha256 prefix `9defc2e001da`
- Verified functional change sets: `c0861a4` (exact Cloudflare artifact),
  `840b50c` (independent GitHub manifest fallback), and `2e6a530` (loader v1.2
  verified bundle mirrors). Use live endpoints and Actions as release evidence;
  do not chase a self-referential handoff commit.

## Verified

- Authenticated local LiteLLM and `growth_smoke`: PASS.
- Tier A linter, three-post daily fuse, idempotent dry-run, and P3-disabled
  contract: PASS.
- Playwright desktop 1440x900 and mobile 390x844 structure and platform-specific
  pixel baselines: PASS on macOS and GitHub Ubuntu.
- GitHub Actions for `build-and-deploy`, `visual-regression`, and
  `growth-smoke`: PASS on `2e6a530`.
- Cloudflare production routes, support status, ads-off flag, manifest schema,
  kill switch, and bundle hash: PASS.
- VoltAgent request created: https://github.com/VoltAgent/awesome-design-md/issues/445
- Mac LaunchAgents loaded:
  - SoM Monday 11:05
  - SEO Wednesday 11:15
  - Weekly telemetry Sunday 11:25
  - Production health every six hours
  - Owned-channel queue every five minutes
- LaunchAgent health run: exit 0, Telegram receipt `message_id=29943`.
- Local LiteLLM route recovered after starting the stopped Worker-Pro Ollama
  service; authenticated `growth_smoke` now reports local reviews as PASS.
- A bounded OpenAI Codex CLI proxy sample produced 5 observed rows and 20
  explicit unobserved rows (`20%` coverage). The scored report was delivered to
  Telegram as `message_id=30026`; mention and citation rates were both `0/5`.

## Ownership Boundaries

- GitHub Actions deploys and verifies the `jenpo.github.io` fallback.
- Mac Wrangler deploys `dist/` to Cloudflare Pages production, then
  `production_health.py --min-manifest-version` proves the release.
- GitHub Pages must not have `arcade.fxpeek.com` configured as a custom domain;
  otherwise its fallback URL redirects back to production and ceases to be an
  independent manifest source. `dist/CNAME` is deliberately absent. This is
  Loader v1.2 adds verified bundle mirrors across GitHub Pages, raw GitHub, and
  jsDelivr. Older v1.1 installations keep the primary `entry` compatibility
  path and still require reinstalling the skill to gain mirror retries.
- Telegram, local LLM, X browser session, and Cloudflare credentials stay on
  the Mac. They are not copied into GitHub.
- Tier A owned surfaces can run unattended only after deterministic gates.
- Tier B Reddit/HN replies and external issues/PRs remain one-click approved.

## Still Open

1. **SoM full second data point:** the OpenAI/Codex proxy sample is complete,
   but Claude, Perplexity, Gemini, and Copilot remain unobserved. The current
   `5/25` sample is honest partial coverage, not a complete five-engine data
   point. Empty or unobserved answers remain PENDING and are not scored as
   misses.
2. **One-click rollback callback:** notification messages and rollback workflow
   exist, but a dedicated Telegram bot plus a repo-scoped GitHub Actions token
   are still required before the callback Worker can be deployed safely. Do not
   reuse the Hermes polling bot webhook or a broad `gh` token.
3. **One-week proof:** LaunchAgents are active, but the 7-day unattended-run
   acceptance window has only just started.
4. **Stripe checkout:** still pending; support route is live, but no
   `buy.stripe.com` link, Pro, or global ranking may be claimed.

## Delivered Change Set

The tested SoM collector and local LLM routing fix were committed, pushed, and
deployed in `cd875b4` plus the exact-artifact deploy fix in `c0861a4`:

- `scripts/growth/som_batch_schema.json` (new)
- `scripts/growth/som_codex_collector.py` (new)
- `scripts/growth/tier_a_runner.py` (modified)
- `scripts/growth/tier_a_smoke.py` (modified)
- `scripts/growth/som_tracker.py` (modified)
- `scripts/install_tier_a_launchd.py` (modified)
- `scripts/local_llm.py` (modified)
- `docs/growth-engine.md` (modified)
- `docs/local-llm-policy.md` (modified)

Completed checks: Python compile, schema load, one bounded proxy collection,
25-row validation, atomic-write/concurrency tests, SoM scoring, Tier A smoke,
authenticated local-LLM growth smoke, LaunchAgent reload, and Telegram delivery.
Scheduled cloud collection is explicitly off (`ARCADE_SOM_CODEX_ENABLED=0`).
Playwright passed locally and in GitHub Actions. Cloudflare production passed
strict health verification at manifest `2026.07.16-0851`.
GitHub Pages custom-domain binding was cleared and the direct manifest endpoint
now returns HTTP 200 instead of redirecting to production (`840b50c`).
Loader v1.2 verified all four bundle mirrors at SHA256 `9defc2e001da...`.
Release `v1.2.0` is Latest; its `arcade.skill` SHA256 is
`f1156ca058f7c04c7f857e4e9cd2ba05bfb7abbee106c3026ec6bf756fae8ad8`.

## Product Truth

- The playable character is an original pixel person, not a plain block.
- Tower100 v1.5.1, multilingual project pages, BGM/SFX, hosted play, sharing,
  telemetry, Stripe support routing, and local best score are live.
- Stripe checkout is not live. `/support/` is a truthful waiting/support route.
- Ads are disabled. AdSense must never be claimed for localhost skill sessions.
- A production global leaderboard does not exist; P3 remains disabled.
- The Egret original is not copied. Game code and visual assets are original.

## Non-Negotiable Rules

- Low-risk copy, SEO/GEO, critique, and summaries use the local LLM first. Do
  not silently fall back to a paid API. External model calls are allowed only
  for explicit external measurement or diagnosis.
- Tier A owned channels may publish automatically only after deterministic
  lint, rate-limit, idempotency, live-check, and rollback gates pass.
- Tier B Reddit/HN/V2EX and third-party issues/PRs stay one-click approved.
- Never expose or copy credentials into GitHub, logs, chat, or documentation.
- Do not mark the goal complete until full SoM evidence, safe rollback callback,
  and seven days of unattended Tier A evidence are verified.

## Resume Commands

```bash
cd /Users/zhanbo/Documents/Codex/2026-06-22/x-2
git status --short
python3 scripts/growth/tier_a_runner.py health
python3 scripts/growth/growth_smoke.py
npm run test:visual
```
