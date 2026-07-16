#!/usr/bin/env python3
"""Offline fault-injection checks for launcher bundle mirrors."""
import hashlib
import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAUNCHER_PATH = ROOT / "skill/scripts/launcher.py"


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def load_launcher():
    spec = importlib.util.spec_from_file_location("arcade_launcher_test", LAUNCHER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    launcher = load_launcher()
    good = b"verified bundle"
    digest = hashlib.sha256(good).hexdigest()
    calls = []

    def fake_fetch(url, timeout=4):
        calls.append(url)
        return b"tampered" if "primary.example" in url else good

    with tempfile.TemporaryDirectory(prefix="arcade-launcher-") as tmp:
        cache = Path(tmp)
        launcher.CACHE = cache
        launcher.fetch = fake_fetch
        launcher.ALLOWED_BUNDLE_HOSTS = {"primary.example", "mirror.example"}
        game = {
            "id": "tower100",
            "version": "test",
            "sha256": digest,
            "entry": "https://primary.example/tower.html",
            "entries": [
                "https://primary.example/tower.html",
                "https://evil.example/tower.html",
                "https://mirror.example/tower.html",
                "https://mirror.example/tower.html",
            ],
        }
        result = launcher.ensure_bundle(game, True)
        require(result.read_bytes() == good, "verified mirror was not installed")
        require(len(calls) == 2, "mirror order or deduplication failed")
        require(not list((cache / "bundles").glob("*.tmp")), "temporary download leaked")

        legacy = {**game, "version": "legacy", "entries": []}
        require(launcher.entry_urls(legacy) == [legacy["entry"]], "legacy entry compatibility failed")
        malformed = {**legacy, "entries": "https://mirror.example/tower.html"}
        require(launcher.entry_urls(malformed) == [legacy["entry"]], "non-list entries must be ignored")
        try:
            launcher.validate_entry_url("https://evil.example/tower.html")
        except ValueError:
            pass
        else:
            raise SystemExit("bundle host allowlist failed")

    print("launcher fallback ok: legacy entry, mirror order, dedupe, sha256, cleanup, allowlist")


if __name__ == "__main__":
    main()
