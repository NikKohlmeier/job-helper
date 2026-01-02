"""Configuration management for JobHelper."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
JOBS_DIR = DATA_DIR / "jobs"
RESUMES_DIR = DATA_DIR / "resumes"
CACHE_DIR = DATA_DIR / "cache"
SCRAPED_JOBS_DIR = DATA_DIR / "scraped"
PROFILE_PATH = PROJECT_ROOT / "job_profile_document.md"
PROFILE_EMBEDDING_PATH = DATA_DIR / "profile_embedding.npy"

# Ensure directories exist
for directory in [DATA_DIR, JOBS_DIR, RESUMES_DIR, CACHE_DIR, SCRAPED_JOBS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def get_secret(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Get a secret value with fallback chain:
    1. System keyring (most secure)
    2. Environment variable / .env file
    3. Default value
    
    Args:
        key: The secret/config key name
        default: Default value if not found anywhere
        
    Returns:
        The secret value or default
    """
    # Try keyring first (silently - don't spam warnings)
    try:
        from secrets_manager import get_secret as keyring_get
        value = keyring_get(key, silent=True)
        if value:
            return value
    except ImportError:
        pass  # secrets_manager not available
    except Exception:
        pass  # keyring error, fall through
    
    # Fall back to environment variable
    value = os.getenv(key)
    if value:
        return value
    
    return default


# Embedding configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Scoring weights
TECHNICAL_WEIGHT = float(os.getenv("TECHNICAL_WEIGHT", "0.6"))
CULTURE_WEIGHT = float(os.getenv("CULTURE_WEIGHT", "0.4"))

# Minimum scores
MIN_TECHNICAL_SCORE = float(os.getenv("MIN_TECHNICAL_SCORE", "0.65"))
MIN_CULTURE_SCORE = float(os.getenv("MIN_CULTURE_SCORE", "0.50"))
MIN_OVERALL_SCORE = float(os.getenv("MIN_OVERALL_SCORE", "0.60"))

# Scraping configuration
SCRAPE_KEYWORDS = os.getenv(
    "SCRAPE_KEYWORDS", 
    "wordpress,frontend,javascript,php,web developer"
).split(",")
SCRAPE_KEYWORDS = [k.strip() for k in SCRAPE_KEYWORDS if k.strip()]

# API keys (using secure fallback chain)
GLASSDOOR_API_KEY = get_secret("GLASSDOOR_API_KEY")
OPENAI_API_KEY = get_secret("OPENAI_API_KEY")

# Email/SMTP configuration (using secure fallback chain)
SMTP_HOST = get_secret("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(get_secret("SMTP_PORT", "587"))
SMTP_USER = get_secret("SMTP_USER")
SMTP_PASSWORD = get_secret("SMTP_PASSWORD")
NOTIFY_EMAIL = get_secret("NOTIFY_EMAIL")

# Validation
if not (0 <= TECHNICAL_WEIGHT <= 1 and 0 <= CULTURE_WEIGHT <= 1):
    raise ValueError("Weights must be between 0 and 1")

if abs(TECHNICAL_WEIGHT + CULTURE_WEIGHT - 1.0) > 0.01:
    raise ValueError(f"Weights must sum to 1.0 (got {TECHNICAL_WEIGHT + CULTURE_WEIGHT})")
