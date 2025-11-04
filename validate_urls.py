#URL Validator - Quick check before submission
#Randomly samples URLs from your output file and verifies they work
#Run this BEFORE submitting to catch any broken links


import pandas as pd
import requests
import random
from urllib.parse import urlparse


def validate_url(url, timeout=10):
    #Check if URL is valid and accessible
    if not url or url == '' or pd.isna(url):
        return False, "Empty URL"
    
    try:
        # basic URL format check
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format"
        
        # try to fetch
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        if response.status_code < 400:
            return True, f"OK ({response.status_code})"
        else:
            return False, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except Exception as e:
        return False, f"Error: {str(e)[:50]}"


def validate_output_file(excel_file='climate_jobs_assignment.xlsx', sample_size=20):
    
    #Validate random sample of URLs from output file
    #Checks: website URLs, LinkedIn URLs, careers pages, job URLs
    
    print(f"\n Validating URLs from {excel_file}")
    print(f"Checking random sample of {sample_size} URLs...\n")
    
    try:
        # load the data sheet
        df = pd.read_excel(excel_file, sheet_name='Data')
        print(f"✓ Loaded {len(df)} rows\n")
        
        # collect all URLs to check
        url_columns = [
            'Website URL',
            'LinkedIn URL', 
            'Careers Page URL',
            'Job listings page URL',
            'job post1 URL',
            'job post2 URL',
            'job post3 URL'
        ]
        
        all_urls = []
        for col in url_columns:
            if col in df.columns:
                for idx, url in enumerate(df[col]):
                    if url and url != '' and not pd.isna(url):
                        all_urls.append({
                            'type': col,
                            'url': url,
                            'company': df.loc[idx, 'Company Name'] if 'Company Name' in df.columns else 'Unknown'
                        })
        
        print(f"Found {len(all_urls)} total URLs to check")
        
        # randomly sample
        sample = random.sample(all_urls, min(sample_size, len(all_urls)))
        
        # validate each URL
        results = {'valid': 0, 'invalid': 0, 'issues': []}
        
        for i, item in enumerate(sample, 1):
            url_type = item['type']
            url = item['url']
            company = item['company']
            
            print(f"[{i}/{len(sample)}] Checking {url_type} for {company[:30]}...")
            
            is_valid, message = validate_url(url)
            
            if is_valid:
                results['valid'] += 1
                print(f"  ✓ {message}")
            else:
                results['invalid'] += 1
                print(f"  ✗ {message}")
                results['issues'].append({
                    'company': company,
                    'type': url_type,
                    'url': url,
                    'issue': message
                })
        
        # print summary
        print("\n" + "="*60)
        print(" VALIDATION SUMMARY")
        print("="*60)
        print(f"✓ Valid URLs: {results['valid']}/{len(sample)}")
        print(f"✗ Invalid URLs: {results['invalid']}/{len(sample)}")
        print(f"Success rate: {(results['valid']/len(sample)*100):.1f}%")
        
        if results['issues']:
            print(f"\n  Found {len(results['issues'])} issues:")
            for issue in results['issues'][:10]:  # show first 10
                print(f"\n  Company: {issue['company']}")
                print(f"  Type: {issue['type']}")
                print(f"  URL: {issue['url']}")
                print(f"  Issue: {issue['issue']}")
        
        print("\n" + "="*60)
        
        if results['invalid'] / len(sample) > 0.2:  # more than 20% invalid
            print("  WARNING: More than 20% of sampled URLs are invalid!")
            print("Consider reviewing your data before submission.")
        else:
            print(" Validation looks good! Ready to submit.")
        
        print("="*60 + "\n")
        
    except FileNotFoundError:
        print(f" File not found: {excel_file}")
        print("Make sure you've run main.py first to generate the output file.")
    except Exception as e:
        print(f" Error during validation: {e}")


def quick_check_data_sheet(excel_file='climate_jobs_assignment.xlsx'):
    #Quick check of data completeness
    print(f"\n Quick Data Check: {excel_file}\n")
    
    try:
        df = pd.read_excel(excel_file, sheet_name='Data')
        
        print(f"Total companies: {len(df)}")
        print(f"Companies with websites: {df['Website URL'].notna().sum()}")
        print(f"Companies with LinkedIn: {df['LinkedIn URL'].notna().sum()}")
        print(f"Companies with careers pages: {df['Careers Page URL'].notna().sum()}")
        
        # count total jobs
        total_jobs = 0
        for i in range(1, 4):
            col = f'job post{i} URL'
            if col in df.columns:
                total_jobs += df[col].notna().sum()
        
        print(f"Total jobs scraped: {total_jobs}")
        
        if total_jobs >= 200:
            print("\n Hit the 200 jobs target!")
        else:
            print(f"\n  Only {total_jobs} jobs - may need to scrape more companies")
        
    except Exception as e:
        print(f" Error: {e}")


if __name__ == "__main__":
    import sys
    
    print("""
    
       URL Validator - Pre-Submission Check      
    
    """)
    
    excel_file = sys.argv[1] if len(sys.argv) > 1 else 'climate_jobs_assignment.xlsx'
    
    # quick data check first
    quick_check_data_sheet(excel_file)
    
    print("\n" + "-"*60 + "\n")
    
    # then validate URLs
    validate_output_file(excel_file, sample_size=20)
    
    print("\n Tip: Manually verify 2-3 random entries in Excel before submitting!")