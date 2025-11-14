"""Job posting management and storage."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

from config import JOBS_DIR


class Job:
    """Represents a job posting."""

    def __init__(
        self,
        title: str,
        company: str,
        description: str,
        url: Optional[str] = None,
        location: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        remote: bool = False,
        job_id: Optional[str] = None,
        added_date: Optional[str] = None,
    ):
        self.job_id = job_id or str(uuid.uuid4())
        self.title = title
        self.company = company
        self.description = description
        self.url = url
        self.location = location
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.remote = remote
        self.added_date = added_date or datetime.now().isoformat()
        self.scores = {}  # Will be populated by matcher

    def to_dict(self) -> Dict:
        """Convert job to dictionary."""
        return {
            'job_id': self.job_id,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'url': self.url,
            'location': self.location,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'remote': self.remote,
            'added_date': self.added_date,
            'scores': self.scores,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Job':
        """Create job from dictionary."""
        job = cls(
            job_id=data['job_id'],
            title=data['title'],
            company=data['company'],
            description=data['description'],
            url=data.get('url'),
            location=data.get('location'),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max'),
            remote=data.get('remote', False),
            added_date=data.get('added_date'),
        )
        job.scores = data.get('scores', {})
        return job

    def get_embedding_text(self) -> str:
        """Get text representation for embedding."""
        parts = []

        parts.append(f"Job Title: {self.title}")
        parts.append(f"Company: {self.company}")

        if self.location:
            parts.append(f"Location: {self.location}")

        if self.remote:
            parts.append("Remote: Yes")

        if self.salary_min and self.salary_max:
            parts.append(f"Salary: ${self.salary_min:,} - ${self.salary_max:,}")
        elif self.salary_min:
            parts.append(f"Salary: ${self.salary_min:,}+")

        parts.append(f"\nJob Description:\n{self.description}")

        return "\n".join(parts)


class JobManager:
    """Manages job postings storage and retrieval."""

    def __init__(self):
        """Initialize job manager."""
        JOBS_DIR.mkdir(parents=True, exist_ok=True)

    def add_job(self, job: Job) -> str:
        """Save a job posting."""
        job_file = JOBS_DIR / f"{job.job_id}.json"

        with open(job_file, 'w', encoding='utf-8') as f:
            json.dump(job.to_dict(), f, indent=2)

        print(f"Job saved: {job.title} at {job.company} (ID: {job.job_id})")
        return job.job_id

    def get_job(self, job_id: str) -> Optional[Job]:
        """Retrieve a job by ID."""
        job_file = JOBS_DIR / f"{job_id}.json"

        if not job_file.exists():
            return None

        with open(job_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return Job.from_dict(data)

    def get_all_jobs(self) -> List[Job]:
        """Retrieve all saved jobs."""
        jobs = []

        for job_file in JOBS_DIR.glob("*.json"):
            with open(job_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                jobs.append(Job.from_dict(data))

        # Sort by added date (newest first)
        jobs.sort(key=lambda j: j.added_date, reverse=True)
        return jobs

    def update_job_scores(self, job_id: str, scores: Dict) -> bool:
        """Update job scores after matching."""
        job = self.get_job(job_id)
        if not job:
            return False

        job.scores = scores
        self.add_job(job)  # Overwrite existing
        return True

    def delete_job(self, job_id: str) -> bool:
        """Delete a job posting."""
        job_file = JOBS_DIR / f"{job_id}.json"

        if job_file.exists():
            job_file.unlink()
            print(f"Job deleted: {job_id}")
            return True

        return False

    def fetch_from_url(self, url: str) -> Optional[Job]:
        """Attempt to fetch job details from a URL.

        This is a basic implementation that tries to extract
        job information from a webpage. May not work for all sites.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Try to extract basic information
            # This is very generic and may need customization per site
            title = None
            company = None
            description = None

            # Common patterns for job titles
            for selector in ['h1', '.job-title', '.jobsearch-JobInfoHeader-title']:
                element = soup.select_one(selector)
                if element:
                    title = element.get_text(strip=True)
                    break

            # Common patterns for company names
            for selector in ['.company', '.employer', '[data-company-name]']:
                element = soup.select_one(selector)
                if element:
                    company = element.get_text(strip=True)
                    break

            # Try to get job description
            for selector in ['.job-description', '.description', '#job-description']:
                element = soup.select_one(selector)
                if element:
                    description = element.get_text(separator='\n', strip=True)
                    break

            # If we couldn't parse, fall back to body text
            if not description:
                body = soup.find('body')
                if body:
                    description = body.get_text(separator='\n', strip=True)[:5000]

            if title and description:
                return Job(
                    title=title or "Unknown Title",
                    company=company or "Unknown Company",
                    description=description,
                    url=url,
                )

            print("Warning: Could not extract complete job information from URL")
            return None

        except Exception as e:
            print(f"Error fetching job from URL: {e}")
            return None


def interactive_add_job() -> Optional[Job]:
    """Interactive CLI for adding a job posting."""
    print("\n=== Add New Job Posting ===\n")

    # Ask for input method
    print("How would you like to add this job?")
    print("1. Paste job URL (attempt auto-fetch)")
    print("2. Enter details manually")
    choice = input("\nChoice (1 or 2): ").strip()

    manager = JobManager()

    if choice == "1":
        url = input("\nJob URL: ").strip()
        print("\nAttempting to fetch job details...")

        job = manager.fetch_from_url(url)

        if job:
            print(f"\nExtracted:")
            print(f"  Title: {job.title}")
            print(f"  Company: {job.company}")
            print(f"  Description: {job.description[:200]}...")

            confirm = input("\nLooks good? (y/n): ").strip().lower()
            if confirm != 'y':
                print("Let's enter details manually instead...")
                job = None

        if not job:
            print("\nAuto-fetch failed or rejected. Falling back to manual entry...")
            choice = "2"

    if choice == "2":
        title = input("\nJob Title: ").strip()
        company = input("Company Name: ").strip()

        print("\nJob Description (paste full description, then press Enter twice):")
        description_lines = []
        empty_line_count = 0
        while empty_line_count < 2:
            line = input()
            if line.strip():
                description_lines.append(line)
                empty_line_count = 0
            else:
                empty_line_count += 1

        description = "\n".join(description_lines)

        url = input("\nJob URL (optional): ").strip() or None
        location = input("Location (optional): ").strip() or None

        remote_input = input("Remote? (y/n): ").strip().lower()
        remote = remote_input == 'y'

        salary_input = input("Salary range (e.g., '70000-90000' or press Enter to skip): ").strip()
        salary_min = None
        salary_max = None

        if salary_input and '-' in salary_input:
            try:
                parts = salary_input.split('-')
                salary_min = int(parts[0].strip())
                salary_max = int(parts[1].strip())
            except ValueError:
                print("Invalid salary format, skipping...")

        job = Job(
            title=title,
            company=company,
            description=description,
            url=url,
            location=location,
            salary_min=salary_min,
            salary_max=salary_max,
            remote=remote,
        )

    return job


if __name__ == "__main__":
    # Test interactive job addition
    job = interactive_add_job()

    if job:
        manager = JobManager()
        job_id = manager.add_job(job)
        print(f"\nJob added successfully! ID: {job_id}")
