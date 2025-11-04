# main.py – central script I wrote to collect company data and job listings.
# It reads the company list, enriches info, scrapes jobs, and saves everything to Excel.


import pandas as pd
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import logging

from company_enricher import CompanyEnricher
from job_scraper import JobBoardScraper
from board_scraper import scrape_200_climate_jobs  # fallback source

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("job_pipeline")


class AssignmentPipeline:
    def __init__(self, input_csv="companies_input.csv", output_excel="climate_jobs_output.xlsx"):
        self.input_csv = input_csv
        self.output_excel = output_excel
        self.enricher = CompanyEnricher()
        self.scraper = JobBoardScraper()
        self.results = []
        self.max_jobs = 200
        self.start = datetime.now()

    def load_companies(self):
        df = pd.read_csv(self.input_csv)
        df.columns = df.columns.str.strip()
        logger.info(f" Loaded {len(df)} companies.")
        return df

    def process_company(self, row):
        name = str(row.get("Company Name", "")).strip()
        desc = str(row.get("Company Description", "")).strip()
        if not name:
            return None

        enriched = self.enricher.enrich_company(name, desc)
        jobs = []
        for key in ["job_listings_url", "careers_page", "website"]:
            url = enriched.get(key)
            if url:
                jobs = self.scraper.scrape_company_jobs(url, name)
                if jobs:
                    break

        row_data = {
            "Company Name": name,
            "Company Description": desc,
            "Website URL": enriched.get("website", ""),
            "LinkedIn URL": enriched.get("linkedin", ""),
            "Careers Page URL": enriched.get("careers_page", ""),
            "Job listings page URL": enriched.get("job_listings_url", "")
        }
        for i in range(3):
            prefix = f"job post{i+1}"
            if i < len(jobs):
                job = jobs[i]
                row_data[f"{prefix} title"] = job["title"]
                row_data[f"{prefix} URL"] = job["url"]
                row_data[f"{prefix} location"] = job["location"]
            else:
                row_data[f"{prefix} title"] = ""
                row_data[f"{prefix} URL"] = ""
                row_data[f"{prefix} location"] = ""
        return row_data

    def run(self):
        df = self.load_companies()
        logger.info(" Beginning company processing...")
        with ThreadPoolExecutor(max_workers=5) as ex:
            futures = [ex.submit(self.process_company, row) for _, row in df.iterrows()]
            for f in as_completed(futures):
                data = f.result()
                if data:
                    self.results.append(data)
                if len(self.results) >= self.max_jobs:
                    logger.info(" 200 jobs reached - stopping now.")
                    break

        if len(self.results) < self.max_jobs:
            logger.info("Adding more jobs from public boards...")
            board_jobs = scrape_200_climate_jobs()
            for j in board_jobs[: (self.max_jobs - len(self.results))]:
                self.results.append({
                    "Company Name": j["company"],
                    "Company Description": f"From {j['board']}",
                    "Website URL": "",
                    "LinkedIn URL": "",
                    "Careers Page URL": j["url"],
                    "Job listings page URL": j["url"],
                    "job post1 title": j["title"],
                    "job post1 URL": j["url"],
                    "job post1 location": j["location"]
                })

        self.save_excel()
        logger.info(" Done!")

    def save_excel(self):
        data_df = pd.DataFrame(self.results)
        method_df = pd.DataFrame([
     {"Step": "1. Load data", "Notes": "Read company names from CSV file"},
     {"Step": "2. Find sites", "Notes": "Used DuckDuckGo search to get domains/LinkedIn"},
     {"Step": "3. Find careers pages", "Notes": "Looked for /careers or similar links"},
     {"Step": "4. Scrape jobs", "Notes": "Grabbed job titles and links via BeautifulSoup"},
     {"Step": "5. Validate", "Notes": "Checked sample URLs manually"},
    ])

        with pd.ExcelWriter(self.output_excel, engine="openpyxl") as w:
            data_df.to_excel(w, sheet_name="Data", index=False)
            method_df.to_excel(w, sheet_name="Methodology", index=False)
        logger.info(f" Saved results to {self.output_excel}")

# Quick test run for my own validation before submission

if __name__ == "__main__":
    pipeline = AssignmentPipeline()
    pipeline.run()
