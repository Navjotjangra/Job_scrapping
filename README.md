# 🌐 Automated Job Data Enrichment & Scraping Pipeline

A Python-based project that automates the process of enriching company data and scraping job listings.  
It collects company websites, LinkedIn pages, and careers/job URLs, then scrapes up to **200 verified job postings** and saves them into a structured Excel file.

---

## 🚀 Features
- Automatically enriches incomplete company data using **DuckDuckGo API**.
- Detects and extracts **career pages** and **job listing URLs**.
- Scrapes up to **3 recent job postings per company**.
- Falls back on **public job boards** if company data is missing.
- Validates and stores results in Excel with both `Data` and `Methodology` sheets.

---

## ⚙️ Tech Stack
- **Language:** Python  
- **Libraries:** `requests`, `BeautifulSoup`, `pandas`, `openpyxl`, `logging`, `concurrent.futures`
- **Data Sources:** Company websites, DuckDuckGo API, Climate job boards (e.g., Remotive, ClimatePeople)

---

## 📁 Project Structure
| File | Description |
|------|--------------|
| `main.py` | Orchestrates the entire enrichment and scraping pipeline. |
| `company_enricher.py` | Finds company website, LinkedIn, and career links. |
| `job_scraper.py` | Scrapes job data from company careers or ATS systems. |
| `board_scraper.py` | Collects fallback jobs from public climate-tech boards. |
| `extra_boards.py` | Adds extra jobs from APIs (Remotive, ClimatePeople). |
| `validate_urls.py` | Verifies URLs and data consistency. |
| `requirements.txt` | Project dependencies. |
| `companies_input.csv` | Input dataset of company names and partial details. |
| `climate_jobs_output.xlsx` | Final output file with `Data` and `Methodology` sheets. |

---

## 🧠 Key Learnings
- Implemented **data enrichment** and **API integration** in a real scenario.  
- Gained hands-on experience with **web scraping**, **HTML parsing**, and **data validation**.  
- Designed a reliable, multi-threaded pipeline that mimics a real-world ETL process.

---

## 💾 Output Example
**Excel File Includes:**
- **Data Sheet:** Contains company info, websites, LinkedIn pages, and up to 3 job listings per company.  
- **Methodology Sheet:** Describes each step, tools used, and validation checks.

---

## 🧩 How to Run
```bash
pip install -r requirements.txt
python main.py
