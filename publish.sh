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
rm -f arcade.skill
(cd skill && zip -qr ../arcade.skill SKILL.md scripts assets -x "*__pycache__*")

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

echo "==> 5/6 enabling GitHub Pages (build_type: workflow) + custom domain"
gh api "repos/$USER/$REPO/pages" -X POST -f build_type=workflow >/dev/null 2>&1 \
  || gh api "repos/$USER/$REPO/pages" -X PUT -f build_type=workflow >/dev/null 2>&1 \
  || echo "    (Pages may already be enabled — check Settings→Pages shows 'GitHub Actions')"
gh api "repos/$USER/$REPO/pages" -X PUT -f cname=arcade.fxpeek.com >/dev/null 2>&1 \
  || echo "    (set custom domain later in Settings→Pages: arcade.fxpeek.com)"
echo "    REQUIRED DNS: add CNAME record  arcade.fxpeek.com → $USER.github.io"
echo "    then tick 'Enforce HTTPS' in Settings→Pages once the cert issues (~5 min)"

echo "==> 6/6 creating release v1.0.0 with arcade.skill"
gh release create v1.0.0 arcade.skill \
  --repo "$USER/$REPO" --title "v1.0.0 — Down 100 Floors" \
  --notes "First release. Install: unzip arcade.skill into your skills directory. Hot updates arrive automatically via manifest." \
  2>/dev/null || echo "    (release v1.0.0 already exists — skipping)"

echo
echo "Done. Verify in ~1 min (first Pages deploy):"
echo "  curl -s https://$USER.github.io/$REPO/manifest.json | head -5"
echo "  python3 skill/scripts/launcher.py --no-open   # should log 'manifest ... from ...github.io'"
