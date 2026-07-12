# Arcade Live Check Worker

Telegram callback receiver for Tier A rollback buttons.

Routes:

- `GET /health`
- `POST /telegram/webhook`

Required Worker secrets:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_WEBHOOK_SECRET
GITHUB_ROLLBACK_TOKEN
```

Optional owned-channel rollback bridge:

```text
OWN_CHANNEL_ROLLBACK_URL
OWN_CHANNEL_ROLLBACK_TOKEN
```

The GitHub token must be scoped only to `Jenpo/arcade-skill` with Actions write
permission. The Worker never accepts a target repository from Telegram input.

After deployment, register the bot webhook with Telegram using the Worker URL
and the same `TELEGRAM_WEBHOOK_SECRET`. Do not put any secret in `wrangler.toml`
or Git.
