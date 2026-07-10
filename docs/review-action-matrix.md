# Review Action Matrix

This file tracks the issues raised in `arcade_skill_review.md` and the exact
project response. It is intentionally operational: every row should be easy to
verify from code, manifest, docs, or deployment status.

## Completed

| Review item | Status | Implementation |
| --- | --- | --- |
| AdSense cannot monetize `127.0.0.1` | Done | Local launcher forces `ads.enabled = false`; README states ads belong only on hosted web. |
| Share loop must land on hosted web | Done | Manifest share URL is `https://arcade.fxpeek.com/play`; game share links add `ref=share`, `floor`, and daily mode when relevant. |
| Add jsDelivr manifest fallback | Done | `launcher.py` includes `cdn.jsdelivr.net/gh/Jenpo/arcade-skill@main/dist/manifest.json` after owned domain and GitHub Pages sources. |
| `touch license.jwt` should not unlock Pro | Done | Pro now uses optional HMAC license validation via `ARCADE_LICENSE_HMAC_KEY`; file-existence unlock is removed. |
| Manifest entry URL host should be constrained | Done | Launcher validates bundle entry hosts before downloading. |
| Manifest signing path | Done | Build script can emit `manifest.json.sig` with `ARCADE_MANIFEST_SIGNING_KEY`; launcher has the verification hook. Enforcement waits for release-runner key handling. |
| Remove "and more" hallucination | Done | Skill and README copy now describe the single current game and roadmap separately. |
| Remove "server-side Pro" hallucination | Done | Docs now call current Pro local lightweight validation and reserve server features for future M3. |
| Trigger scope too broad | Done | Skill description now requires clear user intent to play or take a game break. |
| Add sound | Done | Tower100 uses zero-asset WebAudio synth sounds for land, hurt, and death. |
| Add pause and blur pause | Done | `P` toggles pause; window blur auto-pauses. |
| Add death recap hook | Done | Game-over screen shows a recap placeholder; telemetry can replace it with real cohort data later. |
| Add daily seed challenge | Done | Hosted `/play/?daily=1` injects daily mode; the game uses the date seed and emits mode/seed. |
| Rotate share text variants | Done | Share copy now rotates between score, challenge, and agent-wait variants. |
| Add hosted playable web version | Done | `docs/play.html` is deployed as `/play/` and embeds the verified bundle. |
| Surface tips, Stripe, and ranking strategy in README | Done | README now has Payment And Support, Ranking And Fair Play, and Play Modes sections. |
| Add screenshots / demo feeling | Done | SVG screenshots show Codex/Claude side-by-side demo, menu, and gameplay. |
| Clarify player character | Done | The player sprite is an 8-bit small person, not a plain block. |
| Telemetry receiver | Done | Cloudflare Worker is live at `https://telemetry.fxpeek.com/event`; D1 database `arcade_telemetry` stores accepted events. |

## Deployment-Dependent

| Review item | Current state | Next action |
| --- | --- | --- |
| `arcade.fxpeek.com` HTTPS certificate | Content works through GitHub Pages, but normal curl still reports certificate validation failure until GitHub Pages finishes custom-domain cert issuance. | Recheck GitHub Pages certificate, then enforce HTTPS once certificate exists. |
| AdSense | Hosted slot exists, local sessions stay ad-free. | Apply only after the hosted site has enough content and AdSense approves `arcade.fxpeek.com`. |
| Stripe supporter flow | Strategy and README are ready; no paid-power feature is shipped. | Add Stripe Payment Link only after usage signal; Pro must stay cosmetic/supporter-only. |

## Deferred Product Work

| Review item | Reason |
| --- | --- |
| Second game | M2 scope. It should ship after the first game has telemetry and share-loop evidence. |
| Global leaderboard | Requires telemetry/identity/rate-limit foundation first. Ranked play must stay fair: no paid health, no paid revive, no paid score advantage. |
| WeChat mini-game adapter | M2/M3 channel expansion after web/skill loop stabilizes. |
