import assert from "node:assert/strict";
import fs from "node:fs/promises";
import test from "node:test";

const source = await fs.readFile(new URL("../infra/live-check-worker/src/worker.js", import.meta.url), "utf8");
const worker = (await import(`data:text/javascript;base64,${Buffer.from(source).toString("base64")}`)).default;

const baseEnv = {
  TELEGRAM_BOT_TOKEN: "test-bot-token",
  TELEGRAM_WEBHOOK_SECRET: "test-webhook-secret",
  TELEGRAM_CHAT_ID: "-100123",
  TELEGRAM_ALLOWED_USER_IDS: "42,84",
  GITHUB_ROLLBACK_TOKEN: "test-github-token",
  CLOUDFLARE_ACCOUNT_ID: "account123",
  CLOUDFLARE_PAGES_TOKEN: "test-pages-token",
};

function webhook(data, secret = baseEnv.TELEGRAM_WEBHOOK_SECRET) {
  return new Request("https://worker.example/telegram/webhook", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-telegram-bot-api-secret-token": secret,
    },
    body: JSON.stringify({
      callback_query: {
        id: "callback-1",
        data,
        from: {id: 42},
        message: {message_id: 9, chat: {id: -100123}},
      },
    }),
  });
}

function mockFetch() {
  const calls = [];
  globalThis.fetch = async (input, options = {}) => {
    const url = String(input);
    calls.push({url, options});
    if (url.includes("api.telegram.org")) {
      return new Response(JSON.stringify({ok: true, result: {}}), {
        status: 200,
        headers: {"content-type": "application/json"},
      });
    }
    if (url.includes("api.cloudflare.com") && !url.endsWith("/rollback")) {
      return new Response(JSON.stringify({
        success: true,
        result: [{
          id: "26fb917c-3940-4ce8-9b31-ecddb10fce7c",
          environment: "production",
          latest_stage: {status: "success"},
        }],
      }), {status: 200, headers: {"content-type": "application/json"}});
    }
    if (url.endsWith("/rollback")) {
      return new Response(JSON.stringify({success: true}), {
        status: 200,
        headers: {"content-type": "application/json"},
      });
    }
    if (url.includes("api.github.com")) return new Response(null, {status: 204});
    throw new Error(`unexpected fetch: ${url}`);
  };
  return calls;
}

test("webhook rejects the wrong Telegram secret", async () => {
  const calls = mockFetch();
  const response = await worker.fetch(webhook("rollback:github:a532983", "wrong"), baseEnv);
  assert.equal(response.status, 401);
  assert.equal(calls.length, 0);
});

test("callback rejects an unapproved Telegram user", async () => {
  const calls = mockFetch();
  const body = await webhook("rollback:github:a532983").json();
  body.callback_query.from.id = 99;
  const request = new Request("https://worker.example/telegram/webhook", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-telegram-bot-api-secret-token": baseEnv.TELEGRAM_WEBHOOK_SECRET,
    },
    body: JSON.stringify(body),
  });
  const response = await worker.fetch(request, baseEnv);
  assert.equal(response.status, 403);
  assert.equal(calls.length, 0);
});

test("site callback rolls back Cloudflare and queues GitHub fallback", async () => {
  const calls = mockFetch();
  const response = await worker.fetch(webhook("rollback:site:26fb917c:a532983"), baseEnv);
  const payload = await response.json();
  assert.equal(response.status, 200);
  assert.equal(payload.kind, "site");
  assert.equal(payload.deployment_id, "26fb917c-3940-4ce8-9b31-ecddb10fce7c");
  assert.ok(calls.some((call) => call.url.endsWith("/deployments/26fb917c-3940-4ce8-9b31-ecddb10fce7c/rollback")));
  assert.ok(calls.some((call) => call.url.includes("api.github.com/repos/Jenpo/arcade-skill/actions/workflows/rollback.yml/dispatches")));
  assert.ok(calls.some((call) => call.url.endsWith("/editMessageReplyMarkup")));
});

test("site callback refuses an ambiguous Cloudflare deployment prefix", async () => {
  const calls = mockFetch();
  globalThis.fetch = async (input, options = {}) => {
    const url = String(input);
    calls.push({url, options});
    if (url.includes("api.telegram.org")) {
      return new Response(JSON.stringify({ok: true, result: {}}), {
        status: 200,
        headers: {"content-type": "application/json"},
      });
    }
    return new Response(JSON.stringify({
      success: true,
      result: [
        {id: "26fb917c-1111-4111-8111-111111111111", environment: "production", latest_stage: {status: "success"}},
        {id: "26fb917c-2222-4222-8222-222222222222", environment: "production", latest_stage: {status: "success"}},
      ],
    }), {status: 200, headers: {"content-type": "application/json"}});
  };
  const response = await worker.fetch(webhook("rollback:site:26fb917c:a532983"), baseEnv);
  assert.equal(response.status, 502);
  assert.ok(!calls.some((call) => call.url.includes("api.github.com")));
});
