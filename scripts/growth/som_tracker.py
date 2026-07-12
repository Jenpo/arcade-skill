#!/usr/bin/env python3
"""Track Share of Model for Arcade Skill.

The script is intentionally manual-input first. It scores exported or pasted
answers from AI engines, but does not automate posting, promotion, or logged-in
scraping.
"""
import argparse, datetime as dt, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "scripts/growth/som_prompts.json"
DEFAULT_INPUT = ROOT / "growth/som_responses.jsonl"
DEFAULT_OUT = ROOT / "growth/reports/som-latest.md"

MENTION_PATTERNS = [
    re.compile(r"\barcade skill\b", re.I),
    re.compile(r"\barcade\.fxpeek\.com\b", re.I),
    re.compile(r"\bgithub\.com/Jenpo/arcade-skill\b", re.I),
    re.compile(r"\bdown 100 floors\b", re.I),
]
CITATION_PATTERNS = [
    re.compile(r"https?://arcade\.fxpeek\.com", re.I),
    re.compile(r"https?://github\.com/Jenpo/arcade-skill", re.I),
]


def load_prompts():
    return json.loads(PROMPTS.read_text(encoding="utf-8"))


def init_file(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    prompts = load_prompts()
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing file: {path}")
    with path.open("w", encoding="utf-8") as f:
        for engine in ["ChatGPT", "Claude", "Perplexity", "Gemini", "Copilot"]:
            for p in prompts:
                row = {
                    "date": dt.date.today().isoformat(),
                    "engine": engine,
                    "prompt_id": p["id"],
                    "prompt": p["prompt"],
                    "answer": "",
                    "citations": []
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(path)


def load_rows(path: Path):
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise SystemExit(f"{path}:{lineno}: bad json: {e}") from e
    return rows


def score_row(row):
    answer = str(row.get("answer", ""))
    citations = " ".join(str(x) for x in row.get("citations", []))
    mentioned = any(p.search(answer) for p in MENTION_PATTERNS)
    cited = any(p.search(answer + " " + citations) for p in CITATION_PATTERNS)
    return mentioned, cited


def score_file(src: Path, out: Path):
    rows = load_rows(src)
    if not rows:
        raise SystemExit(f"no rows in {src}")
    imported = len(rows)
    observed_rows = [
        row for row in rows
        if str(row.get("answer", "")).strip() or any(str(x).strip() for x in row.get("citations", []))
    ]
    if not observed_rows:
        raise SystemExit(f"no observed answers in {src}; refusing to report empty rows as misses")
    scored = []
    for row in observed_rows:
        mentioned, cited = score_row(row)
        scored.append({**row, "mentioned": mentioned, "cited": cited})

    total = len(scored)
    mentions = sum(1 for r in scored if r["mentioned"])
    cites = sum(1 for r in scored if r["cited"])
    by_engine = {}
    imported_by_engine = {}
    for row in rows:
        engine = row.get("engine", "unknown")
        imported_by_engine[engine] = imported_by_engine.get(engine, 0) + 1
    for r in scored:
        bucket = by_engine.setdefault(r.get("engine", "unknown"), [0, 0, 0])
        bucket[0] += 1
        bucket[1] += int(r["mentioned"])
        bucket[2] += int(r["cited"])

    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Arcade Skill Share Of Model",
        "",
        f"Generated: {dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        f"- Prompts imported: {imported}",
        f"- Prompts observed: {total} ({total / imported:.1%} coverage)",
        f"- Mention rate: {mentions}/{total} ({mentions / total:.1%})",
        f"- Citation rate: {cites}/{total} ({cites / total:.1%})",
        "",
        "## By Engine",
        "",
        "| Engine | Imported | Observed | Mentions | Citations |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for engine in sorted(imported_by_engine):
        n, m, c = by_engine.get(engine, [0, 0, 0])
        lines.append(f"| {engine} | {imported_by_engine[engine]} | {n} | {m} | {c} |")
    lines.extend(["", "## Misses To Review", ""])
    for r in scored:
        if not r["mentioned"]:
            lines.append(f"- `{r.get('engine','?')}` / `{r.get('prompt_id','?')}`: no mention")
    unobserved = imported - total
    lines.extend(["", "## Coverage Gaps", "", f"- Unobserved rows: {unobserved}"])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)


def main():
    ap = argparse.ArgumentParser(description="Arcade Skill SoM tracker")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_init = sub.add_parser("init", help="write a blank weekly response file")
    p_init.add_argument("--out", type=Path, default=DEFAULT_INPUT)
    p_score = sub.add_parser("score", help="score a JSONL response file")
    p_score.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    p_score.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    if args.cmd == "init":
        init_file(args.out)
    elif args.cmd == "score":
        score_file(args.input, args.out)


if __name__ == "__main__":
    main()
