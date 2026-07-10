# Arcade Skill 🕹️

Instant mini-games for the moments you're waiting on Claude Code / Codex.
Say "开个游戏" / "I'm bored" and **Down 100 Floors** opens in your browser.

[Project intro in 中文 / English / Français / Italiano / العربية](docs/project-intro.md)

- **Thin-shell architecture** — the installed skill is a ~200-line stdlib-only
  launcher. All games, notices, ad switches and pricing live in a remote
  `manifest.json`. Shipping an update = `git push`. Users never reinstall.
- **Offline-capable** — bundles are sha256-verified and cached in
  `~/.arcade-skill/`; a seed bundle ships inside the skill so the very first
  run works with no network.
- **Original code** — clean-room rewrite of the classic falling-floors
  formula. No third-party game code or art. MIT.

## Install (as a Claude skill)

Copy the `skill/` folder into your skills directory (or install the packaged
`arcade.skill` from Releases). Then in any conversation:

> 无聊,来一把下100层

Claude runs `python3 scripts/launcher.py --daemon` and hands you a local URL.

## Play standalone

```bash
python3 skill/scripts/launcher.py            # zh UI
python3 skill/scripts/launcher.py --lang en  # en UI
```

Controls: ← → / A D, or tap left/right half on touch screens.
Land on floors to heal, avoid spikes, don't touch the ceiling. How deep can you go?

## Repo layout

```
skill/            the distributable skill (SKILL.md + launcher + seed bundle)
games/tower100/   game source — single self-contained HTML file
scripts/          build_manifest.py: hash bundles, write dist/manifest.json
dist/             build output = what GitHub Pages serves
.github/          CI: push to main → build → deploy Pages
```

## Releasing an update (hot update)

1. Edit `games/tower100/tower100.html`
2. Bump the version in `scripts/build_manifest.py` → `VERSIONS`
3. `git push` — CI rebuilds `dist/` and redeploys Pages
4. Every user gets the new bundle on next launch. That's it.

Flipping ads on later is the same motion: set
`MONETIZATION.ads.enabled = True` (plus your AdSense ids) and push.

## First-time setup after cloning

One command (requires `git` + [GitHub CLI](https://cli.github.com) with `gh auth login` done):

```bash
./publish.sh <your-github-username>
```

It bakes your username into the manifest URLs, builds `dist/`, creates the
repo, pushes, enables Pages (Actions source), and publishes `arcade.skill`
as Release v1.0.0. Prefer a custom domain? Edit `BASE_URL` in
`scripts/build_manifest.py` and the `MANIFEST_URLS` list in
`skill/scripts/launcher.py` before running.

## Roadmap

- [x] M1 — tower100 + manifest hot-update loop
- [ ] M2 — hub page, second game (snake), WeChat mini-game adapter fork
- [ ] M3 — AdSense switch-on, Stripe Pro licenses, global leaderboard

## License

MIT — game code and art are original to this repository.
