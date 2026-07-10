CREATE TABLE IF NOT EXISTS arcade_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  received_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  game TEXT NOT NULL,
  version TEXT NOT NULL,
  type TEXT NOT NULL,
  session_id TEXT NOT NULL,
  source TEXT NOT NULL,
  floor INTEGER,
  cause TEXT,
  elapsed_ms INTEGER,
  payload TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_arcade_events_game_type_time
  ON arcade_events(game, type, received_at);

CREATE INDEX IF NOT EXISTS idx_arcade_events_session
  ON arcade_events(session_id);
