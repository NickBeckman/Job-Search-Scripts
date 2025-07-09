
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
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Look for job listings - try different selectors
    job_elements = soup.find_all("div", class_="job-listing") or \
                   soup.find_all("div", class_="job-card") or \
                   soup.find_all("div", class_="search-result") or \
                   soup.find_all("a", class_="jobTitle-link") or \
                   soup.find_all("div", class_="job-item")
    
    print(f"Found {len(job_elements)} job elements. Extracting job details...")
    
    job_listings = []
    
    for job in job_elements:
        # Try to extract job title and location
        title_elem = job.find("h3") or job.find("h2") or job.find("a") or job.find("span", class_="job-title")
        location_elem = job.find("span", class_="location") or job.find("div", class_="location") or job.find("span", class_="job-location")
        
        title = title_elem.text.strip() if title_elem else "Unknown Title"
        location = location_elem.text.strip() if location_elem else "Unknown Location"
        
        if title and title != "Unknown Title":
            job_info = f"{title}{location}"
            job_listings.append(job_info)
            print(job_info)
    
    return job_listings

if __name__ == "__main__":
    jobs = scrape_cdw_jobs()
    print("\n== All Job Listings ==")
    for job in jobs:
        print(job)