const REPO = "Jenpo/arcade-skill";

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {"content-type": "application/json; charset=utf-8"},
  });
}

async function telegram(env, method, payload) {
  const response = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/${method}`, {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`Telegram ${method} failed: ${response.status}`);
  return response.json();
}

async function dispatchSiteRollback(env, ref) {
  const response = await fetch(
    `https://api.github.com/repos/${REPO}/actions/workflows/rollback.yml/dispatches`,
    {
      method: "POST",
      headers: {
        "accept": "application/vnd.github+json",
        "authorization": `Bearer ${env.GITHUB_ROLLBACK_TOKEN}`,
        "content-type": "application/json",
        "user-agent": "arcade-live-check-worker",
        "x-github-api-version": "2022-11-28",
      },
      body: JSON.stringify({ref: "main", inputs: {target_ref: ref}}),
    },
  );
  if (response.status !== 204) {
    throw new Error(`GitHub rollback dispatch failed: ${response.status}`);
  }
}

async function dispatchOwnedRollback(env, channel, postId) {
  if (!env.OWN_CHANNEL_ROLLBACK_URL || !env.OWN_CHANNEL_ROLLBACK_TOKEN) {
    throw new Error(`${channel} rollback webhook is not configured`);
  }
  const response = await fetch(env.OWN_CHANNEL_ROLLBACK_URL, {
    method: "POST",
    headers: {
      "authorization": `Bearer ${env.OWN_CHANNEL_ROLLBACK_TOKEN}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({channel, post_id: postId, source: "arcade-live-check"}),
  });
  if (!response.ok) throw new Error(`${channel} rollback webhook failed: ${response.status}`);
}

async function handleCallback(update, env) {
  const query = update.callback_query;
  if (!query || typeof query.data !== "string") return json({ok: true, ignored: true});
  const [action, kind, ref] = query.data.split(":", 3);
  if (action !== "rollback" || !kind || !/^[A-Za-z0-9._-]{1,40}$/.test(ref || "")) {
    await telegram(env, "answerCallbackQuery", {callback_query_id: query.id, text: "Invalid rollback request"});
    return json({ok: false, error: "bad_callback"}, 400);
  }
  try {
    if (kind === "site") await dispatchSiteRollback(env, ref);
    else if (kind === "x" || kind === "jike") await dispatchOwnedRollback(env, kind, ref);
    else throw new Error("unsupported rollback kind");
    await telegram(env, "answerCallbackQuery", {
      callback_query_id: query.id,
      text: `Rollback queued: ${kind}`,
      show_alert: true,
    });
    return json({ok: true, kind, ref});
  } catch (error) {
    await telegram(env, "answerCallbackQuery", {
      callback_query_id: query.id,
      text: String(error.message || error).slice(0, 180),
      show_alert: true,
    });
    return json({ok: false, error: "rollback_failed"}, 502);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({ok: true, service: "arcade-live-check"});
    }
    if (request.method !== "POST" || url.pathname !== "/telegram/webhook") {
      return json({ok: false, error: "not_found"}, 404);
    }
    if (request.headers.get("x-telegram-bot-api-secret-token") !== env.TELEGRAM_WEBHOOK_SECRET) {
      return json({ok: false, error: "unauthorized"}, 401);
    }
    let update;
    try {
      update = await request.json();
    } catch {
      return json({ok: false, error: "bad_json"}, 400);
    }
    return handleCallback(update, env);
  },
};
