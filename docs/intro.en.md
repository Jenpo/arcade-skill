# Arcade Skill

[中文](intro.zh.md) · [English](intro.en.md) · [Français](intro.fr.md) · [Italiano](intro.it.md) · [العربية](intro.ar.md)

## One-liner

Arcade Skill launches tiny nostalgic browser games while Claude Code, Codex, or another coding agent is busy compiling, testing, or thinking very hard.

## Short Description

Arcade Skill is a hot-updated mini-game launcher for AI coding workflows. Install it once, then say “I’m bored” or “play a game” while your agent runs tests, installs dependencies, or refactors code. A lightweight Python launcher fetches a remote manifest, verifies each single-file HTML bundle with sha256, caches it locally, and opens the game in your browser. The feeling is half terminal utility, half old web arcade cabinet.

## Long Description

Coding agents create a new kind of waiting time: a test suite is running, a dependency tree is installing, a refactor is being generated, or a deployment is building. Arcade Skill turns those idle moments into a small developer toy: local URL, manifest log, verified bundle, and a game that loads before your brain reaches for another tab.

The first game is a clean-room rewrite of **Down 100 Floors**: move left and right, land on platforms, avoid spikes, and chase a new personal best. The installed skill stays thin and stable; game content lives behind a remote manifest on `arcade.fxpeek.com`. New games, announcements, tip links, monetization switches, and emergency kill switches ship through hot updates without asking users to reinstall.

## Game Background and Gameplay

**Down 100 Floors** belongs to the classic family of early web, Flash-era, and feature-phone arcade games where the goal is not to climb upward, but to survive by descending. The platforms scroll upward, the ceiling keeps closing in, and the player has to move left or right to land safely on the next platform.

The challenge is direct: **survive longer, descend deeper, rank higher**. Normal platforms give you a stable landing and can restore health. Spikes deal damage. Springs launch you upward. Moving and fragile platforms break your rhythm. The pressure comes from both sides: the ceiling punishes hesitation, while the next landing demands timing.

The original appeal of this genre was always “one more try”: each run is short, failure is immediate, and improvement feels visible. That makes it a strong fit for idle moments while an AI coding agent is running tests, installing dependencies, or generating code. This version keeps the nostalgic loop but uses a clean-room implementation, original pixel-style visuals, and no third-party game code or art.

## Ranking and Fair Play

The current release stores a local personal best. When global leaderboards ship, ranked mode should stay skill-pure: same health, no paid power, no paid revives, and no advantage that changes the competitive rules. Casual mode can be more forgiving, but ranked mode must remain fair.

- Primary rank: deepest floor reached.
- Tie-breaker: faster time wins at the same floor.
- Anti-cheat metadata: submit game version, mode, random seed, and a compact event summary.
- Sharing loop: game-over and new-best states copy a text score with `?ref=share` for attribution.
