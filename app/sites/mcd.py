"""Offline demo source for smoke tests (no network)."""
from typing import Iterable
from ..models import Job
import requests

SITE_KEY = "McD"

url = "https://rvmob42dfh-dsn.algolia.net/1/indexes/*/queries"
params = {
    "x-algolia-agent": "Algolia for JavaScript (4.13.0); Browser (lite); instantsearch.js (4.40.5); JS Helper (3.10.0)",
    "x-algolia-api-key": "0a69e536b78a0eb7abf95cf3331caf64",
    "x-algolia-application-id": "RVMOB42DFH"
}

headers = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9,ta;q=0.8",
    "Connection": "keep-alive",
    "DNT": "1",
    "Origin": "https://people.mcdonalds.ie",
    "Referer": "https://people.mcdonalds.ie/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

data = r'''
{
    "requests":[
        {
            "indexName":"production__mcdscare2501__sort-rank",
            "params":"aroundLatLng=53.3641815,-6.2926623&aroundRadius=16093&facetFilters=%5B%5B%22country%3AUnited%20Kingdom%22%2C%22country%3ARepublic%20of%20Ireland%22%5D%5D&facets=%5B%22business_area%22%2C%22contract_type%22%2C%22country%22%5D&getRankingInfo=true&highlightPostTag=__/ais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=100&maxValuesPerFacet=100&page=0&query=&tagFilters="
        },
        {
            "indexName":"production__mcdscare2501__sort-rank",
            "params":"analytics=false&aroundLatLng=53.3641815,-6.2926623&aroundRadius=16093&clickAnalytics=false&facets=country&getRankingInfo=true&highlightPostTag=__/ais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=100&maxValuesPerFacet=100&page=0&query="
        }
    ]
}
'''

def scrape() -> Iterable[Job]:
    # Pretend two jobs exist right now
    response = requests.post(url, headers=headers, params=params, data=data)
    response.raise_for_status()
    result = response.json()
    for job in result["results"][0]["hits"]:
        yield Job(
            site=SITE_KEY,
            external_id=f"{job['department']} - {job['display_address']}",
            title=job["department"],
            url=job["apply_url"],
            location=job["display_address"],
            employment_type=job["contract_type"],
            posted_at_iso=None,
            metadata={},
        )

