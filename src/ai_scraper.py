#!/usr/bin/env python3
"""AI-Powered Job Scraper using OpenAI."""

import os
import json
from typing import Optional, Dict
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from config import OPENAI_API_KEY


class AIJobScraper:
    """AI-powered job scraper using OpenAI to extract job details from any URL."""

    def __init__(self):
        """Initialize the AI scraper."""
        self.has_api_key = bool(OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key_here')
        if self.has_api_key:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.client = None
            print("Warning: OpenAI API key not configured. AI scraping disabled.")

    def fetch_job_from_url(self, url: str) -> Optional[Dict]:
        """
        Fetch and parse job details from a URL using AI.

        Args:
            url: Job posting URL

        Returns:
            Dictionary with job details or None if failed
        """
        if not self.has_api_key:
            print("OpenAI API key not configured. Cannot use AI scraping.")
            return None

        try:
            # Fetch the page content
            print(f"Fetching URL: {url}")
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            response.raise_for_status()

            # Parse HTML and extract text
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text content
            text = soup.get_text(separator='\n', strip=True)

            # Limit to first 8000 characters to avoid token limits
            text = text[:8000]

            print("Sending to OpenAI for extraction...")

            # Use OpenAI to extract structured data
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a job posting parser. Extract structured information from job postings.
Return ONLY valid JSON with these exact fields:
{
    "title": "job title",
    "company": "company name",
    "location": "city, state/country",
    "remote": true/false,
    "salary_min": 70000 or null,
    "salary_max": 90000 or null,
    "description": "full job description including responsibilities, requirements, and benefits"
}

Important:
- remote should be true if the job mentions "remote", "work from home", or "distributed"
- Extract salary numbers even if written as "$70k-$90k" or "70-90K"
- If salary not mentioned, use null
- Include ALL relevant details in description (responsibilities, requirements, qualifications, benefits)
- If location says "Remote" or "Anywhere", set location to "Remote"
"""
                    },
                    {
                        "role": "user",
                        "content": f"Extract job details from this page:\n\n{text}"
                    }
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            # Parse the response
            result = json.loads(completion.choices[0].message.content)

            # Add the URL to the result
            result['url'] = url

            print(f"✓ Successfully extracted: {result.get('title')} at {result.get('company')}")

            return result

        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def analyze_job_fit(self, job_description: str, profile_summary: str) -> Optional[Dict]:
        """
        Use AI to analyze how well a job fits the candidate profile.

        Args:
            job_description: The job posting description
            profile_summary: Summary of candidate's profile

        Returns:
            Dictionary with insights or None if failed
        """
        if not self.has_api_key:
            return None

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a career advisor analyzing job fit. Provide honest, helpful analysis.
Return ONLY valid JSON with these fields:
{
    "skill_gaps": ["skill1", "skill2"],
    "transferable_skills": ["skill1", "skill2"],
    "recommendations": ["recommendation1", "recommendation2"],
    "key_requirements": ["requirement1", "requirement2"],
    "why_good_fit": "brief explanation of why this is a good fit",
    "concerns": "any concerns or red flags"
}"""
                    },
                    {
                        "role": "user",
                        "content": f"""Analyze this job for the candidate:

CANDIDATE PROFILE:
{profile_summary}

JOB DESCRIPTION:
{job_description}

Provide insights on fit, skill gaps, and recommendations."""
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            result = json.loads(completion.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Error analyzing job fit: {e}")
            return None

    def generate_cover_letter(self, job_description: str, profile_summary: str, company: str, position: str) -> Optional[str]:
        """
        Generate a personalized cover letter using AI.

        Args:
            job_description: The job posting description
            profile_summary: Summary of candidate's profile
            company: Company name
            position: Job title

        Returns:
            Cover letter text or None if failed
        """
        if not self.has_api_key:
            return None

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a professional cover letter writer. Write compelling, personalized cover letters that:
- Are concise (250-300 words)
- Reference specific job requirements
- Highlight relevant accomplishments
- Show genuine interest in the company
- Are professional but personable
- Avoid clichés and generic statements"""
                    },
                    {
                        "role": "user",
                        "content": f"""Write a cover letter for this position:

COMPANY: {company}
POSITION: {position}

CANDIDATE PROFILE:
{profile_summary}

JOB DESCRIPTION:
{job_description}

Write a compelling cover letter that matches the candidate's experience to the job requirements."""
                    }
                ],
                temperature=0.7
            )

            return completion.choices[0].message.content

        except Exception as e:
            print(f"Error generating cover letter: {e}")
            return None


# Test functionality
if __name__ == "__main__":
    scraper = AIJobScraper()

    # Test URL
    test_url = "https://job-boards.greenhouse.io/vultr/jobs/4602862006"

    print("\n" + "="*60)
    print("Testing AI Job Scraper")
    print("="*60 + "\n")

    result = scraper.fetch_job_from_url(test_url)

    if result:
        print("\n✓ Extraction successful!\n")
        print(json.dumps(result, indent=2))
    else:
        print("\n✗ Extraction failed.")
