#!/usr/bin/env python3
"""Install the Arcade runtime artifact layout backed by the S volume."""
import argparse
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ARTIFACT_ROOT = Path(
    os.environ.get(
        "ARCADE_ARTIFACT_ROOT",
        "/Volumes/S/Workplace/Codex-Workdir/arcade-skill/current",
    )
)

MAPPINGS = {
    Path("growth/som"): Path("input/som"),
    Path("growth/reports"): Path("reports"),
    Path("growth/drafts"): Path("work/drafts"),
    Path("growth/queue"): Path("work/queue"),
    Path("growth/state"): Path("work/state"),
    Path("growth/radar"): Path("work/radar"),
    Path("growth/smoke"): Path("tmp/smoke"),
}


def install(repo_root: Path, artifact_root: Path):
    if not artifact_root.exists():
        raise SystemExit(
            f"Artifact root is unavailable: {artifact_root}. "
            "Mount the S volume or set ARCADE_ARTIFACT_ROOT."
        )
    for relative_link, relative_target in MAPPINGS.items():
        link = repo_root / relative_link
        target = artifact_root / relative_target
        target.mkdir(parents=True, exist_ok=True)
        link.parent.mkdir(parents=True, exist_ok=True)

        if link.is_symlink():
            if link.resolve() != target.resolve():
                raise SystemExit(f"Refusing to replace mismatched symlink: {link}")
            print(f"OK {link} -> {target}")
            continue
        if link.exists():
            if not link.is_dir() or any(link.iterdir()):
                raise SystemExit(f"Refusing to replace non-empty path: {link}")
            link.rmdir()
        link.symlink_to(target, target_is_directory=True)
        print(f"LINK {link} -> {target}")


def main():
    parser = argparse.ArgumentParser(description="Install Arcade S-volume artifact links")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    args = parser.parse_args()
    install(args.repo_root.resolve(), args.artifact_root)


if __name__ == "__main__":
    main()
