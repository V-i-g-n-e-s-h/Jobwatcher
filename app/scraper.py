import importlib
import os
from pathlib import Path
from typing import List, Set
from datetime import datetime

from .db import DB
from .models import Job
from .notify import notify, setup_logging
from .sites.registry import SITES

DB_PATH = Path(os.environ.get("DB_PATH", "/data/data/com.termux/files/home/jobwatcher/data/jobwatcher.db"))
LOG_PATH = Path(os.environ.get("LOG_PATH", "/data/data/com.termux/files/home/jobwatcher/logs/jobwatcher.log"))

def run_once():
    notify(title="Executing", content=f"Scrapper: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    setup_logging(LOG_PATH)
    db = DB(DB_PATH)
    for modname in SITES:
        mod = importlib.import_module(modname)
        site_key = getattr(mod, "SITE_KEY")
        print(f"Scraping {site_key}...")
        present: Set[str] = set()
        new_ids: List[int] = []
        removed_ids: List[int] = []

        for job in mod.scrape():
            assert isinstance(job, Job)
            rec = job.to_record()
            job_id, is_new = db.upsert_job(rec)
            present.add(job.external_id)
            if is_new:
                db.add_event(job_id, "new")
                new_ids.append(job_id)

        removed_job_ids = db.mark_removed_missing(site_key, present)
        for jid in removed_job_ids:
            db.add_event(jid, "removed")
            removed_ids.append(jid)

        for jid in new_ids:
            print(f"NEW:{site_key} :: {str(jid)}")
            notify(title=f"NEW:{site_key}", content=str(jid))
        for jid in removed_ids:
            print(f"REMOVED:{site_key} :: {jid}")
            notify(title=f"REMOVED:{site_key}", content=str(jid))

if __name__ == "__main__":
    run_once()
