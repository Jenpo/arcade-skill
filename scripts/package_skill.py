#!/usr/bin/env python3
"""Build arcade.skill atomically from the thin-shell skill directory."""
import hashlib
import os
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skill"
OUT = ROOT / "arcade.skill"
INCLUDE = [SKILL / "SKILL.md", SKILL / "scripts", SKILL / "assets"]


def included_files():
    for source in INCLUDE:
        paths = [source] if source.is_file() else sorted(source.rglob("*"))
        for path in paths:
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc" or path.name == ".DS_Store":
                continue
            yield path


def main():
    with tempfile.NamedTemporaryFile(dir=ROOT, prefix=".arcade.skill.", delete=False) as stream:
        pending = Path(stream.name)
    try:
        with zipfile.ZipFile(pending, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in included_files():
                archive.write(path, path.relative_to(SKILL))
        os.replace(pending, OUT)
    finally:
        pending.unlink(missing_ok=True)
    digest = hashlib.sha256(OUT.read_bytes()).hexdigest()
    print(f"{OUT} {OUT.stat().st_size} bytes sha256={digest}")


if __name__ == "__main__":
    main()
