#!/usr/bin/env bash
# One-shot publisher for arcade-skill.
# Prereq: git + GitHub CLI (`gh auth login` done once). macOS & Linux compatible.
#
#   ./publish.sh <github-username> [repo-name]
#
set -euo pipefail
if [ $# -lt 1 ]; then
  echo "usage: ./publish.sh <github-username> [repo-name]" >&2
  exit 2
fi
USER=$1
REPO=${2:-arcade-skill}
RELEASE_TAG=${ARCADE_RELEASE_TAG:-v1.2.0}
cd "$(dirname "$0")"

echo "==> 1/6 baking manifest URL for github.com/$USER/$REPO"
FILES=$(grep -rl "REPLACE_ME_GITHUB_USER" skill scripts README.md .github 2>/dev/null || true)
if [ -n "$FILES" ]; then
  echo "$FILES" | xargs sed -i.bak "s/REPLACE_ME_GITHUB_USER/$USER/g"
  find . -name "*.bak" -delete
fi
FILES=$(grep -rl "Jenpo" skill scripts README.md .github publish.sh 2>/dev/null || true)
if [ -n "$FILES" ]; then
  echo "$FILES" | xargs sed -i.bak "s/Jenpo/$USER/g"
  find . -name "*.bak" -delete
fi

echo "==> 2/6 building dist/ (bundles + manifest + seed sync)"
python3 scripts/build_manifest.py

echo "==> 3/6 packaging arcade.skill"
python3 scripts/package_skill.py

echo "==> 4/6 git init + push"
if [ ! -d .git ]; then
  git init
  git checkout -B main
fi
git add -A
git commit -m "M1: tower100 + hot-update thin-shell loader" || echo "(nothing new to commit)"
if ! gh repo view "$USER/$REPO" >/dev/null 2>&1; then
  gh repo create "$USER/$REPO" --public --source . --push \
    --description "Mini-games while you wait for Claude Code / Codex. Thin-shell skill + hot-updated bundles."
else
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "https://github.com/$USER/$REPO.git"
  git push -u origin main
fi

echo "==> 5/6 enabling independent GitHub Pages fallback"
gh api "repos/$USER/$REPO/pages" -X POST -f build_type=workflow >/dev/null 2>&1 \
  || gh api "repos/$USER/$REPO/pages" -X PUT -f build_type=workflow >/dev/null 2>&1 \
  || echo "    (Pages may already be enabled — check Settings→Pages shows 'GitHub Actions')"
echo "    Keep Pages custom domain empty; arcade.fxpeek.com is served by Cloudflare."

echo "==> 6/6 creating release $RELEASE_TAG with arcade.skill"
gh release create "$RELEASE_TAG" arcade.skill \
  --repo "$USER/$REPO" --title "$RELEASE_TAG — verified bundle mirrors" \
  --notes "Loader v1.2 retries Cloudflare, GitHub Pages, raw GitHub, and jsDelivr mirrors with SHA-256 verification. Existing game content remains hot-updatable." \
  2>/dev/null || echo "    (release $RELEASE_TAG already exists — skipping)"

echo
echo "Done. Verify in ~1 min (first Pages deploy):"
echo "  curl -s https://$USER.github.io/$REPO/manifest.json | head -5"
echo "  python3 skill/scripts/launcher.py --no-open   # should log 'manifest ... from ...github.io'"
