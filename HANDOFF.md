---
type: project-handoff
status: active
updated: 2026-07-13
project: arcade-skill
---

# Arcade Skill Handoff

## Current State

- Active checkout: `/Users/zhanbo/Documents/Codex/2026-06-22/x-2`
- GitHub: `https://github.com/Jenpo/arcade-skill`
- Verified branch: `main`; use the production manifest and current Actions runs
  below as deployment evidence instead of a handoff-embedded commit pointer.
- Production: `https://arcade.fxpeek.com`
- Production manifest: `2026.07.13-0732`
- Game bundle: `tower100-1.5.1.html`, sha256 prefix `9defc2e001da`
- Worktree was clean after the final deployment commit.

## Verified

- Authenticated local LiteLLM and `growth_smoke`: PASS.
- Tier A linter, three-post daily fuse, idempotent dry-run, and P3-disabled
  contract: PASS.
- Playwright desktop 1440x900 and mobile 390x844 structure and platform-specific
  pixel baselines: PASS on macOS and GitHub Ubuntu.
- GitHub Actions for `build-and-deploy`, `visual-regression`, and
  `growth-smoke`: PASS on `a4a2328`.
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

## Ownership Boundaries

- GitHub Actions deploys and verifies the `jenpo.github.io` fallback.
- Mac Wrangler deploys `dist/` to Cloudflare Pages production, then
  `production_health.py --min-manifest-version` proves the release.
- Telegram, local LLM, X browser session, and Cloudflare credentials stay on
  the Mac. They are not copied into GitHub.
- Tier A owned surfaces can run unattended only after deterministic gates.
- Tier B Reddit/HN replies and external issues/PRs remain one-click approved.

## Still Open

1. **SoM second real data point:** no five-engine answer export is available in
   the current environment. Empty answers must remain PENDING and must not be
   reported as 0% mention rate.
2. **One-click rollback callback:** notification messages and rollback workflow
   exist, but a dedicated Telegram bot plus a repo-scoped GitHub Actions token
   are still required before the callback Worker can be deployed safely. Do not
   reuse the Hermes polling bot webhook or a broad `gh` token.
3. **One-week proof:** LaunchAgents are active, but the 7-day unattended-run
   acceptance window has only just started.
4. **Stripe checkout:** still pending; support route is live, but no
   `buy.stripe.com` link, Pro, or global ranking may be claimed.

## Resume Commands

```bash
cd /Users/zhanbo/Documents/Codex/2026-06-22/x-2
git status --short
python3 scripts/growth/tier_a_runner.py health
python3 scripts/growth/growth_smoke.py
npm run test:visual
```

Do not mark the goal complete until the SoM observation, rollback callback, and
one-week unattended-run evidence are real and verified.
