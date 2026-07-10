# Arcade Skill Project Intro

## Languages

[中文](intro.zh.md) · [English](intro.en.md) · [Français](intro.fr.md) · [Italiano](intro.it.md) · [العربية](intro.ar.md)

Ready-to-use project descriptions, screenshots, and launch positioning for
GitHub, directories, launch posts, and landing pages.

## Screenshot Gallery

| Codex / Claude demo | Game menu | Gameplay |
| --- | --- | --- |
| ![Arcade Skill running beside a coding-agent session](assets/screenshots/codex-claude-demo.svg) | ![Down 100 Floors start screen](assets/screenshots/tower100-menu.svg) | ![Down 100 Floors gameplay](assets/screenshots/tower100-run.svg) |

## Positioning

Arcade Skill is an agent-era loading screen: tiny nostalgic arcade games that
open while Claude Code, Codex, or another coding agent is busy working.

The installed skill stays stable and lightweight. The remote manifest controls
game bundles, notices, sponsor links, ads switches, Pro switches, and emergency
shutdowns. Shipping an update is a push to `arcade.fxpeek.com`, not a user
reinstall.

The tone is intentionally geeky and retro: terminal logs, local URLs, sha256
checks, hot-update manifests, pixel platforms, and that “one more run before the
tests finish” feeling.

## First Game

**Down 100 Floors / 是男人就下100层** is a clean-room rewrite of the classic
falling-platform formula that lived in old web portals, school computer rooms,
and early mobile game folders:

- Move left and right.
- Land on platforms to survive.
- Avoid spikes and the ceiling.
- Chase a deeper floor and a cleaner run.
- Hear tiny zero-asset chiptune BGM and arcade synth hits after the first input.

## Ranking Direction

The current release stores a local personal best. Future leaderboard mode should
stay skill-pure:

- Primary rank: deepest floor reached.
- Tie-breaker: faster time at the same floor.
- No paid health, paid revives, or paid competitive advantage.
- Score submissions should include version, mode, seed, and compact event data.

## GTM and Monetization

The project should earn money like a geeky developer artifact, not like a
pay-to-win mobile funnel.

- **Tip jar first:** GitHub Sponsors is the primary early monetization path and
  appears at the “new best” emotional peak.
- **Stripe later:** Pro should wait for real WAU signal and stay cosmetic,
  early-access, or supporter-badge based.
- **Ads later:** AdSense belongs on the web surface, not localhost skill
  sessions. The manifest keeps an `ads.enabled` switch ready for rollout.
- **Fair ranked play:** no paid health, paid revives, or competitive advantage.

## Suggested Tags

- AI coding break
- Browser mini-game
- Claude Code skill
- Codex companion
- Hot-updated HTML game bundle
- Down 100 Floors
- Agent-era loading screen
