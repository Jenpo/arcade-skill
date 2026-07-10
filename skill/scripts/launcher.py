#!/usr/bin/env python3
"""Arcade Skill launcher — thin bootstrap shell. stdlib only, no pip installs.

Design contract (do NOT put game logic here — everything below is hot-updatable
via the remote manifest, this file should almost never need to change):

  1. Fetch manifest.json from MANIFEST_URLS (first that answers wins).
  2. Verify / refresh cached game bundles by version + sha256 (atomic replace).
  3. Inject runtime config (ads / pro / lang) via ?cfg= base64 JSON.
  4. Serve the cache dir on localhost and open the browser.

Offline behaviour: falls back to last cached manifest, then to the seed bundle
shipped inside the skill package. Ads are forced OFF when offline.
"""
import argparse, base64, hashlib, http.server, json, os, shutil, socket
import socketserver, subprocess, sys, threading, time, urllib.request, webbrowser
from pathlib import Path

# ---- the ONLY burned-in values. Use a domain you control forever. ----
MANIFEST_URLS = [
    os.environ.get("ARCADE_MANIFEST_URL", ""),
    "https://arcade.fxpeek.com/manifest.json",               # primary: owned domain
    "https://jenpo.github.io/arcade-skill/manifest.json",
    "https://raw.githubusercontent.com/Jenpo/arcade-skill/main/dist/manifest.json",
]
LOADER_VERSION = "1.0.0"
CACHE = Path(os.environ.get("ARCADE_CACHE_DIR", Path.home() / ".arcade-skill"))
SKILL_DIR = Path(__file__).resolve().parent.parent          # skill/
SEED_BUNDLES = SKILL_DIR / "assets"                          # offline fallback


def log(msg): print(f"[arcade] {msg}", flush=True)


def ver_tuple(v): return tuple(int(x) for x in str(v).split(".") if x.isdigit())


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, timeout=4) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": f"arcade-loader/{LOADER_VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def load_manifest() -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / "manifest.json"
    for url in [u for u in MANIFEST_URLS if u and "REPLACE_ME" not in u]:
        try:
            data = fetch(url)
            m = json.loads(data)
            cached.write_bytes(data)
            m["_online"] = True
            log(f"manifest {m.get('manifest_version','?')} from {url}")
            return m
        except Exception as e:
            log(f"manifest fetch failed ({url.split('/')[2]}): {e.__class__.__name__}")
    if cached.exists():
        log("offline — using cached manifest, ads forced off")
        m = json.loads(cached.read_text())
        m["_online"] = False
        return m
    # first run + offline: synthesize a manifest around the seed bundle
    log("offline first run — using seed bundle shipped with the skill")
    seeds = sorted(SEED_BUNDLES.glob("*.html"))
    games = []
    for s in seeds:
        gid = s.stem.rsplit("-", 1)[0]
        games.append({"id": gid, "title": {"zh": gid, "en": gid}, "version": "seed",
                      "entry": s.name, "sha256": sha256_file(s), "tier": "free", "_seed": str(s)})
    return {"schema_version": 2, "kill_switch": False, "_online": False,
            "monetization": {"ads": {"enabled": False}}, "games": games}


def ensure_bundle(game: dict, online: bool) -> Path:
    """Return path of a verified local bundle. Never hands the user a broken file."""
    bundles = CACHE / "bundles"
    bundles.mkdir(parents=True, exist_ok=True)
    name = f"{game['id']}-{game['version']}.html"
    local = bundles / name
    if local.exists() and sha256_file(local) == game["sha256"]:
        return local
    if game.get("_seed"):                                   # offline first run
        shutil.copy2(game["_seed"], local)
        return local
    if online:
        tmp = local.with_suffix(".tmp")
        try:
            log(f"downloading {name} ...")
            tmp.write_bytes(fetch(game["entry"], timeout=15))
            if sha256_file(tmp) == game["sha256"]:
                tmp.replace(local)                          # atomic swap
                return local
            log("hash mismatch — discarding download")
            tmp.unlink(missing_ok=True)
        except Exception as e:
            log(f"download failed: {e.__class__.__name__}")
            tmp.unlink(missing_ok=True)
    # fall back to newest cached version of the same game
    prev = sorted(bundles.glob(f"{game['id']}-*.html"), key=lambda p: p.stat().st_mtime)
    if prev:
        log(f"falling back to cached {prev[-1].name}")
        return prev[-1]
    # last resort: any seed of that game
    for s in SEED_BUNDLES.glob(f"{game['id']}-*.html"):
        shutil.copy2(s, bundles / s.name)
        return bundles / s.name
    raise SystemExit(f"[arcade] no playable bundle for {game['id']}")


def build_cfg(manifest: dict, lang: str) -> str:
    mon = manifest.get("monetization", {})
    ads = dict(mon.get("ads", {}))
    if not manifest.get("_online"):
        ads["enabled"] = False
    licensed = (CACHE / "license.jwt").exists()             # TODO(M3): real signature check
    cfg = {"lang": lang, "ads": ads, "pro": licensed, "source": "skill",
           "tips": mon.get("tips", {}), "share": mon.get("share", {})}
    return base64.b64encode(json.dumps(cfg, separators=(",", ":")).encode()).decode()


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


def serve(directory: Path, port: int):
    os.chdir(directory)
    with socketserver.TCPServer(("127.0.0.1", port), Quiet) as httpd:
        httpd.serve_forever()


def main():
    ap = argparse.ArgumentParser(description="Arcade Skill launcher")
    ap.add_argument("--game", default=None, help="game id (default: first free game)")
    ap.add_argument("--lang", default="zh", choices=["zh", "en"])
    ap.add_argument("--daemon", action="store_true", help="detach server and return immediately")
    ap.add_argument("--no-open", action="store_true", help="print URL only, don't open browser")
    ap.add_argument("--port", type=int, default=0)
    args = ap.parse_args()

    m = load_manifest()
    if m.get("kill_switch"):
        raise SystemExit("[arcade] service paused by operator: " +
                         str(m.get("notice", {}).get(args.lang, "")))
    need = m.get("min_loader_version", "0")
    if ver_tuple(LOADER_VERSION) < ver_tuple(need):
        log(f"NOTE: loader {LOADER_VERSION} < required {need} — please reinstall the skill soon")

    games = m.get("games", [])
    pick = None
    if args.game:
        pick = next((x for x in games if x["id"] == args.game), None)
        if not pick:
            raise SystemExit(f"[arcade] unknown game '{args.game}'. available: "
                             + ", ".join(x["id"] for x in games))
    else:
        pick = next((x for x in games if x.get("tier", "free") == "free"), games[0] if games else None)
    if not pick:
        raise SystemExit("[arcade] manifest has no games")

    bundle = ensure_bundle(pick, m.get("_online", False))
    port = args.port or free_port()
    url = f"http://127.0.0.1:{port}/{bundle.name}?cfg={build_cfg(m, args.lang)}"

    if args.daemon:
        child = subprocess.Popen(
            [sys.executable, __file__, "--port", str(port), "--lang", args.lang,
             "--no-open"] + (["--game", pick["id"]] if args.game else []),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True)
        time.sleep(0.6)
        if not args.no_open:
            webbrowser.open(url)
        print(url)
        log(f"server pid {child.pid} — stop with: kill {child.pid}")
        return

    threading.Thread(target=serve, args=(bundle.parent, port), daemon=True).start()
    print(url)
    if not args.no_open:
        webbrowser.open(url)
    notice = m.get("notice", {}).get(args.lang)
    if notice:
        log(f"notice: {notice}")
    log("serving — Ctrl+C to stop")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        log("bye")


if __name__ == "__main__":
    main()
