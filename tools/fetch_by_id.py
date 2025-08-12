import os
import sys
from pathlib import Path
from textwrap import indent

sys.path.append(str(Path(__file__).resolve().parents[1]))
from app.db import DB

DB_PATH = Path(os.environ.get("DB_PATH", "/data/data/com.termux/files/home/jobwatcher/data/jobwatcher.db"))

def main():
    if len(sys.argv) != 2:
        print("Usage: python tools/fetch_by_id.py <JOB_ID>")
        sys.exit(1)
    job_id = int(sys.argv[1])
    db = DB(DB_PATH)
    row = db.get_job_by_id(job_id)
    if not row:
        print(f"No job found with id {job_id}")
        sys.exit(2)

    print(f"Job #{row['id']} — {row['title']}")
    print(f"Site: {row['site']} | External ID: {row['external_id']}")
    print(f"URL:  {row['url']}")
    if row['location']:
        print(f"Location: {row['location']}")
    if row['employment_type']:
        print(f"Type: {row['employment_type']}")
    if row['posted_at_iso']:
        print(f"Posted: {row['posted_at_iso']}")
    print(f"First Seen: {row['first_seen_at']} | Last Seen: {row['last_seen_at']} | Active: {bool(row['is_active'])}")

    import json
    try:
        meta = json.loads(row['metadata_json'] or "{}")
    except Exception:
        meta = {}
    if meta:
        print("\nMetadata:")
        for k, v in meta.items():
            print(f"  - {k}: {v}")

if __name__ == "__main__":
    main()
