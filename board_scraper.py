"""
board_scraper.py - Enhanced with more climate job boards
"""

import requests
import time
import random
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def safe_get(url, timeout=15):
    """Safe GET request with retry"""
    time.sleep(random.uniform(1.0, 2.5))
    for attempt in range(2):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200:
                return r.text
            time.sleep(2)
        except Exception as e:
            logger.debug(f"Request failed: {e}")
            time.sleep(2)
    return None


def climatetechlist_jobs():
    """Scrape ClimateTechList.com"""
    jobs = []
    logger.info("Scraping ClimateTechList...")
    
    for page in range(1, 6):  # 5 pages
        if len(jobs) >= 80:
            break
        
        html = safe_get(f"https://climatetechlist.com/jobs?page={page}")
        if not html:
            break
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Try multiple selectors
        cards = soup.find_all("div", class_=re.compile("job|posting"))
        if not cards:
            cards = soup.find_all("a", href=re.compile("/jobs/"))
        
        for card in cards:
            if len(jobs) >= 80:
                break
            
            link = card if card.name == "a" else card.find("a")
            if not link or not link.get("href"):
                continue
            
            title_elem = card.find(class_=re.compile("title|name|heading"))
            title = title_elem.get_text(strip=True) if title_elem else link.get_text(strip=True)
            
            company_elem = card.find(class_=re.compile("company"))
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            
            location_elem = card.find(class_=re.compile("location"))
            location = location_elem.get_text(strip=True) if location_elem else "Remote"
            
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "url": urljoin("https://climatetechlist.com", link["href"]),
                "board": "ClimateTechList",
            })
        
        logger.info(f"  ClimateTechList page {page}: {len(jobs)} jobs so far")
    
    return jobs


def climatebase_jobs():
    """Scrape Climatebase.org"""
    jobs = []
    logger.info("Scraping Climatebase...")
    
    for page in range(1, 6):
        if len(jobs) >= 80:
            break
        
        html = safe_get(f"https://climatebase.org/jobs?page={page}")
        if not html:
            break
        
        soup = BeautifulSoup(html, "html.parser")
        
        cards = soup.find_all(["div", "article"], class_=re.compile("job|position"))
        
        for card in cards:
            if len(jobs) >= 80:
                break
            
            link = card.find("a", href=True)
            if not link:
                continue
            
            title = link.get_text(strip=True)
            
            company_elem = card.find(class_=re.compile("company|organization"))
            company = company_elem.get_text(strip=True) if company_elem else "Unknown"
            
            location_elem = card.find(class_=re.compile("location"))
            location = location_elem.get_text(strip=True) if location_elem else "Remote"
            
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "url": urljoin("https://climatebase.org", link["href"]),
                "board": "Climatebase",
            })
        
        logger.info(f"  Climatebase page {page}: {len(jobs)} jobs so far")
    
    return jobs


def terra_do_jobs():
    """Scrape Terra.do job board"""
    jobs = []
    logger.info("Scraping Terra.do...")
    
    html = safe_get("https://www.terra.do/climate-jobs/job-board/")
    if not html:
        return jobs
    
    soup = BeautifulSoup(html, "html.parser")
    
    cards = soup.find_all("div", class_=re.compile("job|card"))[:40]
    
    for card in cards:
        link = card.find("a", href=True)
        if not link:
            continue
        
        title = link.get_text(strip=True)
        
        company_elem = card.find(class_=re.compile("company"))
        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
        
        location_elem = card.find(class_=re.compile("location"))
        location = location_elem.get_text(strip=True) if location_elem else "Remote"
        
        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "url": urljoin("https://www.terra.do", link["href"]),
            "board": "Terra.do",
        })
    
    logger.info(f"  Terra.do: {len(jobs)} jobs")
    return jobs


def work_on_climate_jobs():
    """Scrape WorkOnClimate.org"""
    jobs = []
    logger.info("Scraping WorkOnClimate...")
    
    html = safe_get("https://workonclimate.org/job-board")
    if not html:
        return jobs
    
    soup = BeautifulSoup(html, "html.parser")
    
    # WorkOnClimate may have different structure
    cards = soup.find_all(["div", "li"], class_=re.compile("job|listing"))[:40]
    
    for card in cards:
        link = card.find("a", href=True)
        if not link:
            continue
        
        title = link.get_text(strip=True)
        if len(title) < 5:
            continue
        
        company_elem = card.find(class_=re.compile("company|employer"))
        company = company_elem.get_text(strip=True) if company_elem else "Unknown"
        
        location = "Remote"
        
        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "url": urljoin("https://workonclimate.org", link["href"]),
            "board": "WorkOnClimate",
        })
    
    logger.info(f"  WorkOnClimate: {len(jobs)} jobs")
    return jobs


def scrape_200_climate_jobs():
    """
    Main function to scrape 200 jobs from public boards
    Tries multiple sources to ensure we get enough jobs
    """
    logger.info("\n" + "="*80)
    logger.info("SCRAPING PUBLIC CLIMATE JOB BOARDS")
    logger.info("="*80 + "\n")
    
    all_jobs = []
    
    # Scrape from all sources
    sources = [
        climatetechlist_jobs,
        climatebase_jobs,
        terra_do_jobs,
        work_on_climate_jobs,
    ]
    
    for source_func in sources:
        if len(all_jobs) >= 200:
            break
        
        try:
            jobs = source_func()
            all_jobs.extend(jobs)
            logger.info(f"Running total: {len(all_jobs)} jobs\n")
        except Exception as e:
            logger.error(f"Failed to scrape {source_func.__name__}: {e}")
            continue
    
    logger.info(f" Finished scraping {len(all_jobs)} jobs from public boards")
    
    return all_jobs[:200]


if __name__ == "__main__":
    # Test the scraper
    jobs = scrape_200_climate_jobs()
    print(f"\nSuccessfully scraped {len(jobs)} jobs")
    print("\nSample jobs:")
    for job in jobs[:5]:
        print(f"  - {job['title']} at {job['company']} ({job['board']})")