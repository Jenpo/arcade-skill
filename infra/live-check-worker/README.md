# Arcade Live Check Worker

Telegram callback receiver for Tier A rollback buttons.

Routes:

- `GET /health`
- `POST /telegram/webhook`

Worker URL: `https://arcade-live-check.fxpeek.workers.dev`

Required Worker secrets:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_WEBHOOK_SECRET
TELEGRAM_CHAT_ID
TELEGRAM_ALLOWED_USER_IDS
GITHUB_ROLLBACK_TOKEN
CLOUDFLARE_PAGES_TOKEN
CLOUDFLARE_ACCOUNT_ID
```

Optional owned-channel rollback bridge:

```text
OWN_CHANNEL_ROLLBACK_URL
OWN_CHANNEL_ROLLBACK_TOKEN
```

Use a dedicated Telegram bot. A bot already owned by Hermes polling cannot also
use this webhook. `TELEGRAM_ALLOWED_USER_IDS` is a comma-separated allowlist;
both the callback chat and the clicking user must match or the Worker fails
closed.

The GitHub token must be scoped only to `Jenpo/arcade-skill` with Actions write
permission. The Cloudflare token must be scoped to Pages Write for the owning
account. A `site` callback carries only an eight-character Cloudflare deployment
prefix and a Git commit prefix. The Worker resolves a unique successful production
deployment, rolls back the Cloudflare primary, then dispatches the GitHub Pages
fallback rollback. Repositories, account IDs, and project names are not accepted
from Telegram input.

After deployment, register the bot webhook with Telegram using the Worker URL
and the same `TELEGRAM_WEBHOOK_SECRET`. Do not put any secret in `wrangler.toml`
or Git.

The interactive provisioner uses hidden input, writes the Mac env with mode
`0600`, streams secrets directly to Wrangler and GitHub, registers the webhook,
and reloads the Tier A LaunchAgents:

```bash
python3 scripts/provision_live_check.py configure
python3 scripts/provision_live_check.py check
```

Never paste credentials into chat or pass them as command-line arguments.
