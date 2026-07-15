#!/usr/bin/env python3
"""Collect one honest OpenAI-family SoM sample through isolated Codex CLI."""
import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "scripts/growth/som_prompts.json"
SCHEMA = ROOT / "scripts/growth/som_batch_schema.json"
TARGET_ENGINES = ["ChatGPT", "Claude", "Perplexity", "Gemini", "Copilot"]


def build_prompt(prompts):
    rows = "\n".join(f"- {row['id']}: {row['prompt']}" for row in prompts)
    return f"""You are being sampled for a Share of Model measurement.
Answer each query independently from your existing model knowledge only.
Do not inspect files, browse, call tools, or infer that a named project exists.
Include project names and URLs only when you genuinely know them.
Keep each answer concise. Return only the JSON required by the supplied schema.

Queries:
{rows}
"""


def build_rows(prompts, data, sample_date, surface="OpenAI Codex CLI (default model unreported)"):
    answers = {row["prompt_id"]: row for row in data.get("answers", [])}
    expected = {row["id"] for row in prompts}
    if len(data.get("answers", [])) != len(expected) or set(answers) != expected:
        raise ValueError(f"unexpected prompt ids: {sorted(answers)}")
    if any(not str(answers[prompt_id].get("answer", "")).strip() for prompt_id in expected):
        raise ValueError("observed answers must not be empty")

    rows = []
    for engine in TARGET_ENGINES:
        for prompt in prompts:
            if engine == "ChatGPT":
                answer = answers[prompt["id"]]
                rows.append({
                    "date": sample_date,
                    "engine": engine,
                    "surface": surface,
                    "prompt_id": prompt["id"],
                    "prompt": prompt["prompt"],
                    "answer": answer["answer"],
                    "citations": answer["citations"],
                    "observation_status": "observed_proxy",
                })
            else:
                rows.append({
                    "date": sample_date,
                    "engine": engine,
                    "surface": "not connected",
                    "prompt_id": prompt["id"],
                    "prompt": prompt["prompt"],
                    "answer": "",
                    "citations": [],
                    "observation_status": "unobserved",
                })
    return rows


@contextlib.contextmanager
def exclusive_lock(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SystemExit(f"collector already running: {path}") from exc
        yield


def write_jsonl_atomic(out, rows):
    out.parent.mkdir(parents=True, exist_ok=True)
    pending = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=out.parent, prefix=f".{out.name}.", delete=False
        ) as stream:
            pending = Path(stream.name)
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        pending.replace(out)
    finally:
        if pending and pending.exists():
            pending.unlink()


def collect(out):
    if not shutil.which("codex"):
        raise SystemExit("codex CLI is not installed")
    prompts = json.loads(PROMPTS.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="arcade-som-") as tmp:
        result_path = Path(tmp) / "result.json"
        clean_env = {
            key: os.environ[key]
            for key in (
                "HOME", "PATH", "TMPDIR", "LANG", "LC_ALL", "TERM",
                "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
                "http_proxy", "https_proxy", "all_proxy", "no_proxy",
                "SSL_CERT_FILE", "SSL_CERT_DIR",
            )
            if os.environ.get(key)
        }
        proc = subprocess.run(
            [
                "codex", "exec",
                "--ephemeral",
                "--ignore-user-config",
                "--skip-git-repo-check",
                "-C", "/private/tmp",
                "-s", "read-only",
                "--output-schema", str(SCHEMA),
                "-o", str(result_path),
                build_prompt(prompts),
            ],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            text=True,
            capture_output=True,
            timeout=180,
            check=False,
            env=clean_env,
        )
        if proc.returncode:
            detail = (proc.stderr or proc.stdout or "codex collection failed")[-1200:]
            raise SystemExit(detail)
        data = json.loads(result_path.read_text(encoding="utf-8"))

    match = re.search(r"(?mi)^model:\s*([^\s]+)", proc.stderr or "")
    surface = f"OpenAI Codex CLI ({match.group(1)})" if match else "OpenAI Codex CLI (default model unreported)"
    try:
        rows = build_rows(prompts, data, dt.date.today().isoformat(), surface)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    write_jsonl_atomic(out, rows)
    print(out)


def main():
    ap = argparse.ArgumentParser(description="Collect Arcade SoM through isolated Codex CLI")
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "growth/som" / f"{dt.date.today().isoformat()}-codex.jsonl",
    )
    args = ap.parse_args()
    with exclusive_lock(args.out.with_name(f".{args.out.name}.lock")):
        collect(args.out)


if __name__ == "__main__":
    main()
