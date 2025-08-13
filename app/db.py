import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from datetime import datetime, timezone
import json

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS jobs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    site            TEXT NOT NULL,
    external_id     TEXT NOT NULL,
    title           TEXT NOT NULL,
    url             TEXT NOT NULL,
    location        TEXT,
    employment_type TEXT,
    posted_at_iso   TEXT,
    first_seen_at   TEXT NOT NULL,
    last_seen_at    TEXT NOT NULL,
    is_active       INTEGER NOT NULL DEFAULT 1,
    metadata_json   TEXT,
    UNIQUE(site, external_id)
);

CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id      INTEGER NOT NULL,
    event_type  TEXT NOT NULL, -- 'new' | 'removed' | 'updated'
    created_at  TEXT NOT NULL,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);
"""

ISO = "%Y-%m-%dT%H:%M:%S%z"

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime(ISO)

class DB:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.executescript(SCHEMA)
        self.conn.commit()

    # --- inserts / updates ---
    def upsert_job(self, rec: Dict) -> Tuple[int, bool]:
        """Insert or update job by (site, external_id).
        Returns: (job_id, is_new)
        """
        metadata_json = json.dumps(rec.get("metadata") or {}, ensure_ascii=False)
        now = now_iso()
        cur = self.conn.cursor()
        # Try update existing
        cur.execute(
            """
            SELECT id FROM jobs WHERE site=? AND external_id=?
            """,
            (rec["site"], rec["external_id"]),
        )
        row = cur.fetchone()
        if row:
            job_id = row["id"]
            cur.execute(
                """
                UPDATE jobs SET
                    title=?, url=?, location=?, employment_type=?, posted_at_iso=?,
                    last_seen_at=?, is_active=1, metadata_json=?
                WHERE id=?
                """,
                (
                    rec.get("title"), rec.get("url"), rec.get("location"),
                    rec.get("employment_type"), rec.get("posted_at_iso"),
                    now, metadata_json, job_id,
                ),
            )
            self.conn.commit()
            return job_id, False
        # Insert new
        cur.execute(
            """
            INSERT INTO jobs (site, external_id, title, url, location, employment_type,
                              posted_at_iso, first_seen_at, last_seen_at, is_active, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
            """,
            (
                rec["site"], rec["external_id"], rec.get("title"), rec.get("url"),
                rec.get("location"), rec.get("employment_type"), rec.get("posted_at_iso"),
                now, now, metadata_json,
            ),
        )
        job_id = cur.lastrowid
        self.conn.commit()
        return job_id, True

    def mark_removed_missing(self, site: str, still_present_external_ids: Iterable[str]) -> List[int]:
        """Mark as removed all *active* jobs from a site not present in current scrape.
        Returns list of affected job ids.
        """
        cur = self.conn.cursor()
        ids_param = list(still_present_external_ids)
        if not ids_param:
            # If nothing present now, remove all active from this site
            cur.execute(
                "SELECT id FROM jobs WHERE site=? AND is_active=1",
                (site,),
            )
        else:
            placeholders = ",".join(["?"] * len(ids_param))
            cur.execute(
                f"SELECT id FROM jobs WHERE site=? AND is_active=1 AND external_id NOT IN ({placeholders})",
                (site, *ids_param),
            )
        rows = cur.fetchall()
        job_ids = [r["id"] for r in rows]
        if not job_ids:
            return []
        # now = now_iso()
        # cur.executemany(
        #     "UPDATE jobs SET is_active=0, last_seen_at=? WHERE id=?",
        #     [(now, jid) for jid in job_ids],
        # )
        cur.executemany(
            "DELETE FROM events WHERE job_id=?",
            [(jid,) for jid in job_ids],
        )
        self.conn.commit()
        cur.executemany(
            "DELETE FROM jobs WHERE id=?",
            [(jid,) for jid in job_ids],
        )
        self.conn.commit()
        return job_ids

    def add_event(self, job_id: int, event_type: str):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO events (job_id, event_type, created_at) VALUES (?, ?, ?)",
            (job_id, event_type, now_iso()),
        )
        self.conn.commit()

    # --- reads ---
    def get_job_by_id(self, job_id: int) -> Optional[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
        return cur.fetchone()
