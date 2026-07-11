#!/usr/bin/env bash
# Deploy the current dist/ folder to Cloudflare Pages production.
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/build_manifest.py
npx wrangler pages deploy dist --project-name arcade-skill --branch main
