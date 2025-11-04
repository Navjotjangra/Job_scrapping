# company_enricher.py – helper I wrote to pull company info.
# It looks up sites and LinkedIn pages using DuckDuckGo, then guesses careers URLs.


import requests
import re
import time
import random
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("enricher")

DUCK_API = "https://api.duckduckgo.com/?q={query}&format=json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


class CompanyEnricher:
    #Finds website, LinkedIn, careers, and job listings URLs for a company

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _get(self, url, timeout=12):
        # basic GET call with retry; short delay to be polite
        for _ in range(2):
            try:
                r = self.session.get(url, timeout=timeout)
                if r.status_code == 200:
                    return r.text
            except Exception:
                time.sleep(2)
        return None

    def _search_api(self, query):
        #Use DuckDuckGo Instant Answer API
        try:
            url = DUCK_API.format(query=quote_plus(query))
            r = self.session.get(url, timeout=10)
            data = r.json()
            if data.get("AbstractURL"):
                return [data["AbstractURL"]]
            related = [topic["FirstURL"] for topic in data.get("RelatedTopics", []) if "FirstURL" in topic]
            return related[:5]
        except Exception:
            return []

    def find_website(self, company):
        #Try to find official website
        logger.info(f" Searching website for {company}")
        results = self._search_api(f"{company} official website")
        for link in results:
            if not any(x in link for x in ["linkedin", "facebook", "glassdoor", "indeed"]):
                logger.info(f"Found website: {link}")
                return link
        # fallback guess
        slug = re.sub(r"[^a-z0-9]", "", company.lower())
        for tld in ["com", "io", "org", "co", "ai"]:
            guess = f"https://{slug}.{tld}"
            html = self._get(guess)
            if html:
                logger.info(f"Guessed website: {guess}")
                return guess
        return None

    def find_linkedin(self, company):
        #Find LinkedIn company page
        results = self._search_api(f"{company} site:linkedin.com/company")
        for link in results:
            if "linkedin.com/company" in link:
                return link.split("?")[0]
        return None

    def find_careers_page(self, website):
        #Find /careers or /jobs link on site
        if not website:
            return None
        html = self._get(website)
        if not html:
            return None

        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True).lower()
            if any(kw in text for kw in ["career", "job", "join", "work with"]):
                return urljoin(website, a["href"])
        for suffix in ["/careers", "/jobs", "/join-us"]:
            test_url = website.rstrip("/") + suffix
            if self._get(test_url):
                return test_url
        return None

    def detect_job_board(self, url):
        #Detect if site uses known ATS (Lever, Greenhouse, etc.)
        if not url:
            return None
        patterns = ["lever.co", "greenhouse.io", "workday", "ashbyhq", "smartrecruiters",
                    "bamboohr", "recruitee", "workable", "jobvite"]
        if any(p in url for p in patterns):
            return url
        html = self._get(url)
        if html:
            for p in patterns:
                if p in html:
                    return url
        return None

    def enrich_company(self, name, desc=""):
        #Main entry
        data = {
            "company_name": name,
            "company_description": desc,
            "website": None,
            "linkedin": None,
            "careers_page": None,
            "job_listings_url": None,
        }

        website = self.find_website(name)
        data["website"] = website or ""
        data["linkedin"] = self.find_linkedin(name)
        data["careers_page"] = self.find_careers_page(website)
        data["job_listings_url"] = self.detect_job_board(data["careers_page"])
        return data
