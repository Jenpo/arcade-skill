#!/usr/bin/env python3
"""Reusable local-first review bridge for growth scripts."""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL_LLM = ROOT / "scripts/local_llm.py"


def run_local_review(task, text, max_tokens=700, review_model=False, timeout=180):
    cmd = [
        sys.executable,
        str(LOCAL_LLM),
        task,
        "--json",
        "--max-tokens",
        str(max_tokens),
        "--timeout",
        str(max(1, timeout - 15)),
    ]
    if review_model:
        cmd.append("--review-model")
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            input=text,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "LOCAL_LLM_UNAVAILABLE",
            "reason": "local review timed out",
            "fallback": "blocked: no automatic paid API fallback",
        }
    try:
        result = json.loads(proc.stdout)
    except json.JSONDecodeError:
        detail = (proc.stderr or proc.stdout or "no output").strip()[-400:]
        return {
            "status": "LOCAL_LLM_UNAVAILABLE",
            "reason": f"invalid local review response: {detail}",
            "fallback": "blocked: no automatic paid API fallback",
        }
    if proc.returncode and result.get("status") == "PASS":
        result["status"] = "LOCAL_LLM_UNAVAILABLE"
        result["reason"] = f"local helper exited {proc.returncode}"
    return result


def review_markdown(heading, result):
    status = result.get("status", "LOCAL_LLM_UNAVAILABLE")
    lines = [
        f"## {heading}",
        "",
        f"Generated: {dt.datetime.now(dt.UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
        f"- Status: `{status}`",
    ]
    if result.get("model"):
        lines.append(f"- Model: `{result['model']}`")
    if result.get("reason"):
        lines.append(f"- Reason: {result['reason']}")
    lines.append("")
    if result.get("content"):
        lines.extend([result["content"].strip(), ""])
    else:
        lines.extend([
            "No paid API fallback was used. Deterministic scoring remains the",
            "source of truth until the local route is available.",
            "",
        ])
    return "\n".join(lines)


def append_review(path, heading, result):
    with path.open("a", encoding="utf-8") as stream:
        stream.write("\n" + review_markdown(heading, result))


def write_review(path, heading, result):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"# Arcade Skill Local Review\n\n{review_markdown(heading, result)}",
        encoding="utf-8",
    )
