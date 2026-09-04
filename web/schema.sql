-- prepmyproperty.tech submissions
--
-- One row per person who asked for an assessment. Answers are stored as JSON
-- because the five questions will change, and a JSON column survives that
-- without a migration. The columns that must never change are the ones the
-- privacy notice makes promises about: created_at drives the 24-month
-- retention, and consent records that permission was actually given.

CREATE TABLE IF NOT EXISTS submissions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at  TEXT    NOT NULL,          -- ISO 8601 UTC, drives retention
  due_date    TEXT    NOT NULL,          -- the date promised on screen
  address     TEXT    NOT NULL,
  email       TEXT    NOT NULL,
  answers     TEXT    NOT NULL,          -- JSON
  consent     INTEGER NOT NULL DEFAULT 0,
  country     TEXT,
  user_agent  TEXT,
  status      TEXT    NOT NULL DEFAULT 'new',   -- new | sent | bounced | deleted
  sent_at     TEXT
);

-- What is due, oldest first. This is the work queue.
CREATE INDEX IF NOT EXISTS idx_status_due ON submissions(status, due_date);

-- For finding someone who emails asking to be deleted.
CREATE INDEX IF NOT EXISTS idx_email ON submissions(email);
