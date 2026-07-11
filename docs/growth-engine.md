# Arcade Growth Engine

The growth model has three layers:

1. Traditional search: focused landing pages, multilingual intros, and clear
   canonical project files.
2. GEO: earn third-party mentions that AI engines can cite.
3. Agent runtime: make the skill easy for coding agents to invoke when users
   are waiting on tests, installs, builds, or diffs.

The operating rule is strict:

Radar can be automated. Publishing stays human-reviewed.

## P4: Share Of Model

SoM is the weekly GEO KPI. Run a fixed prompt set across target AI engines and
record whether Arcade Skill is mentioned and cited.

```bash
python3 scripts/growth/som_tracker.py init
python3 scripts/growth/som_tracker.py score \
  --input growth/som_responses.jsonl \
  --out growth/reports/som-latest.md
```

Fill `growth/som_responses.jsonl` manually or from approved exports. Do not
auto-post or scrape logged-in answers without review.

## P5: Telemetry回流

Use D1 event data to answer:

- where players die
- whether daily mode is used
- whether share and Stripe support hooks fire
- whether hosted web traffic is replacing local-only usage

```bash
npx wrangler d1 execute arcade_telemetry \
  --remote \
  --file scripts/growth/telemetry_summary.sql
```

For a Markdown report:

```bash
python3 scripts/growth/telemetry_report.py \
  --out growth/reports/telemetry-latest.md
```

## Public AI Hints

The site publishes:

- `/llms.txt`
- `/ai.txt`
- `/docs/project-intro.md`
- multilingual intros under `/docs/intro.*.md`

These files are descriptive, not spam pages. Third-party mentions remain the
main GEO fuel.
