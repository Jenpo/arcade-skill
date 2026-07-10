#!/usr/bin/env python3
"""Build dist/: copy game bundles, compute sha256, write manifest.json.

Release flow = edit games/*/ + bump VERSIONS + git push. CI runs this and
deploys dist/ to GitHub Pages. Nothing else to do.
"""
import hashlib, json, shutil, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BUNDLES = DIST / "bundles"
DOCS = ROOT / "docs"

# ---- release registry: bump a version here to ship a new build ----
BASE_URL = "https://arcade.fxpeek.com"       # owned domain; CNAME → GitHub Pages
CUSTOM_DOMAIN = "arcade.fxpeek.com"          # written to dist/CNAME for Pages
VERSIONS = {
    "tower100": {
        "version": "1.1.1",
        "src": ROOT / "games/tower100/tower100.html",
        "title": {"zh": "是男人就下100层", "en": "Down 100 Floors"},
        "tier": "free",
    },
}
MONETIZATION = {
    "tips": {
        "enabled": True,                  # NEW BEST moment tip line + link
        "url": "https://github.com/sponsors/Jenpo",
    },
    "share": {
        "enabled": True,
        "url": "https://arcade.fxpeek.com",   # landing for shared scores (?ref=share)
    },
    "ads": {
        "enabled": False,                 # <— THE ad switch. flip + push = live.
        "provider": "adsense",
        "client_id": "",                  # fill after AdSense approval
        "slots": {"game_over": ""},
    },
    "pro": {
        "enabled": False,                 # flip on when Stripe track ships (M3)
        "stripe_payment_link": "",
        "license_pubkey": "",
    },
}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    BUNDLES.mkdir(parents=True, exist_ok=True)
    games = []
    for gid, meta in VERSIONS.items():
        src = meta["src"]
        if not src.exists():
            sys.exit(f"missing source: {src}")
        name = f"{gid}-{meta['version']}.html"
        dst = BUNDLES / name
        shutil.copy2(src, dst)
        digest = sha256_file(dst)
        games.append({
            "id": gid, "title": meta["title"], "version": meta["version"],
            "entry": f"{BASE_URL}/bundles/{name}", "sha256": digest,
            "size_kb": round(dst.stat().st_size / 1024, 1),
            "tier": meta["tier"], "min_loader_version": "1.0.0",
        })
        # refresh the offline seed shipped inside the skill package
        seed_dir = ROOT / "skill/assets"
        seed_dir.mkdir(parents=True, exist_ok=True)
        for old in seed_dir.glob(f"{gid}-*.html"):
            old.unlink()
        shutil.copy2(dst, seed_dir / name)
        print(f"  {name}  {digest[:12]}…  {games[-1]['size_kb']}KB")

    manifest = {
        "schema_version": 2,
        "manifest_version": time.strftime("%Y.%m.%d-%H%M"),
        "min_loader_version": "1.0.0",
        "kill_switch": False,
        "notice": {"zh": "", "en": ""},
        "monetization": MONETIZATION,
        "games": games,
    }
    (DIST / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (DIST / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")
    if DOCS.exists():
        docs_out = DIST / "docs"
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(DOCS, docs_out)
        landing = DOCS / "landing.html"
        if landing.exists():
            shutil.copy2(landing, DIST / "index.html")
    print(f"manifest {manifest['manifest_version']} → dist/manifest.json  (CNAME: {CUSTOM_DOMAIN})")


if __name__ == "__main__":
    main()
