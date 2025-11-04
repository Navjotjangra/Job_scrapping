#job_scraper.py — Universal Job Listing Scraper
#Supports common ATS (Lever, Greenhouse, Workday) + generic parsing.
#Grabs up to 3 jobs per company, up to 200 total.

import requests
import time
import random
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("JobScraper")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


class JobBoardScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.total = 0
        self.max_total = 200

    def _get(self, url):
        """Safe GET with retries"""
        if self.total >= self.max_total:
            return None
        for _ in range(2):
            try:
                r = self.session.get(url, timeout=12)
                if r.status_code == 200:
                    return r.text
            except Exception:
                time.sleep(2)
        return None

    def detect_platform(self, url):
        u = url.lower()
        if "lever" in u: return "lever"
        if "greenhouse" in u: return "greenhouse"
        if "workday" in u: return "workday"
        return "generic"

    def scrape_lever(self, url):
        html = self._get(url)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        postings = soup.select("div.posting, a.posting")[:3]
        jobs = []
        for p in postings:
            a = p if p.name == "a" else p.find("a")
            if not a: continue
            title = a.get_text(strip=True)
            loc = (p.find(class_=re.compile("location")) or {}).get_text(strip=True) if hasattr(p.find(class_=re.compile("location")), "get_text") else "Remote"
            jobs.append({"title": title, "url": urljoin(url, a["href"]), "location": loc})
        return jobs

    def scrape_greenhouse(self, url):
        html = self._get(url)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select("div.opening, section.level-0 a")[:3]
        jobs = []
        for i in items:
            a = i if i.name == "a" else i.find("a")
            if not a: continue
            jobs.append({
                "title": a.get_text(strip=True),
                "url": urljoin(url, a["href"]),
                "location": "Remote"
            })
        return jobs

    def scrape_workday(self, url):
        html = self._get(url)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        for li in soup.find_all("li", {"data-automation-id": "listItem"})[:3]:
            a = li.find("a", href=True)
            if not a: continue
            jobs.append({"title": a.get_text(strip=True), "url": urljoin(url, a["href"]), "location": "Remote"})
        return jobs

    def scrape_generic(self, url):
        html = self._get(url)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        jobs = []
        for link in soup.find_all("a", href=True):
            text = link.get_text(strip=True)
            if len(text) < 5: continue
            if any(k in text.lower() for k in ["engineer", "manager", "developer", "analyst", "scientist"]):
                jobs.append({
                    "title": text[:120],
                    "url": urljoin(url, link["href"]),
                    "location": "Remote"
                })
            if len(jobs) >= 3:
                break
        return jobs

    def scrape_company_jobs(self, careers_url, company_name=""):
        """Main dispatcher"""
        if not careers_url or self.total >= self.max_total:
            return []
        platform = self.detect_platform(careers_url)
        logger.info(f" {company_name} | Platform detected: {platform}")
        func = {
            "lever": self.scrape_lever,
            "greenhouse": self.scrape_greenhouse,
            "workday": self.scrape_workday
        }.get(platform, self.scrape_generic)
        jobs = func(careers_url)
        self.total += len(jobs)
        logger.info(f" {company_name}: {len(jobs)} jobs found (total {self.total})")
        return jobs
