---
name: arcade
description: >
  Launch instant browser mini-games (Down 100 Floors / 是男人就下100层 and more)
  for the user to play while waiting. Use this skill whenever the user says they
  are bored, waiting for a long task, wants to play a game, take a break, or
  mentions 玩游戏 / 无聊 / 摸鱼 / 等任务 / 来一把 / 下100层 / game / bored /
  "kill time" — even if they don't explicitly ask for an "arcade". Also use it
  proactively when a long-running background task leaves the user idle and they
  ask what to do meanwhile.
---

# Arcade — games while you wait

This skill opens a local, offline-capable mini-game in the user's browser.
Game content is hot-updated from a remote manifest; this skill package itself
is only a thin launcher and rarely changes.

## How to launch

Default (Down 100 Floors, Chinese UI, detaches and returns immediately):

```bash
python3 scripts/launcher.py --daemon
```

Options:

- `--lang en` — English UI
- `--game <id>` — pick a specific game (see list below)
- `--no-open` — print the URL only (useful over SSH; tell the user to open it)

The command prints the local URL (`http://127.0.0.1:<port>/...`) and the server
PID. Relay the URL to the user, and mention the PID kill command if they ask
how to stop it.

## Listing available games

The manifest is fetched at launch; to show the catalogue without launching:

```bash
python3 - <<'PY'
import json, urllib.request
u = "https://arcade.fxpeek.com/manifest.json"
m = json.load(urllib.request.urlopen(u, timeout=4))
for g in m["games"]:
    print(f"{g['id']:<12} v{g['version']:<8} {g['title'].get('zh','')} / {g['title'].get('en','')}  [{g.get('tier','free')}]")
PY
```

## Behaviour notes

- Works fully offline after first run (bundles cached in `~/.arcade-skill/`);
  a seed copy of the flagship game ships in `assets/` so even the very first
  run works without network.
- Ads and Pro unlocks are controlled server-side by the manifest — never edit
  the launcher to change monetization behaviour.
- If the manifest reports `kill_switch: true`, tell the user the arcade is
  temporarily paused and relay the notice text.
- Do not keep the conversation waiting on the game: launch with `--daemon`,
  hand over the URL, and continue with whatever task was in progress.
