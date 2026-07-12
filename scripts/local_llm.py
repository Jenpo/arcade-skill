#!/usr/bin/env python3
"""Local-first LLM helper for Arcade Skill ops."""
import argparse
import json
import os
import sys
import urllib.request

DEFAULT_BASE_URL = os.environ.get("ARCADE_LOCAL_LLM_BASE_URL", "http://192.168.31.68:4000/v1")
DEFAULT_MODEL = os.environ.get("ARCADE_LOCAL_LLM_MODEL", "s8_local_fast_v1")
DEFAULT_REVIEW_MODEL = os.environ.get("ARCADE_LOCAL_LLM_REVIEW_MODEL", "s8_local_main_v1")
KEY_ENV_NAMES = ["ARCADE_LOCAL_LLM_API_KEY", "LITELLM_MASTER_KEY", "S8_LLM_ROUTER_KEY"]

TASK_PROMPTS = {
    "design-review": "你是严苛但务实的网页设计评审。只输出最值得改的3点、不要改的2点、可执行建议。",
    "copy": "你是偏极客、复古、克制的产品文案编辑。保留事实，不制造未实现功能，不写付费买优势。",
    "seo": "你是SEO/GEO草稿审稿人。检查搜索意图、重复度风险、FAQ结构、真实数据点和垃圾页风险。",
    "radar": "你是社区增长雷达评审。判断是否值得人工回复或提PR；必须透明披露maker身份，禁止自动发布。",
}


def api_key():
    for name in KEY_ENV_NAMES:
        value = os.environ.get(name)
        if value:
            return value
    return ""


def read_input(path):
    if path:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def post_json(url, payload, key, timeout):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def chat(args, prompt):
    key = api_key()
    if not key and not args.allow_no_auth:
        return {
            "status": "LOCAL_LLM_PENDING",
            "reason": "missing local router key",
            "expected_env": KEY_ENV_NAMES,
            "base_url": args.base_url,
            "model": args.model,
        }
    payload = {
        "model": args.model,
        "messages": [
            {"role": "system", "content": TASK_PROMPTS[args.task]},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "extra_body": {"reasoning_effort": False},
    }
    try:
        data = post_json(args.base_url.rstrip("/") + "/chat/completions", payload, key, args.timeout)
    except Exception as exc:
        return {
            "status": "LOCAL_LLM_UNAVAILABLE",
            "reason": str(exc),
            "base_url": args.base_url,
            "model": args.model,
            "fallback": "blocked: no automatic paid API fallback",
        }
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    content = (message.get("content") or "").strip()
    if not content:
        return {
            "status": "LOCAL_LLM_EMPTY",
            "reason": "empty message.content; check Qwen/LiteLLM reasoning_content routing",
            "model": data.get("model") or args.model,
        }
    return {"status": "PASS", "model": data.get("model") or args.model, "content": content}


def main():
    ap = argparse.ArgumentParser(description="Arcade local-first LLM helper")
    ap.add_argument("task", choices=sorted(TASK_PROMPTS.keys()))
    ap.add_argument("--input", help="input text file; defaults to stdin")
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--review-model", action="store_true", help="use the main review model")
    ap.add_argument("--max-tokens", type=int, default=900)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--allow-no-auth", action="store_true", help="try the router without Authorization")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.review_model:
        args.model = DEFAULT_REVIEW_MODEL
    prompt = read_input(args.input).strip()
    if not prompt:
        raise SystemExit("empty prompt")
    result = chat(args, prompt)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif result["status"] == "PASS":
        print(result["content"])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] not in {"PASS", "LOCAL_LLM_PENDING"}:
        sys.exit(1)


if __name__ == "__main__":
    main()
