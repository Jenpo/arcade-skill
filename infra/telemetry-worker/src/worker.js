const MAX_BODY_BYTES = 4096;
const ALLOWED_ORIGINS = new Set([
  "https://arcade.fxpeek.com",
]);

function cors(origin) {
  const allow = ALLOWED_ORIGINS.has(origin) ? origin : "https://arcade.fxpeek.com";
  return {
    "access-control-allow-origin": allow,
    "access-control-allow-methods": "POST, OPTIONS",
    "access-control-allow-headers": "content-type",
    "access-control-max-age": "86400",
  };
}

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {"content-type": "application/json; charset=utf-8", ...headers},
  });
}

function cleanText(value, fallback, max = 80) {
  const s = typeof value === "string" ? value : fallback;
  return s.slice(0, max).replace(/[^\w:./-]/g, "_");
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("origin") || "";
    const headers = cors(origin);
    if (request.method === "OPTIONS") return new Response(null, {status: 204, headers});
    if (request.method !== "POST") return json({ok: false, error: "method_not_allowed"}, 405, headers);
    const len = Number(request.headers.get("content-length") || "0");
    if (len > MAX_BODY_BYTES) return json({ok: false, error: "payload_too_large"}, 413, headers);

    let event;
    try {
      event = await request.json();
    } catch {
      return json({ok: false, error: "bad_json"}, 400, headers);
    }
    if (!event || event.arcade !== true || event.game !== "tower100") {
      return json({ok: false, error: "bad_event"}, 400, headers);
    }

    const type = cleanText(event.type, "unknown", 40);
    const data = event.data && typeof event.data === "object" ? event.data : {};
    const floor = Number.isFinite(Number(data.floor)) ? Math.max(0, Math.min(9999, Number(data.floor))) : null;
    const elapsed = Number.isFinite(Number(event.elapsed_ms)) ? Math.max(0, Math.min(86400000, Number(event.elapsed_ms))) : null;

    await env.DB.prepare(
      `INSERT INTO arcade_events
       (game, version, type, session_id, source, floor, cause, elapsed_ms, payload)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    ).bind(
      "tower100",
      cleanText(event.version, "unknown", 32),
      type,
      cleanText(event.session_id, "missing", 80),
      cleanText(event.source, "unknown", 32),
      floor,
      data.cause ? cleanText(data.cause, "", 32) : null,
      elapsed,
      JSON.stringify(event).slice(0, MAX_BODY_BYTES)
    ).run();

    return json({ok: true}, 200, headers);
  },
};
