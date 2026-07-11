-- Weekly P5 telemetry rollup for Arcade Skill.
-- Run with:
-- npx wrangler d1 execute arcade_telemetry --remote --file scripts/growth/telemetry_summary.sql

SELECT 'events_last_7d' AS metric, COUNT(*) AS value
FROM arcade_events
WHERE received_at >= datetime('now', '-7 days');

SELECT source, type, COUNT(*) AS events
FROM arcade_events
WHERE received_at >= datetime('now', '-7 days')
GROUP BY source, type
ORDER BY events DESC;

SELECT
  COUNT(*) AS game_overs,
  COALESCE(ROUND(AVG(floor), 1), 0) AS avg_floor,
  COALESCE(MAX(floor), 0) AS best_floor,
  COALESCE(ROUND(AVG(elapsed_ms) / 1000.0, 1), 0) AS avg_seconds
FROM arcade_events
WHERE type = 'game_over'
  AND received_at >= datetime('now', '-7 days');

SELECT floor, COUNT(*) AS deaths
FROM arcade_events
WHERE type = 'game_over'
  AND floor IS NOT NULL
  AND received_at >= datetime('now', '-7 days')
GROUP BY floor
ORDER BY deaths DESC, floor ASC
LIMIT 20;

SELECT
  COALESCE(SUM(CASE WHEN type = 'share' THEN 1 ELSE 0 END), 0) AS shares,
  COALESCE(SUM(CASE WHEN type = 'tip_click' THEN 1 ELSE 0 END), 0) AS tip_clicks,
  COALESCE(SUM(CASE WHEN type = 'game_over' THEN 1 ELSE 0 END), 0) AS game_overs
FROM arcade_events
WHERE received_at >= datetime('now', '-7 days');
