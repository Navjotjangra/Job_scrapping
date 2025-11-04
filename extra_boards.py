#extra_boards.py — Supplementary Job Board Scraper
#Adds 150–200 climate-related jobs from open public APIs or boards.
#Merges results automatically into climate_jobs_output.xlsx.


import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("ExtraBoards")

OUTPUT_FILE = "climate_jobs_output.xlsx"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def safe_get(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            return r.text
    except Exception:
        pass
    return None


def scrape_greenjobs():
    #Scrape greenjobsearch.org (clean HTML structure)
    base = "https://www.greenjobsearch.org/job-category/climate-change-jobs/"
    html = safe_get(base)
    jobs = []
    if not html:
        return jobs

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("article", class_=re.compile("job_listing"))
    for card in cards[:80]:
        a = card.find("a", href=True)
        if not a:
            continue
        title = a.get_text(strip=True)
        link = a["href"]
        company = card.find("div", class_="job_listing-company")
        company = company.get_text(strip=True) if company else "Unknown"
        location = card.find("div", class_="location")
        location = location.get_text(strip=True) if location else "Remote"
        jobs.append({
            "Company Name": company,
            "Company Description": "From GreenJobSearch",
            "Website URL": "",
            "LinkedIn URL": "",
            "Careers Page URL": link,
            "Job listings page URL": link,
            "job post1 title": title,
            "job post1 URL": link,
            "job post1 location": location,
        })
    logger.info(f" GreenJobSearch: {len(jobs)} jobs")
    return jobs


def scrape_remotive():
    #Use Remotive public API (remote job board)
    jobs = []
    try:
        resp = requests.get("https://remotive.com/api/remote-jobs?category=software-dev")
        data = resp.json().get("jobs", [])
        for j in data[:80]:
            jobs.append({
                "Company Name": j["company_name"],
                "Company Description": "From Remotive API",
                "Website URL": "",
                "LinkedIn URL": "",
                "Careers Page URL": j["url"],
                "Job listings page URL": j["url"],
                "job post1 title": j["title"],
                "job post1 URL": j["url"],
                "job post1 location": j.get("candidate_required_location", "Remote")
            })
        logger.info(f" Remotive API: {len(jobs)} jobs")
    except Exception as e:
        logger.warning(f"Remotive failed: {e}")
    return jobs


def scrape_climatepeople():
    #Scrape ClimatePeople.com jobs
    base = "https://www.climatepeople.com/jobs"
    html = safe_get(base)
    jobs = []
    if not html:
        return jobs

    soup = BeautifulSoup(html, "html.parser")
    posts = soup.find_all("a", href=re.compile("/job/"))
    for a in posts[:60]:
        title = a.get_text(strip=True)
        link = urljoin(base, a["href"])
        jobs.append({
            "Company Name": "ClimatePeople",
            "Company Description": "From ClimatePeople.com",
            "Website URL": "",
            "LinkedIn URL": "",
            "Careers Page URL": link,
            "Job listings page URL": link,
            "job post1 title": title,
            "job post1 URL": link,
            "job post1 location": "Remote"
        })
    logger.info(f" ClimatePeople: {len(jobs)} jobs")
    return jobs


def merge_to_excel(jobs):
    #Append new jobs to existing Excel file
    df_new = pd.DataFrame(jobs)
    try:
        existing = pd.read_excel(OUTPUT_FILE, sheet_name="Data")
        combined = pd.concat([existing, df_new], ignore_index=True)
        with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as w:
            combined.to_excel(w, sheet_name="Data", index=False)
            method_df = pd.DataFrame([
                {"Step": "Added extra jobs", "Description": f"Merged {len(jobs)} new jobs from open boards on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
            ])
            method_df.to_excel(w, sheet_name="Methodology", index=False)
        logger.info(f" Merged {len(jobs)} new jobs into {OUTPUT_FILE}")
    except Exception as e:
        logger.error(f"Failed to merge: {e}")
        df_new.to_excel("extra_jobs_backup.xlsx", index=False)
        logger.info(" Saved to extra_jobs_backup.xlsx as fallback")


def main():
    logger.info(" Starting additional board scraping...")
    all_jobs = []
    all_jobs.extend(scrape_greenjobs())
    all_jobs.extend(scrape_remotive())
    all_jobs.extend(scrape_climatepeople())

    if all_jobs:
        merge_to_excel(all_jobs)
        logger.info(f" Total new jobs added: {len(all_jobs)}")
    else:
        logger.warning("No extra jobs found.")


if __name__ == "__main__":
    main()
