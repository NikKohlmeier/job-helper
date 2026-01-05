#!/usr/bin/env python3
"""Test script for scraping features."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all scraping modules can be imported."""
    print("=" * 60)
    print("Testing Module Imports")
    print("=" * 60)
    
    try:
        from job_manager import JobManager, Job
        print("✓ job_manager imported successfully")
    except Exception as e:
        print(f"✗ Failed to import job_manager: {e}")
        return False
    
    try:
        from ai_scraper import AIJobScraper
        print("✓ ai_scraper imported successfully")
    except Exception as e:
        print(f"✗ Failed to import ai_scraper: {e}")
        return False
    
    try:
        from config import OPENAI_API_KEY, SCRAPED_JOBS_DIR
        print("✓ config imported successfully")
        print(f"  - SCRAPED_JOBS_DIR: {SCRAPED_JOBS_DIR}")
        print(f"  - OPENAI_API_KEY configured: {'Yes' if OPENAI_API_KEY and OPENAI_API_KEY != 'your_openai_api_key_here' else 'No'}")
    except Exception as e:
        print(f"✗ Failed to import config: {e}")
        return False
    
    return True


def test_basic_scraper():
    """Test the basic scraper in job_manager."""
    print("\n" + "=" * 60)
    print("Testing Basic Scraper (job_manager.fetch_from_url)")
    print("=" * 60)
    
    try:
        from job_manager import JobManager
        
        manager = JobManager()
        
        # Test with a simple, static HTML site
        # Using a test URL that should work with basic scraping
        test_url = "https://job-boards.greenhouse.io/vultr/jobs/4602862006"
        
        print(f"\nTesting URL: {test_url}")
        print("Fetching...")
        
        job = manager.fetch_from_url(test_url)
        
        if job:
            print("\n✓ Basic scraper succeeded!")
            print(f"  Title: {job.title}")
            print(f"  Company: {job.company}")
            print(f"  Description length: {len(job.description)} chars")
            print(f"  URL: {job.url}")
            return True
        else:
            print("\n✗ Basic scraper failed to extract job data")
            return False
            
    except Exception as e:
        print(f"\n✗ Basic scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_scraper():
    """Test the AI scraper."""
    print("\n" + "=" * 60)
    print("Testing AI Scraper (ai_scraper.fetch_job_from_url)")
    print("=" * 60)
    
    try:
        from ai_scraper import AIJobScraper
        from config import OPENAI_API_KEY
        
        if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here':
            print("\n⚠ OpenAI API key not configured. Skipping AI scraper test.")
            print("  Set it with: python3 src/main.py secrets set OPENAI_API_KEY")
            return None
        
        scraper = AIJobScraper()
        
        if not scraper.has_api_key:
            print("\n⚠ AI scraper not initialized (no API key). Skipping test.")
            return None
        
        test_url = "https://job-boards.greenhouse.io/vultr/jobs/4602862006"
        
        print(f"\nTesting URL: {test_url}")
        print("Fetching and extracting with AI...")
        
        result = scraper.fetch_job_from_url(test_url)
        
        if result:
            print("\n✓ AI scraper succeeded!")
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  Company: {result.get('company', 'N/A')}")
            print(f"  Location: {result.get('location', 'N/A')}")
            print(f"  Remote: {result.get('remote', 'N/A')}")
            print(f"  Description length: {len(result.get('description', ''))} chars")
            print(f"  URL: {result.get('url', 'N/A')}")
            return True
        else:
            print("\n✗ AI scraper failed to extract job data")
            return False
            
    except Exception as e:
        print(f"\n✗ AI scraper test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_web_api_integration():
    """Test that the web API endpoints are properly set up."""
    print("\n" + "=" * 60)
    print("Testing Web API Integration")
    print("=" * 60)
    
    try:
        import app
        
        # Check if the fetch endpoint exists
        routes = []
        for rule in app.app.url_map.iter_rules():
            routes.append(rule.rule)
        
        print("\nAvailable API routes:")
        for route in sorted(routes):
            if '/api/' in route:
                print(f"  {route}")
        
        if '/api/jobs/fetch-url' in routes:
            print("\n✓ /api/jobs/fetch-url endpoint exists")
            return True
        else:
            print("\n✗ /api/jobs/fetch-url endpoint not found")
            return False
            
    except Exception as e:
        print(f"\n✗ Web API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_browser_agent_integration():
    """Check if browser agent features are integrated."""
    print("\n" + "=" * 60)
    print("Checking Browser Agent Integration")
    print("=" * 60)
    
    browser_agent_found = False
    
    # Check for browser agent module
    browser_agent_path = Path(__file__).parent / 'src' / 'browser_agent.py'
    if browser_agent_path.exists():
        print("\n✓ browser_agent.py module exists")
        browser_agent_found = True
    else:
        print("\n✗ browser_agent.py module not found")
    
    # Check requirements for playwright/selenium
    requirements_path = Path(__file__).parent / 'requirements.txt'
    if requirements_path.exists():
        with open(requirements_path) as f:
            content = f.read()
            if 'playwright' in content.lower():
                print("✓ Playwright found in requirements.txt")
                browser_agent_found = True
            elif 'selenium' in content.lower():
                print("✓ Selenium found in requirements.txt")
                browser_agent_found = True
            else:
                print("✗ No browser automation library in requirements.txt")
    
    # Check if browser agent is used in scraping code
    try:
        from job_manager import JobManager
        import inspect
        source = inspect.getsource(JobManager.fetch_from_url)
        if 'playwright' in source.lower() or 'selenium' in source.lower() or 'browser' in source.lower():
            print("✓ Browser agent code found in job_manager")
            browser_agent_found = True
        else:
            print("✗ No browser agent code in job_manager.fetch_from_url")
    except:
        pass
    
    try:
        from ai_scraper import AIJobScraper
        import inspect
        source = inspect.getsource(AIJobScraper.fetch_job_from_url)
        if 'playwright' in source.lower() or 'selenium' in source.lower() or 'browser' in source.lower():
            print("✓ Browser agent code found in ai_scraper")
            browser_agent_found = True
        else:
            print("✗ No browser agent code in ai_scraper.fetch_job_from_url")
    except:
        pass
    
    if not browser_agent_found:
        print("\n⚠ Browser agent features are NOT yet integrated.")
        print("  This is expected - browser automation is a planned feature.")
    
    return browser_agent_found


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("JobHelper Scraping Features Test Suite")
    print("=" * 60)
    
    results = {}
    
    # Test imports
    results['imports'] = test_imports()
    
    if not results['imports']:
        print("\n❌ Import tests failed. Please install dependencies:")
        print("   pip3 install -r requirements.txt")
        return
    
    # Test basic scraper
    results['basic_scraper'] = test_basic_scraper()
    
    # Test AI scraper
    results['ai_scraper'] = test_ai_scraper()
    
    # Test web API
    results['web_api'] = test_web_api_integration()
    
    # Check browser agent
    results['browser_agent'] = test_browser_agent_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is None:
            status = "⚠ SKIPPED"
        elif result:
            status = "✓ PASSED"
        else:
            status = "✗ FAILED"
        print(f"  {test_name:20} {status}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()



