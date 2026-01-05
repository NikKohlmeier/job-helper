#!/usr/bin/env python3
"""Job Board Scraper - Scrapes job listings from various job boards."""

import re
import time
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from urllib.parse import urlencode, urljoin, urlparse
import requests
from bs4 import BeautifulSoup

from config import SCRAPE_KEYWORDS


class JobBoardScraper:
    """Scrapes job listings from various job boards."""

    def __init__(self):
        """Initialize the scraper."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,application/rss+xml,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # Don't request compression - let requests handle it automatically
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def search_we_work_remotely(
        self,
        keywords: Optional[List[str]] = None,
        category: str = "remote-programming-jobs",
        max_results: int = 20
    ) -> List[Dict]:
        """
        Scrape jobs from We Work Remotely (weworkremotely.com).
        Uses RSS feed which is more reliable than HTML scraping.
        
        Args:
            keywords: List of keywords to filter jobs (defaults to config keywords)
            category: Job category (remote-programming-jobs, remote-design-jobs, etc.)
            max_results: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries with url, title, company, location, remote flags
        """
        if keywords is None:
            keywords = SCRAPE_KEYWORDS
        
        jobs = []
        
        try:
            # We Work Remotely RSS feed
            base_url = "https://weworkremotely.com"
            rss_url = f"{base_url}/categories/{category}"
            
            print(f"Scraping We Work Remotely RSS: {rss_url}")
            
            # Request with RSS-specific headers
            rss_headers = {
                'Accept': 'application/rss+xml, application/xml, text/xml, */*',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = self.session.get(rss_url, headers=rss_headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            # Requests should auto-decompress, use response.text
            content_str = response.text
            
            # Check if we got RSS/XML
            if '<?xml' not in content_str[:100] and '<rss' not in content_str[:100]:
                print(f"Warning: Got HTML instead of RSS. Trying to find RSS link...")
                # Try to find RSS link in HTML
                soup = BeautifulSoup(content_str, 'html.parser')
                rss_link = soup.find('link', {'type': 'application/rss+xml'})
                if rss_link and rss_link.get('href'):
                    rss_url = urljoin(base_url, rss_link['href'])
                    print(f"Found RSS link: {rss_url}")
                    response = self.session.get(rss_url, headers=rss_headers, timeout=15)
                    response.raise_for_status()
                    content_str = response.text
                else:
                    print("Could not find RSS feed")
                    return jobs
            use_etree = False
            use_text_parse = False
            
            # Simple regex-based parsing for RSS (most reliable)
            import re
            # Match items - handle multiline with DOTALL flag
            item_pattern = r'<item>(.*?)</item>'
            items_text = re.findall(item_pattern, content_str, re.DOTALL)
            
            # If no matches, try alternative pattern
            if not items_text:
                item_count = len(re.findall(r'<item>', content_str))
                if item_count > 0:
                    # Try matching without requiring closing tag
                    item_pattern = r'<item>(.*?)(?=<item>|</channel>|$)'
                    items_text = re.findall(item_pattern, content_str, re.DOTALL)
            items = []
            for item_text in items_text:
                # Extract title - handle CDATA and HTML entities
                title_match = re.search(r'<title>(.*?)</title>', item_text, re.DOTALL)
                link_match = re.search(r'<link>(.*?)</link>', item_text, re.DOTALL)
                region_match = re.search(r'<region>(.*?)</region>', item_text, re.DOTALL)
                
                if title_match and link_match:
                    title = title_match.group(1).strip()
                    # Remove CDATA wrapper if present
                    title = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', title, flags=re.DOTALL)
                    
                    link = link_match.group(1).strip()
                    region = region_match.group(1).strip() if region_match else 'Remote'
                    
                    items.append({
                        'title': title,
                        'link': link,
                        'region': region
                    })
            use_text_parse = True
            
            print(f"Found {len(items)} items in RSS feed")
            
            # Process all items and filter, then limit
            for item in items:
                try:
                    # Handle different parsing methods
                    if use_etree:
                        # ElementTree - handle namespaces
                        title_elem = item.find('.//title') or item.find('title')
                        title_text = title_elem.text if title_elem is not None else ""
                        link_elem = item.find('.//link') or item.find('link')
                        job_url = link_elem.text if link_elem is not None else None
                        region_elem = item.find('.//region') or item.find('region')
                        location = region_elem.text if region_elem is not None else "Remote"
                    elif use_text_parse:
                        # Text-based parsing result
                        title_text = item.get('title', '')
                        job_url = item.get('link', '')
                        location = item.get('region', 'Remote')
                    else:
                        # BeautifulSoup fallback
                        title_elem = item.find('title')
                        title_text = title_elem.get_text(strip=True) if title_elem else ""
                        link_elem = item.find('link')
                        job_url = link_elem.get_text(strip=True) if link_elem is not None else None
                        if not job_url:
                            guid_elem = item.find('guid')
                            if guid_elem:
                                job_url = guid_elem.get_text(strip=True)
                        region_elem = item.find('region')
                        location = region_elem.get_text(strip=True) if region_elem is not None else "Remote"
                    
                    if not title_text or not job_url:
                        continue
                    
                    # Parse "Company: Job Title" format
                    if ':' in title_text:
                        parts = title_text.split(':', 1)
                        company = parts[0].strip()
                        title = parts[1].strip()
                    else:
                        company = "Unknown Company"
                        title = title_text.strip()
                    
                    if not job_url:
                        continue
                    
                    # Check if job matches keywords (case-insensitive)
                    title_lower = title.lower()
                    description_lower = ""  # We don't have description yet from RSS
                    
                    # Match if any keyword appears in title or company
                    # Also include common developer terms if keywords are programming-related
                    company_lower = company.lower()
                    
                    # Expand keywords with common variations for programming jobs
                    expanded_keywords = list(keywords)
                    # Check if we're looking for programming-related jobs
                    has_programming_keywords = any(
                        kw.lower() in ['wordpress', 'frontend', 'javascript', 'php', 'web', 'developer', 'programmer']
                        for kw in keywords
                    )
                    
                    if has_programming_keywords:
                        # Add general developer terms
                        expanded_keywords.extend(['developer', 'programmer', 'engineer', 'development', 'software'])
                    
                    matches = any(
                        keyword.lower() in title_lower or 
                        keyword.lower() in company_lower
                        for keyword in expanded_keywords
                    )
                    
                    if not matches:
                        continue
                    
                    # All We Work Remotely jobs are remote
                    job_data = {
                        'url': job_url,
                        'title': title,
                        'company': company,
                        'location': location,
                        'remote': True,
                        'source': 'We Work Remotely',
                        'description': None,  # Will be fetched when user adds job
                    }
                    
                    jobs.append(job_data)
                    
                    # Stop if we have enough
                    if len(jobs) >= max_results:
                        break
                    
                except Exception as e:
                    print(f"Error parsing RSS item: {e}")
                    continue
            
            print(f"✓ Found {len(jobs)} matching jobs from We Work Remotely")
            
        except Exception as e:
            print(f"Error scraping We Work Remotely: {e}")
            import traceback
            traceback.print_exc()
        
        return jobs

    def search_github_jobs(
        self,
        keywords: Optional[List[str]] = None,
        location: str = "remote",
        max_results: int = 20
    ) -> List[Dict]:
        """
        Scrape jobs from GitHub Jobs (jobs.github.com).
        
        Note: GitHub Jobs was deprecated, but some companies still use similar patterns.
        This searches for GitHub-related job boards.
        
        Args:
            keywords: List of keywords to filter jobs
            location: Location filter (default: remote)
            max_results: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        if keywords is None:
            keywords = SCRAPE_KEYWORDS
        
        jobs = []
        
        try:
            # GitHub Jobs alternative: jobs.github.com redirects, but we can try
            # Many companies post on their own sites with GitHub in the URL
            # For now, we'll search a common pattern
            
            # Try searching for GitHub Jobs RSS or similar
            search_url = "https://jobs.github.com/positions.json"
            params = {
                'description': ' '.join(keywords[:3]),  # Use first 3 keywords
                'location': location
            }
            
            print(f"Searching GitHub Jobs: {search_url}")
            
            response = self.session.get(search_url, params=params, timeout=15)
            
            # GitHub Jobs API might be deprecated, so handle gracefully
            if response.status_code == 200:
                try:
                    data = response.json()
                    for job in data[:max_results]:
                        jobs.append({
                            'url': job.get('url', ''),
                            'title': job.get('title', ''),
                            'company': job.get('company', ''),
                            'location': job.get('location', ''),
                            'remote': 'remote' in job.get('location', '').lower(),
                            'source': 'GitHub Jobs',
                            'description': job.get('description', ''),
                        })
                except:
                    pass  # Not JSON, might be HTML
            
            # If API doesn't work, try HTML scraping
            if not jobs:
                html_url = "https://jobs.github.com/positions"
                response = self.session.get(html_url, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Parse HTML structure (would need to inspect actual site)
                    # For now, return empty if API doesn't work
                    pass
            
            print(f"✓ Found {len(jobs)} jobs from GitHub Jobs")
            
        except Exception as e:
            print(f"Error scraping GitHub Jobs: {e}")
        
        return jobs

    def search_remoteok(
        self,
        keywords: Optional[List[str]] = None,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Scrape jobs from RemoteOK (remoteok.com).
        Uses JSON API which is more reliable than HTML scraping.
        
        Args:
            keywords: List of keywords to filter jobs
            max_results: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        if keywords is None:
            keywords = SCRAPE_KEYWORDS
        
        jobs = []
        
        try:
            base_url = "https://remoteok.com"
            # RemoteOK has a JSON endpoint
            json_url = f"{base_url}/remote-dev-jobs.json"
            
            print(f"Scraping RemoteOK JSON: {json_url}")
            
            response = self.session.get(json_url, timeout=15)
            response.raise_for_status()
            
            # Parse JSON - handle potential errors
            try:
                data = response.json()
            except json.JSONDecodeError:
                # Might be HTML or empty response
                print("RemoteOK returned non-JSON response, trying HTML parsing")
                soup = BeautifulSoup(response.content, 'html.parser')
                # Look for JSON data in script tags or try HTML parsing
                # For now, return empty and log
                return jobs
            
            # RemoteOK JSON is an array of job objects
            if not isinstance(data, list):
                print("Unexpected JSON format from RemoteOK")
                return jobs
            
            print(f"Found {len(data)} jobs in JSON")
            
            for job_data in data[:max_results * 2]:  # Get more to filter
                try:
                    # Skip header row if present
                    if not isinstance(job_data, dict) or 'id' not in job_data:
                        continue
                    
                    title = job_data.get('position', '') or job_data.get('title', '')
                    company = job_data.get('company', 'Unknown Company')
                    job_url = job_data.get('url', '')
                    
                    # Construct full URL if relative
                    if job_url and not job_url.startswith('http'):
                        job_url = urljoin(base_url, job_url)
                    elif not job_url:
                        # RemoteOK jobs have IDs, construct URL
                        job_id = job_data.get('id', '')
                        if job_id:
                            job_url = f"{base_url}/remote-jobs/{job_id}"
                    
                    # Check keywords
                    title_lower = title.lower()
                    if not any(keyword.lower() in title_lower for keyword in keywords):
                        continue
                    
                    jobs.append({
                        'url': job_url,
                        'title': title,
                        'company': company,
                        'location': 'Remote',
                        'remote': True,
                        'source': 'RemoteOK',
                        'description': None,
                    })
                    
                    if len(jobs) >= max_results:
                        break
                    
                except Exception as e:
                    print(f"Error parsing RemoteOK job: {e}")
                    continue
            
            print(f"✓ Found {len(jobs)} matching jobs from RemoteOK")
            
        except Exception as e:
            print(f"Error scraping RemoteOK: {e}")
            import traceback
            traceback.print_exc()
        
        return jobs

    def search_all_boards(
        self,
        keywords: Optional[List[str]] = None,
        boards: Optional[List[str]] = None,
        max_results_per_board: int = 20
    ) -> List[Dict]:
        """
        Search all configured job boards.
        
        Args:
            keywords: List of keywords to search for
            boards: List of board names to search (None = all)
            max_results_per_board: Max results per board
            
        Returns:
            Combined list of jobs from all boards
        """
        if boards is None:
            boards = ['we_work_remotely', 'remoteok']  # Start with easy ones
        
        all_jobs = []
        
        for board in boards:
            try:
                if board == 'we_work_remotely':
                    jobs = self.search_we_work_remotely(keywords, max_results=max_results_per_board)
                elif board == 'remoteok':
                    jobs = self.search_remoteok(keywords, max_results=max_results_per_board)
                elif board == 'github_jobs':
                    jobs = self.search_github_jobs(keywords, max_results=max_results_per_board)
                else:
                    print(f"Unknown board: {board}")
                    continue
                
                all_jobs.extend(jobs)
                
                # Be polite - add delay between requests
                time.sleep(1)
                
            except Exception as e:
                print(f"Error searching {board}: {e}")
                continue
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        print(f"\n✓ Total unique jobs found: {len(unique_jobs)}")
        
        return unique_jobs


# Test functionality
if __name__ == "__main__":
    scraper = JobBoardScraper()
    
    print("\n" + "="*60)
    print("Testing Job Board Scraper")
    print("="*60 + "\n")
    
    # Test We Work Remotely
    print("Testing We Work Remotely...")
    jobs = scraper.search_we_work_remotely(max_results=5)
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   URL: {job['url']}")
        print(f"   Source: {job['source']}")

