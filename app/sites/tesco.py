import requests
from urllib.parse import urljoin
from lxml import html
import json
from typing import Iterable
from ..models import Job

SITE_KEY = "Tesco"

BASE_URL = "https://careers.tesco.com/en_GB/careersmarketplace/SearchJobs/"

params = {
    "748_location_place": "D07, Dublin, Ireland",
    "748_location_radius": "5",
    "748_location_coordinates": "[53.36,-6.29]",
    "listFilterMode": "1",
    "jobRecordsPerPage": "10",
}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9,ta;q=0.8",
    "dnt": "1",
    "priority": "u=0, i",
    "referer": "https://careers.tesco.com/en_GB/careersmarketplace/SearchJobs?_gl=1*zyntfu*_up*MQ..*_ga*MTYyMjM3ODY2My4xNzU1MTc3MzMw*_ga_FCL0R2642N*czE3NTUxNzczMjkkbzEkZzAkdDE3NTUxNzczMjkkajYwJGwwJGgw",
    "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
}

def scrape() -> Iterable[Job]:
    resp = requests.get(BASE_URL, params=params, headers=headers, timeout=30)
    resp.raise_for_status()

    doc = html.fromstring(resp.text)

    container_xpath = "/html/body/div[1]/main/div/div/section/div[2]/div[2]/div/div"
    container = doc.xpath(container_xpath)
    if not container:
        raise RuntimeError("Container not found. The page layout or cookies may have changed.")

    articles = container[0].xpath("./article")

    for art in articles:
        title_a = art.xpath("./div[1]/div[1]/h3/a")
        title_text = title_a[0].text_content().strip() if title_a else None
        href = urljoin(resp.url, title_a[0].get("href")) if title_a and title_a[0].get("href") else None

        spans = art.xpath("./div[1]/div[1]/div//span")
        span_texts = [s.text_content().strip() for s in spans if s.text_content().strip()]

        yield Job(
            site=SITE_KEY,
            external_id=title_text,
            title=title_text,
            url=href,
            location=span_texts[2],
            employment_type=span_texts[0],
            posted_at_iso=None,
            metadata={},
        )