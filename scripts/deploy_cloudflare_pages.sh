#!/usr/bin/env bash
# Deploy the current dist/ folder to Cloudflare Pages production.
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ "${1:-}" == "--build" ]]; then
  python3 scripts/build_manifest.py
  shift
fi

test -f dist/manifest.json
npx wrangler pages deploy dist --project-name arcade-skill --branch main
