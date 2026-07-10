# Arcade Telemetry Worker

Minimal Cloudflare Worker + D1 receiver for `tower100` event telemetry.

It answers the missing product loop: where players die, how long a session lasts,
whether people replay, and which share/tip hooks fire.

## Events

The game emits compact JSON:

```json
{
  "arcade": true,
  "game": "tower100",
  "version": "1.4.0",
  "type": "game_over",
  "session_id": "abc123",
  "source": "skill",
  "mode": "daily",
  "seed": 20260710,
  "ts": 1783690000000,
  "elapsed_ms": 42000,
  "data": {"floor": 37, "cause": "hp"}
}
```

## Deploy Sketch

```bash
cd infra/telemetry-worker
wrangler d1 create arcade_telemetry
wrangler d1 execute arcade_telemetry --file schema.sql --remote
wrangler deploy --domain telemetry.fxpeek.com
```

Then point the manifest telemetry config at:

`https://telemetry.fxpeek.com/event`

Keep this endpoint anonymous, low-cardinality, and free of personal data.
