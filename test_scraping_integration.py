#!/usr/bin/env python3
"""Test scraping feature integration without requiring dependencies."""

import ast
import re
from pathlib import Path


def check_file_for_patterns(file_path, patterns, description):
    """Check if a file contains certain patterns."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        found = []
        for pattern, name in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found.append(name)
        
        if found:
            print(f"  ✓ {description}: {', '.join(found)}")
            return True
        else:
            print(f"  ✗ {description}: Not found")
            return False
    except Exception as e:
        print(f"  ✗ Error reading {file_path}: {e}")
        return False


def test_scraping_integration():
    """Test scraping feature integration by examining code structure."""
    print("=" * 60)
    print("Scraping Features Integration Test")
    print("=" * 60)
    
    src_dir = Path(__file__).parent / 'src'
    results = {}
    
    # 1. Check basic scraper in job_manager
    print("\n1. Basic Scraper (job_manager.py)")
    print("-" * 60)
    job_manager_path = src_dir / 'job_manager.py'
    
    if job_manager_path.exists():
        patterns = [
            (r'def fetch_from_url', 'fetch_from_url method'),
            (r'requests\.get', 'requests library usage'),
            (r'BeautifulSoup', 'BeautifulSoup usage'),
        ]
        results['basic_scraper'] = check_file_for_patterns(
            job_manager_path, patterns, "Basic scraper features"
        )
    else:
        print("  ✗ job_manager.py not found")
        results['basic_scraper'] = False
    
    # 2. Check AI scraper
    print("\n2. AI Scraper (ai_scraper.py)")
    print("-" * 60)
    ai_scraper_path = src_dir / 'ai_scraper.py'
    
    if ai_scraper_path.exists():
        patterns = [
            (r'class AIJobScraper', 'AIJobScraper class'),
            (r'def fetch_job_from_url', 'fetch_job_from_url method'),
            (r'OpenAI', 'OpenAI integration'),
            (r'requests\.get', 'HTTP requests'),
        ]
        results['ai_scraper'] = check_file_for_patterns(
            ai_scraper_path, patterns, "AI scraper features"
        )
    else:
        print("  ✗ ai_scraper.py not found")
        results['ai_scraper'] = False
    
    # 3. Check browser agent
    print("\n3. Browser Agent Integration")
    print("-" * 60)
    browser_agent_path = src_dir / 'browser_agent.py'
    
    if browser_agent_path.exists():
        print("  ✓ browser_agent.py exists")
        patterns = [
            (r'playwright|selenium', 'Browser automation library'),
            (r'def.*fetch|def.*scrape', 'Scraping methods'),
        ]
        check_file_for_patterns(
            browser_agent_path, patterns, "Browser agent features"
        )
        results['browser_agent'] = True
    else:
        print("  ✗ browser_agent.py not found (not yet implemented)")
        results['browser_agent'] = False
    
    # 4. Check web API integration
    print("\n4. Web API Integration (app.py)")
    print("-" * 60)
    app_path = Path(__file__).parent / 'app.py'
    
    if app_path.exists():
        patterns = [
            (r'/api/jobs/fetch-url', 'fetch-url endpoint'),
            (r'ai_scraper\.fetch_job_from_url', 'AI scraper usage'),
            (r'job_manager\.fetch_from_url', 'Basic scraper usage'),
        ]
        results['web_api'] = check_file_for_patterns(
            app_path, patterns, "Web API scraping endpoints"
        )
    else:
        print("  ✗ app.py not found")
        results['web_api'] = False
    
    # 5. Check requirements
    print("\n5. Dependencies (requirements.txt)")
    print("-" * 60)
    requirements_path = Path(__file__).parent / 'requirements.txt'
    
    if requirements_path.exists():
        with open(requirements_path) as f:
            content = f.read()
        
        deps = {
            'requests': 'requests' in content,
            'beautifulsoup4': 'beautifulsoup4' in content or 'bs4' in content,
            'openai': 'openai' in content,
            'playwright': 'playwright' in content.lower(),
            'selenium': 'selenium' in content.lower(),
        }
        
        for dep, found in deps.items():
            status = "✓" if found else "✗"
            print(f"  {status} {dep}")
        
        results['dependencies'] = any([
            deps['requests'],
            deps['beautifulsoup4'],
            deps['openai']
        ])
    else:
        print("  ✗ requirements.txt not found")
        results['dependencies'] = False
    
    # 6. Check config integration
    print("\n6. Configuration Integration (config.py)")
    print("-" * 60)
    config_path = src_dir / 'config.py'
    
    if config_path.exists():
        patterns = [
            (r'OPENAI_API_KEY', 'OpenAI API key config'),
            (r'SCRAPED_JOBS_DIR', 'Scraped jobs directory'),
            (r'get_secret', 'Secret management integration'),
        ]
        results['config'] = check_file_for_patterns(
            config_path, patterns, "Scraping configuration"
        )
    else:
        print("  ✗ config.py not found")
        results['config'] = False
    
    # 7. Check if browser agent is integrated into scrapers
    print("\n7. Browser Agent Integration in Scrapers")
    print("-" * 60)
    
    integration_found = False
    
    # Check job_manager
    if job_manager_path.exists():
        with open(job_manager_path) as f:
            content = f.read()
            if 'browser_agent' in content or 'BrowserAgent' in content:
                print("  ✓ Browser agent used in job_manager.py")
                integration_found = True
    
    # Check ai_scraper
    if ai_scraper_path.exists():
        with open(ai_scraper_path) as f:
            content = f.read()
            if 'browser_agent' in content or 'BrowserAgent' in content:
                print("  ✓ Browser agent used in ai_scraper.py")
                integration_found = True
    
    if not integration_found:
        print("  ✗ Browser agent not integrated into scrapers")
    
    results['browser_integration'] = integration_found
    
    # Summary
    print("\n" + "=" * 60)
    print("Integration Summary")
    print("=" * 60)
    
    status_map = {
        'basic_scraper': 'Basic Scraper (job_manager)',
        'ai_scraper': 'AI Scraper',
        'browser_agent': 'Browser Agent Module',
        'web_api': 'Web API Integration',
        'dependencies': 'Dependencies',
        'config': 'Configuration',
        'browser_integration': 'Browser Agent Integration',
    }
    
    for key, label in status_map.items():
        result = results.get(key, False)
        status = "✓ INTEGRATED" if result else "✗ NOT INTEGRATED"
        print(f"  {label:30} {status}")
    
    # Overall assessment
    print("\n" + "=" * 60)
    core_features = ['basic_scraper', 'ai_scraper', 'web_api', 'config']
    core_working = all(results.get(k, False) for k in core_features)
    
    if core_working:
        print("✓ Core scraping features are integrated")
    else:
        print("✗ Some core scraping features are missing")
    
    if results.get('browser_agent') or results.get('browser_integration'):
        print("✓ Browser agent features are integrated")
    else:
        print("⚠ Browser agent features are NOT yet integrated (planned feature)")
    
    print("=" * 60)


if __name__ == "__main__":
    test_scraping_integration()



