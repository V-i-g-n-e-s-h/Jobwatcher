from typing import Iterable, Dict
from ..models import Job

# Every site module must expose: scrape() -> Iterable[Job]
# And a constant: SITE_KEY = "shortname"

SiteResult = Iterable[Job]

__all__ = ["SiteResult", "Job"]
