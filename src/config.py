"""Configuration management for JobHelper."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
JOBS_DIR = DATA_DIR / "jobs"
RESUMES_DIR = DATA_DIR / "resumes"
CACHE_DIR = DATA_DIR / "cache"
PROFILE_PATH = PROJECT_ROOT / "job_profile_document.md"
PROFILE_EMBEDDING_PATH = DATA_DIR / "profile_embedding.npy"

# Ensure directories exist
for directory in [DATA_DIR, JOBS_DIR, RESUMES_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Embedding configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Scoring weights
TECHNICAL_WEIGHT = float(os.getenv("TECHNICAL_WEIGHT", "0.6"))
CULTURE_WEIGHT = float(os.getenv("CULTURE_WEIGHT", "0.4"))

# Minimum scores
MIN_TECHNICAL_SCORE = float(os.getenv("MIN_TECHNICAL_SCORE", "0.65"))
MIN_CULTURE_SCORE = float(os.getenv("MIN_CULTURE_SCORE", "0.50"))
MIN_OVERALL_SCORE = float(os.getenv("MIN_OVERALL_SCORE", "0.60"))

# API keys (optional)
GLASSDOOR_API_KEY = os.getenv("GLASSDOOR_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validation
if not (0 <= TECHNICAL_WEIGHT <= 1 and 0 <= CULTURE_WEIGHT <= 1):
    raise ValueError("Weights must be between 0 and 1")

if abs(TECHNICAL_WEIGHT + CULTURE_WEIGHT - 1.0) > 0.01:
    raise ValueError(f"Weights must sum to 1.0 (got {TECHNICAL_WEIGHT + CULTURE_WEIGHT})")
