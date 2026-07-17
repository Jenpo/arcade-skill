const REPO = "Jenpo/arcade-skill";
const PAGES_PROJECT = "arcade-skill";

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

function requireEnv(env, names) {
  const missing = names.filter((name) => !env[name]);
  if (missing.length) throw new Error(`Missing worker configuration: ${missing.join(", ")}`);
}

async function dispatchGitHubRollback(env, ref) {
  requireEnv(env, ["GITHUB_ROLLBACK_TOKEN"]);
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

async function findProductionDeployment(env, shortId) {
  requireEnv(env, ["CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_PAGES_TOKEN"]);
  const url = new URL(
    `https://api.cloudflare.com/client/v4/accounts/${env.CLOUDFLARE_ACCOUNT_ID}/pages/projects/${PAGES_PROJECT}/deployments`,
  );
  url.searchParams.set("env", "production");
  url.searchParams.set("per_page", "25");
  const response = await fetch(url, {
    headers: {"authorization": `Bearer ${env.CLOUDFLARE_PAGES_TOKEN}`},
  });
  if (!response.ok) throw new Error(`Cloudflare deployment lookup failed: ${response.status}`);
  const payload = await response.json();
  const matches = (payload.result || []).filter(
    (deployment) => deployment.environment === "production"
      && deployment.latest_stage?.status === "success"
      && String(deployment.id || "").startsWith(shortId),
  );
  if (matches.length !== 1) throw new Error(`Cloudflare rollback target is not unique: ${shortId}`);
  return matches[0].id;
}

async function rollbackCloudflareProduction(env, shortId) {
  const deploymentId = await findProductionDeployment(env, shortId);
  const response = await fetch(
    `https://api.cloudflare.com/client/v4/accounts/${env.CLOUDFLARE_ACCOUNT_ID}/pages/projects/${PAGES_PROJECT}/deployments/${deploymentId}/rollback`,
    {
      method: "POST",
      headers: {"authorization": `Bearer ${env.CLOUDFLARE_PAGES_TOKEN}`},
    },
  );
  if (!response.ok) throw new Error(`Cloudflare rollback failed: ${response.status}`);
  return deploymentId;
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

function callbackScope(query, env) {
  requireEnv(env, ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "TELEGRAM_ALLOWED_USER_IDS"]);
  const chatId = String(query.message?.chat?.id ?? "");
  const userId = String(query.from?.id ?? "");
  const allowedUsers = env.TELEGRAM_ALLOWED_USER_IDS.split(",").map((value) => value.trim()).filter(Boolean);
  return {
    chatAllowed: chatId === String(env.TELEGRAM_CHAT_ID),
    userAllowed: allowedUsers.includes(userId),
  };
}

async function consumeButton(env, query) {
  const chatId = query.message?.chat?.id;
  const messageId = query.message?.message_id;
  if (chatId === undefined || messageId === undefined) return;
  await telegram(env, "editMessageReplyMarkup", {
    chat_id: chatId,
    message_id: messageId,
    reply_markup: {inline_keyboard: []},
  });
}

async function handleCallback(update, env) {
  const query = update.callback_query;
  if (!query || typeof query.data !== "string") return json({ok: true, ignored: true});
  let scope;
  try {
    scope = callbackScope(query, env);
  } catch {
    return json({ok: false, error: "authorization_not_configured"}, 503);
  }
  if (!scope.chatAllowed || !scope.userAllowed) {
    return json({ok: false, error: "forbidden"}, 403);
  }
  const [action, kind, ref, fallbackRef] = query.data.split(":", 4);
  const validSite = kind === "site" && /^[a-f0-9]{8}$/.test(ref || "") && /^[a-f0-9]{7,40}$/.test(fallbackRef || "");
  const validGitHub = kind === "github" && /^[a-f0-9]{7,40}$/.test(ref || "") && !fallbackRef;
  const validOwned = (kind === "x" || kind === "jike") && /^[A-Za-z0-9._-]{1,40}$/.test(ref || "") && !fallbackRef;
  if (action !== "rollback" || !(validSite || validGitHub || validOwned)) {
    await telegram(env, "answerCallbackQuery", {callback_query_id: query.id, text: "Invalid rollback request"});
    return json({ok: false, error: "bad_callback"}, 400);
  }
  try {
    let deploymentId = "";
    if (kind === "site") {
      deploymentId = await rollbackCloudflareProduction(env, ref);
      await dispatchGitHubRollback(env, fallbackRef);
    }
    else if (kind === "github") await dispatchGitHubRollback(env, ref);
    else if (kind === "x" || kind === "jike") await dispatchOwnedRollback(env, kind, ref);
    else throw new Error("unsupported rollback kind");
    await consumeButton(env, query);
    await telegram(env, "answerCallbackQuery", {
      callback_query_id: query.id,
      text: `Rollback queued: ${kind}`,
      show_alert: true,
    });
    return json({ok: true, kind, ref, fallback_ref: fallbackRef || null, deployment_id: deploymentId || null});
  } catch (error) {
    await telegram(env, "answerCallbackQuery", {
      callback_query_id: query.id,
      text: "Rollback failed. Check the live-check Worker logs.",
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
