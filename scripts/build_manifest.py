#!/usr/bin/env python3
"""Build dist/: copy game bundles, compute sha256, write manifest.json.

Release flow = edit games/*/ + bump VERSIONS + git push. CI runs this and
deploys dist/ to GitHub Pages. Nothing else to do.
"""
import base64, hashlib, json, os, shutil, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BUNDLES = DIST / "bundles"
DOCS = ROOT / "docs"

# ---- release registry: bump a version here to ship a new build ----
BASE_URL = "https://arcade.fxpeek.com"       # owned domain; production runs on Cloudflare Pages
CUSTOM_DOMAIN = "arcade.fxpeek.com"          # kept for GitHub Pages fallback compatibility
SIGNING_KEY_B64 = os.environ.get("ARCADE_MANIFEST_SIGNING_KEY", "")
STRIPE_SUPPORT_URL = os.environ.get(
    "ARCADE_STRIPE_SUPPORT_URL", f"{BASE_URL}/support/")
VERSIONS = {
    "tower100": {
        "version": "1.5.1",
        "src": ROOT / "games/tower100/tower100.html",
        "title": {"zh": "是男人就下100层", "en": "Down 100 Floors"},
        "tier": "free",
    },
}
MONETIZATION = {
    "tips": {
        "enabled": True,                  # game-over support link
        "provider": "stripe",
        "url": STRIPE_SUPPORT_URL,
    },
    "share": {
        "enabled": True,
        "url": "https://arcade.fxpeek.com/play",   # hosted play/share landing (?ref=share)
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
    "telemetry": {
        "enabled": True,                  # Worker + D1 deployed
        "endpoint": "https://telemetry.fxpeek.com/event",
        "sample_rate": 1.0,
    },
}

STATIC_ROUTES = [
    "/",
    "/about/",
    "/scenarios/",
    "/play/",
    "/support/",
    "/docs/project-intro.md",
    "/docs/DESIGN.md",
    "/docs/local-llm-policy.md",
    "/docs/intro.zh.md",
    "/docs/intro.en.md",
    "/docs/intro.fr.md",
    "/docs/intro.it.md",
    "/docs/intro.ar.md",
    "/llms.txt",
    "/ai.txt",
    "/manifest.json",
]


def discover_routes():
    routes = list(STATIC_ROUTES)
    scenarios = DOCS / "scenarios"
    if scenarios.exists():
        for index in sorted(scenarios.glob("*/index.html")):
            slug = index.parent.name
            routes.append(f"/scenarios/{slug}/")
    return routes


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def maybe_sign_manifest(manifest_path: Path):
    if not SIGNING_KEY_B64:
        sig = manifest_path.with_suffix(manifest_path.suffix + ".sig")
        sig.unlink(missing_ok=True)
        return
    try:
        from nacl.signing import SigningKey
    except ImportError:
        sys.exit("ARCADE_MANIFEST_SIGNING_KEY is set but PyNaCl is not installed")
    key = SigningKey(base64.b64decode(SIGNING_KEY_B64))
    sig = key.sign(manifest_path.read_bytes()).signature
    manifest_path.with_suffix(manifest_path.suffix + ".sig").write_text(
        base64.b64encode(sig).decode() + "\n", encoding="utf-8")


def copy_rendered_doc(src: Path, dst: Path):
    text = src.read_text(encoding="utf-8")
    text = text.replace("__ARCADE_STRIPE_SUPPORT_URL__", STRIPE_SUPPORT_URL)
    dst.write_text(text, encoding="utf-8")


def render_html_tree(root: Path):
    for path in root.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        rendered = text.replace("__ARCADE_STRIPE_SUPPORT_URL__", STRIPE_SUPPORT_URL)
        if rendered != text:
            path.write_text(rendered, encoding="utf-8")


def write_search_files():
    robots = "\n".join([
        "User-agent: *",
        "Allow: /",
        "",
        "User-agent: GPTBot",
        "Allow: /",
        "",
        "User-agent: ClaudeBot",
        "Allow: /",
        "",
        "User-agent: PerplexityBot",
        "Allow: /",
        "",
        "Sitemap: https://arcade.fxpeek.com/sitemap.xml",
        "",
    ])
    (DIST / "robots.txt").write_text(robots, encoding="utf-8")
    today = time.strftime("%Y-%m-%d")
    urls = "\n".join(
        f"  <url><loc>{BASE_URL}{route}</loc><lastmod>{today}</lastmod></url>"
        for route in discover_routes()
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")


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
    manifest_path = DIST / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    maybe_sign_manifest(manifest_path)
    (DIST / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")
    if DOCS.exists():
        docs_out = DIST / "docs"
        if docs_out.exists():
            shutil.rmtree(docs_out)
        shutil.copytree(DOCS, docs_out)
        render_html_tree(docs_out)
        landing = DOCS / "landing.html"
        if landing.exists():
            shutil.copy2(landing, DIST / "index.html")
        play = DOCS / "play.html"
        if play.exists():
            play_dir = DIST / "play"
            play_dir.mkdir(exist_ok=True)
            copy_rendered_doc(play, play_dir / "index.html")
            copy_rendered_doc(play, DIST / "play.html")
        support = DOCS / "support.html"
        if support.exists():
            support_dir = DIST / "support"
            support_dir.mkdir(exist_ok=True)
            copy_rendered_doc(support, support_dir / "index.html")
            copy_rendered_doc(support, DIST / "support.html")
        about = DOCS / "about.html"
        if about.exists():
            about_dir = DIST / "about"
            about_dir.mkdir(exist_ok=True)
            copy_rendered_doc(about, about_dir / "index.html")
            copy_rendered_doc(about, DIST / "about.html")
        scenarios = DOCS / "scenarios"
        if scenarios.exists():
            scenarios_out = DIST / "scenarios"
            if scenarios_out.exists():
                shutil.rmtree(scenarios_out)
            shutil.copytree(scenarios, scenarios_out)
            render_html_tree(scenarios_out)
            scenarios_index = scenarios / "index.html"
            if scenarios_index.exists():
                copy_rendered_doc(scenarios_index, DIST / "scenarios.html")
        for name in ["llms.txt", "ai.txt"]:
            src = DOCS / name
            if src.exists():
                shutil.copy2(src, DIST / name)
    write_search_files()
    print(f"manifest {manifest['manifest_version']} → dist/manifest.json  (CNAME: {CUSTOM_DOMAIN})")


if __name__ == "__main__":
    main()
