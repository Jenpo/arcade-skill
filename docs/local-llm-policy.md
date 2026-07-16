# Local LLM Policy

Arcade Skill ops are local-first by default.

Use the local LiteLLM router for design review, landing-page copy, SEO/GEO
draft critique, radar opportunity classification, weekly summaries, and
non-realtime planning.

Use API models only when current external information is required, production
diagnostics require provider-specific reasoning, the local route is unavailable
and the operator accepts the cost, or the user explicitly asks for an API-backed
answer.

No script in this repo silently falls back to a paid API.

## Router

Default OpenAI-compatible endpoint:

```text
http://192.168.31.68:4000/v1
```

`scripts/local_llm.py` opens this private endpoint directly and deliberately
ignores inherited HTTP/SOCKS proxy variables. This prevents a desktop proxy from
returning a misleading 502 for a healthy LAN router. External model traffic is
not routed through this helper.

Default aliases:

- `s8_local_fast_v1` for lightweight copy, radar, and smoke tasks
- `s8_local_main_v1` for review and higher-context critique

## Environment

Set one of:

```bash
export ARCADE_LOCAL_LLM_API_KEY=...
export LITELLM_MASTER_KEY=...
export S8_LLM_ROUTER_KEY=...
```

On the Mac scheduler, the helper also reads the existing local-only key file at
`~/Library/Application Support/S8/.litellm_master_key`. Override its location
with `ARCADE_LOCAL_LLM_KEY_FILE`; the key is never copied into the repository.

Optional overrides:

```bash
export ARCADE_LOCAL_LLM_BASE_URL=http://192.168.31.68:4000/v1
export ARCADE_LOCAL_LLM_MODEL=s8_local_fast_v1
export ARCADE_LOCAL_LLM_REVIEW_MODEL=s8_local_main_v1
```

## Usage

```bash
python3 scripts/local_llm.py design-review --input docs/scenarios/index.html
python3 scripts/local_llm.py seo --input docs/scenarios/games-while-ai-agent-runs-tests/index.html
python3 scripts/local_llm.py copy --input docs/DESIGN.md
```

If no local router key is present, the command returns `LOCAL_LLM_PENDING`
instead of calling a remote API.

The mention radar and SEO page factory call this local review layer by default
after their deterministic checks:

```bash
python3 scripts/growth/mention_radar.py --offline
python3 scripts/growth/seo_page_factory.py --dry-run
```

Their generated reports record `PASS`, `LOCAL_LLM_PENDING`, or
`LOCAL_LLM_UNAVAILABLE`. Use `--no-llm-review` only for an explicitly
deterministic-only run. No status triggers an automatic paid API fallback.
