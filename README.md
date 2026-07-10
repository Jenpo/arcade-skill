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
[Sponsor on GitHub](https://github.com/sponsors/Jenpo) ·
[Download arcade.skill](https://github.com/Jenpo/arcade-skill/releases/tag/v1.0.0) ·
[View manifest](https://arcade.fxpeek.com/manifest.json) ·
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

- **Tips now:** GitHub Sponsors is live. The repo links to it, and the game only
  surfaces the coffee link when you hit a new personal best.
- **Stripe later:** Pro is reserved for cosmetics, early access, supporter
  badges, or cloud features after real usage signal. No paid power.
- **Ads later:** AdSense can be enabled on the hosted web version after the site
  has enough content and review readiness. Local skill sessions stay ad-free.

Current support link:

> https://github.com/sponsors/Jenpo

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
- Works offline through a seed bundle and cached verified bundles.
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
4. GitHub Actions rebuilds `dist/` and deploys Pages.
5. Installed users receive the new bundle on next launch.

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
