from typing import Iterable
from ..models import Job
import requests

SITE_KEY = "Lidl"

url = "https://jobs.lidl.ie/search_api/jobsearch"

params = {
    "page": "1",
    "midpoint_name": "Dublin, County Dublin",
    "midpoint_lat": "53.3641",
    "midpoint_lon": "-6.2931",
    "radius": "5",
    "sort_field": "location.distance",
    "sort_order": "asc",
    "filter": '{"contract_type":[],"employment_area":[],"entry_level":[]}',
    "with_event": "true",
    "hash": ""
}

headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,ta;q=0.8",
    "dnt": "1",
    "priority": "u=1, i",
    "referer": "https://jobs.lidl.ie/jobsearch?page=1&midpoint_name=Dublin,%20County%20Dublin&midpoint_lat=53.3641&midpoint_lon=-6.2931&radius=5&sort_field=location.distance&sort_order=asc&filter={%22contract_type%22:[],%22employment_area%22:[],%22entry_level%22:[]}&with_event=true&hash=",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}


def scrape() -> Iterable[Job]:
    response = requests.get(
        url, 
        headers=headers, 
        params=params
    )
    response.raise_for_status()
    resp = response.json()
    for job in resp["result"]["hits"]:
        yield Job(
            site=SITE_KEY,
            external_id=job["title"],
            title=job["title"],
            url=job["easyApply"]["easyApplyUrl"],
            location=f"{job['location']['title']} - {job['location']['postcode']}",
            employment_type=job["contractType"],
            posted_at_iso=job["onlineUntil"],
            metadata={
                "closing date": job["closingDate"],
                "online Until": job["onlineUntil"],
                "entry level": job["entryLevel"]
            },
        )