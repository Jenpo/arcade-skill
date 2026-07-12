---
type: project-handoff
status: active
updated: 2026-07-13
project: arcade-skill
---

# Arcade Skill Project Handoff

## 1. Current Snapshot

- Active working copy: `/Users/zhanbo/Documents/Codex/2026-06-22/x-2`
- Git remote: `https://github.com/Jenpo/arcade-skill.git`
- Branch: `main`
- Base commit: `5c7de9d chore: refresh production manifest`
- Production domain: `https://arcade.fxpeek.com`
- Last known live manifest from the previous completed deploy:
  `2026.07.12-2318`. This was not revalidated during the current handoff turn.
- The older publish-run checkout remains at
  `/Users/zhanbo/Documents/Codex/2026-06-22/x/work/arcade-publish-run/arcade-skill`.
  Current uncommitted work exists only in the active `x-2` copy.

Do not delete either checkout until the `x-2` changes are committed and pushed.

## 2. Product Contract

- The installed skill is a thin launcher. Game bundles, notices, support links,
  ads flags, and kill switch settings come from the signed/hash-verified
  manifest path.
- The first game is the original rewrite **Down 100 Floors**, bundle version
  `1.5.1` in the current repository baseline.
- Local skill sessions run on `127.0.0.1`; AdSense must remain disabled there.
- Hosted play lives at `https://arcade.fxpeek.com/play/`.
- Stripe support is allowed, but never buys health, revives, score, or ranking
  advantage.
- Stripe checkout is still described as pending. Do not claim that a live
  `buy.stripe.com` payment link exists until it is actually configured.
- The current game stores a local personal best. Global ranking is planned, not
  live. Do not publish copy that claims a production leaderboard exists.
- Growth discovery can be automated; replies, posts, issues, and pull requests
  remain human-reviewed.
- Copy, design review, SEO/GEO critique, and routine summaries are local-LLM
  first. There is no automatic paid API fallback.

## 3. Previously Completed And Live

- Multilingual project introductions: Chinese, English, French, Italian, and
  Arabic.
- Language links at the beginning of the main project presentation.
- Hosted play, daily challenge, support, about, scenarios, `llms.txt`, and
  `ai.txt` routes.
- Original game art and code, WebAudio sound effects, and chiptune BGM.
- Share-score and Stripe-support hooks on the game-over path.
- Manifest sha256 verification, atomic cache replacement, offline seed bundle,
  and fallback manifest sources.
- Telemetry Worker/D1 hooks and read-only production-health checks.
- Growth scripts for mention radar, scenario-page generation, leaderboard
  drafts, Share of Model, telemetry reports, and weekly summaries.

## 4. Uncommitted Changes In This Working Copy

### Design And Collaboration

- `docs/scenarios/index.html`
  - Reduced oversized heading scale.
  - Replaced pill-heavy navigation/actions with compact links and 6px buttons.
  - Removed the decorative screen gradient and card shadows.
  - Changed the cabinet preview from a square avatar to a recognisable pixel
    person.
  - Added visible keyboard focus styling.
- `docs/DESIGN.md`
  - Added the required Reference / Keep / Fix / Avoid / Verify audit.
  - References are limited to Vercel, Stripe, and PlayStation.
- `docs/awesome-design-md-proposal.md`
  - Added a form-aligned request draft for `VoltAgent/awesome-design-md`.
  - Important: the live repository currently accepts a `Design MD Request`
    issue and explicitly says it cannot accept external `DESIGN.md` pull
    requests. The draft now uses the four required form fields.
- `scripts/build_manifest.py` and `README.md`
  - Added the collaboration document to public build routes and quick links.

### Local LLM Default

- `scripts/growth/local_review.py`
  - New reusable subprocess bridge around `scripts/local_llm.py`.
  - Writes `PASS`, `LOCAL_LLM_PENDING`, or `LOCAL_LLM_UNAVAILABLE` into review
    artifacts without using a paid fallback.
- `scripts/growth/mention_radar.py`
  - Runs local opportunity review by default after deterministic scoring.
  - `--no-llm-review` is available for deterministic-only testing.
- `scripts/growth/seo_page_factory.py`
  - Runs one aggregated local SEO review after deterministic QC.
  - Default report: `growth/reports/seo-local-review-latest.md`.
- `.gitignore`
  - Ignores only root generated output under `/growth/`; it does not ignore
    `scripts/growth/` source files.
- `docs/local-llm-policy.md` and `docs/growth-engine.md`
  - Document the default local review behavior and explicit fallback boundary.

### Local Router Diagnostics

- `scripts/local_llm.py`
  - Moved `reasoning_effort: false` to the raw request's top level.
  - Added bounded HTTP error-body capture for the next diagnostic run.
  - No key or secret was committed or printed.

## 5. Verification Evidence

Passed in the current working copy:

```text
python3 -m py_compile ...                         PASS
git diff --check                                 PASS
mention_radar.py --offline                       PASS
SEO page deterministic QC                       PASS
English page 1: 800 words, max Jaccard 0.316
English page 2: 729 words, max Jaccard 0.316
Chinese page: 1109 words, max Jaccard 0.361
```

Local review behavior observed:

```text
No injected router key: LOCAL_LLM_PENDING
Router key loaded in process: HTTP 400
Paid API fallback: not used
```

The first 400 response hid its body. Bounded error-body reporting has now been
added, but the command was not rerun because the handoff was requested.

Not yet run after these edits:

- Full `scripts/growth/growth_smoke.py` with an authenticated local router.
- `scripts/build_manifest.py`.
- Desktop/mobile screenshot verification of the revised scenarios page.
- `scripts/production_health.py` after deployment.
- Git commit, push, Cloudflare Pages deploy, or live manifest verification.
- External `VoltAgent/awesome-design-md` issue creation.

## 6. Current Blockers And Risks

### P1: Local LLM HTTP 400

Run the authenticated local helper once more now that HTTP error-body capture is
present. Use the exact returned error to decide whether the router expects
`reasoning_effort` at the top level, drops it, or requires a different model
alias. Do not repeat blind payload changes and do not fall back to a paid API.

### P1: Collaboration Request Is Not Yet Submitted

Current upstream issue fields are:

- Website URL
- Delivery Email
- Priority: No / Yes
- Additional Details

The draft uses `https://arcade.fxpeek.com/scenarios/`, `data@fxpeek.com`, and
Priority `No`. Review the final issue body before creating it because upstream
says external DESIGN.md PRs are not accepted.

### P1: Uncommitted Working Copy

All current changes are uncommitted in `x-2`. Do not deploy from the older
publish-run checkout or the new changes will be omitted.

### P2: Visual Regression Check Pending

The revised scenarios page still needs 1440x900 and 390x844 screenshots. Check
navigation wrapping, cabinet-first mobile order, pixel-person legibility, focus
states, and text overflow.

## 7. Safe Resume Order

1. Run `git status --short` from the active `x-2` working copy.
2. Rerun authenticated local design review and inspect the captured 400 body.
3. Fix only the specific local-router contract error, then run:

   ```bash
   python3 scripts/growth/growth_smoke.py
   ```

4. Review `docs/awesome-design-md-proposal.md` against the actual issue form.
5. Build and verify locally:

   ```bash
   python3 scripts/build_manifest.py
   python3 scripts/production_health.py --insecure
   ```

6. Verify desktop and mobile rendered pages.
7. Review `git diff`, commit, and push the `x-2` working copy.
8. Deploy Cloudflare Pages and verify manifest, bundle sha256, support route,
   scenarios route, and Actions status.
9. Create the upstream Design MD Request issue only after the final issue body
   is reviewed.

## 8. Do Not Regress

- Do not expose or commit Cloudflare, Stripe, LiteLLM, GitHub, or telemetry
  credentials.
- Do not claim Stripe checkout, global ranking, or Pro is live before evidence.
- Do not enable AdSense for localhost skill sessions.
- Do not sell competitive advantage.
- Do not copy Egret code or third-party game art.
- Do not auto-publish community outreach.
- Do not silently route local-first work to a paid API.
