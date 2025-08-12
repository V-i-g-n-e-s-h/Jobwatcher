from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional

@dataclass
class Job:
    site: str                     # short key for the company/site (e.g., "kfc", "aldi")
    external_id: str              # stable id from the site (or the job URL)
    title: str
    url: str
    location: Optional[str] = None
    employment_type: Optional[str] = None
    posted_at_iso: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_record(self) -> Dict[str, Any]:
        d = asdict(self)
        return d
