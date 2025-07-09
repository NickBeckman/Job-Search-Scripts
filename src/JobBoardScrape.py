
import os
import requests
from bs4 import BeautifulSoup
import openai
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

def classify_job_title(title):
    """Use GPT to check if a job title is early career (<3 years exp, non-senior/manager)"""
    prompt = f"Is the job title '{title}' an early-career role that requires less than 3 years of experience and is not a senior or manager-level role? Answer only 'Yes' or 'No'."

    response = openai.ChatCompletion.create(  # type: ignore
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return "Yes" in response['choices'][0]['message']['content']

def scrape_cdw_jobs():
    url = "https://www.cdwjobs.com/search/jobs"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.cdwjobs.com/",
        "Connection": "keep-alive",
    }
    response = requests.get(url, headers=headers)
    
    print(f"Response status: {response.status_code}")
    print(f"Response URL: {response.url}")
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Debug: Print some of the HTML to see the structure
    print("First 1000 characters of HTML:")
    print(response.text[:1000])
    
    # Try multiple approaches to find job listings
    job_elements = []
    
    # Method 1: Look for common job listing selectors
    selectors = [
        "div[class*='job']",
        "div[class*='listing']", 
        "div[class*='card']",
        "div[class*='result']",
        "a[class*='job']",
        "li[class*='job']",
        "article[class*='job']"
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        if elements:
            print(f"Found {len(elements)} elements with selector: {selector}")
            job_elements.extend(elements)
            break
    
    # Method 2: Look for any elements containing job-related text
    if not job_elements:
        all_divs = soup.find_all("div")
        for div in all_divs:
            text = div.get_text().lower()
            if any(keyword in text for keyword in ["engineer", "manager", "specialist", "analyst", "developer", "coordinator"]):
                job_elements.append(div)
                print(f"Found potential job div: {div.get_text()[:100]}")
    
    print(f"Total found: {len(job_elements)} job elements")
    
    job_listings = []
    
    for i, job in enumerate(job_elements[:10]):  # Limit to first 10 for debugging
        print(f"\n--- Job Element {i+1} ---")
        print(f"Tag: {job.name}")
        print(f"Classes: {job.get('class', [])}")
        print(f"Text preview: {job.get_text()[:200]}")
        
        # Try to extract job title and location
        title = "Unknown Title"
        location = "Unknown Location"
        
        # Look for title in various elements
        title_candidates = job.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "a", "span", "div"])
        for candidate in title_candidates:
            text = candidate.get_text().strip()
            if len(text) > 5 and len(text) < 100:  # Reasonable title length
                if any(keyword in text.lower() for keyword in ["engineer", "manager", "specialist", "analyst", "developer", "coordinator", "administrator"]):
                    title = text
                    break
        
        # Look for location
        location_candidates = job.find_all(["span", "div", "p"])
        for candidate in location_candidates:
            text = candidate.get_text().strip()
            if "," in text and any(keyword in text.lower() for keyword in ["united states", "canada", "uk", "london", "chicago", "montreal"]):
                location = text
                break
        
        if title != "Unknown Title":
            job_info = f"{title}{location}"
            job_listings.append(job_info)
            print(f"Extracted: {job_info}")
    
    return job_listings

if __name__ == "__main__":
    jobs = scrape_cdw_jobs()
    print("\n== All Job Listings ==")
    for job in jobs:
        print(job)