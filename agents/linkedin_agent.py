# agents/linkedin_agent.py
import requests
from bs4 import BeautifulSoup
import time
import urllib.parse

def search_linkedin(role, location, show_browser=False):
    """
    Attempt to fetch LinkedIn guest job listings via the 'seeMoreJobPostings' endpoint.
    If blocked or any error occurs, returns a small sample dataset so UI works.
    """
    try:
        q_role = urllib.parse.quote(role or "")
        q_loc = urllib.parse.quote(location or "")
        url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={q_role}&location={q_loc}&start=0"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        html = r.text

        # The guest API returns an HTML fragment; parse job cards
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("li")  # guest API often returns list items

        results = []
        for li in cards[:40]:
            title_tag = li.find("h3") or li.find("h2") or li.find("h1")
            company_tag = li.find("h4") or li.find("a", {"data-tracking-control-name": "public_jobs_company_link"})
            link_tag = li.find("a", href=True)
            location_tag = li.find("span", class_="job-result-card__location") or li.find("span")

            title = title_tag.get_text(strip=True) if title_tag else None
            company = company_tag.get_text(strip=True) if company_tag else ""
            link = link_tag["href"] if link_tag and link_tag.get("href") else "#"
            location_text = location_tag.get_text(strip=True) if location_tag else ""

            if title:
                results.append({
                    "title": title,
                    "company": company,
                    "location": location_text,
                    "link": link,
                    "description": "",  # guest API lacks detailed desc
                    "source": "LinkedIn"
                })

        if not results:
            raise ValueError("No jobs parsed from LinkedIn guest response")

        return results

    except Exception as e:
        # fallback sample jobs so UI is usable
        # (these are realistic-looking placeholders)
        time.sleep(0.2)
        sample = [
            {
                "title": "Data Engineer (Remote)",
                "company": "Greenhouse Inc",
                "location": "Remote",
                "link": "https://greenhouse.io/example-job",
                "description": "Build data pipelines, ETL, Spark, Python.",
                "source": "Greenhouse"
            },
            {
                "title": "Software Engineer (Fullstack)",
                "company": "Notion",
                "location": "New York, NY",
                "link": "https://www.notion.so/jobs/example",
                "description": "React, Node, backend services.",
                "source": "Notion"
            },
            {
                "title": "Data Scientist",
                "company": "Capgemini Engineering",
                "location": "Coimbatore, India",
                "link": "https://in.linkedin.com/jobs/view/example",
                "description": "ML models, Python, SQL.",
                "source": "LinkedIn (sample)"
            }
        ]
        return sample
