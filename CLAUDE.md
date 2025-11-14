# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

JobHelper is a personal job search assistance tool designed to help match job postings with a candidate profile, generate tailored resumes, and streamline the job application process.

**Current Status:** Functional MVP with profile vectorization, job matching, and resume generation implemented.

## Project Structure

```
JobHelper/
├── job_profile_document.md      # Career profile (source of truth)
├── requirements.txt              # Python dependencies
├── .env.example                  # Configuration template
├── src/
│   ├── main.py                   # CLI entry point
│   ├── config.py                 # Configuration management
│   ├── profile_vectorizer.py    # Profile parsing & embedding
│   ├── job_manager.py            # Job storage & retrieval
│   ├── job_matcher.py            # Vector matching & scoring
│   └── resume_generator.py      # Tailored resume generation
└── data/
    ├── profile_embedding.npy     # Profile vector (generated)
    ├── jobs/                     # Job postings (JSON)
    └── resumes/                  # Generated resumes
```

## Core Concepts

### Career Profile Document
The `job_profile_document.md` file serves as the source of truth for:
- Technical skills (tiered by proficiency: Expert, Intermediate, Foundational)
- Work preferences (remote, compensation range, culture fit criteria)
- Professional experience and accomplishments
- Ideal role profile and company culture preferences
- Red flags and deal-breakers for job opportunities
- Application strategy and tracking methodology

### Implemented Functionality
The system currently provides:
1. **Profile Vectorization** - Converts career profile into semantic embeddings using sentence-transformers
2. **Job Management** - Manual job input (paste URL or enter details), storage as JSON
3. **Dual Scoring** - Matches jobs using:
   - Technical fit (60%): Vector similarity between profile and job description
   - Culture fit (40%): Rule-based scoring against preferences and red flags
4. **Resume Generation** - Creates tailored resumes in Markdown/TXT/HTML formats based on role type
5. **CLI Interface** - Commands for init, add-job, match, list, show, generate-resume, delete

### Planned Future Features
- Automated job board scraping (LinkedIn, Indeed)
- Glassdoor integration for culture research
- Application tracking system
- Email notifications for high-match jobs

## Key Information for Development

### Privacy & Sensitive Data
- The profile contains personal information (name, email, phone, location)
- Never commit API keys, credentials, or tokens
- Consider `.gitignore` for any generated files containing sensitive data
- If building web scraping features, respect robots.txt and rate limits

### Career Profile Anchors
When building job matching or resume generation features, key profile elements to prioritize:

**Technical Focus:**
- WordPress (8+ years) - primary expertise
- Vanilla JavaScript (strong preference over frameworks)
- Frontend development with backend templating/styling
- PHP backend logic
- SQL/Database integration

**Compensation & Work Arrangement:**
- Target range: $70k-$90k
- High preference for remote work (80%+)
- Geographic: Fort Wayne, IN or Grand Rapids, MI (or fully remote)

**Culture Priorities:**
- Mission-driven organizations (education, healthcare, social good)
- People-first culture with work-life balance
- Growth opportunities and clear career progression
- Psychological safety and collaborative environment

**Red Flags to Filter:**
- Micromanagement signals
- Poor work-life balance indicators
- Glassdoor rating <3.0 or >30% negative balance reviews
- High turnover patterns

### Resume Customization Strategy
The profile defines different emphasis points depending on role type:
- **WordPress roles:** Emphasize 8+ years experience, custom plugins, cost optimization
- **Full-stack roles:** Cross-functional experience, database integration, multiple tech stacks
- **Frontend roles:** UX focus, accessibility, design + technical background
- **Agency roles:** Client communication, project management, business requirements translation
- **Mission-driven roles:** Collaboration, problem-solving, reliability, mission alignment

## Common Commands

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows

# Install dependencies
pip install -r requirements.txt

# Copy configuration template
cp .env.example .env
```

### Usage
```bash
# Initialize (one-time setup)
python src/main.py init

# Add a job posting
python src/main.py add-job

# Match all jobs against profile
python src/main.py match
python src/main.py match --all    # Show all, including low scores

# List saved jobs
python src/main.py list

# Show job details
python src/main.py show <job-id>

# Generate custom resume
python src/main.py generate-resume <job-id>
python src/main.py generate-resume <job-id> --format html

# Delete a job
python src/main.py delete <job-id>
```

### Testing Individual Modules
```bash
# Test profile vectorization
python src/profile_vectorizer.py

# Test job matching
python src/job_matcher.py

# Test resume generation
python src/resume_generator.py
```

## Architecture & Implementation Details

### Profile Vectorization (profile_vectorizer.py)
- Parses Markdown profile into structured data (skills, preferences, red flags, accomplishments)
- Creates focused embedding text emphasizing technical skills and key accomplishments
- Uses sentence-transformers (all-MiniLM-L6-v2 by default) for semantic embeddings
- Saves embedding to `data/profile_embedding.npy` for reuse
- Profile data extraction uses regex patterns to parse specific sections

### Job Matching (job_matcher.py)
- **Technical Score**: Cosine similarity between profile and job embeddings
- **Culture Score**: Rule-based scoring that checks:
  - Work arrangement (remote, salary, location) - 40%
  - Culture priorities (keywords: work-life balance, growth, mission, collaborative) - 30%
  - Red flags (micromanagement, poor balance, toxic keywords) - 30% (penalties)
  - Bonuses for role type alignment and industry match
- **Dual Scoring**: Weighted combination (default 60% technical / 40% culture)
- Filters jobs by minimum thresholds (configurable in .env)
- Saves scores back to job JSON files

### Job Storage (job_manager.py)
- Jobs stored as individual JSON files in `data/jobs/`
- Each job has UUID, supports manual entry or URL fetch (basic scraping)
- URL fetching attempts to extract title, company, description from common HTML patterns
- Not all job sites will parse correctly - manual entry is more reliable
- Jobs include metadata: title, company, description, location, remote flag, salary range, scores

### Resume Generation (resume_generator.py)
- Detects role type from job title (wordpress, frontend, full-stack, agency, mission-driven)
- Selects relevant skills that appear in job description
- Scores and ranks accomplishments by keyword relevance to job
- Generates role-specific summary statement
- Supports Markdown, TXT, and HTML output formats
- Uses Jinja2 templates for formatting

### Configuration (config.py)
- Loads settings from .env file
- Validates scoring weights sum to 1.0
- Configurable: embedding model, score weights, minimum thresholds
- Can switch to OpenAI embeddings by changing EMBEDDING_MODEL (requires API key)

## Development Considerations

### When Adding Features

**Job Board Scraping:**
- Start with one board at a time (LinkedIn, Indeed, etc.)
- Each site has different HTML structure - will need custom parsers
- Consider using Selenium/Playwright for JavaScript-rendered content
- Respect rate limits and robots.txt
- Store raw HTML for debugging failed parses

**Glassdoor Integration:**
- Requires API key or scraping (scraping may violate ToS)
- Match company names (fuzzy matching needed - "ABC Corp" vs "ABC Corporation")
- Extract: overall rating, review highlights, work-life balance score
- Integrate into culture scoring algorithm

**Application Tracking:**
- Store application status (interested, applied, interviewing, rejected, offer)
- Track dates for follow-up reminders
- Link to generated resume and cover letter
- Could extend Job model or create separate Application model

**Testing:**
- Add pytest tests for profile parsing, scoring logic, resume generation
- Mock sentence-transformers for faster tests
- Use sample job JSON files for test fixtures

### Code Architecture Notes
- All modules can run standalone with `if __name__ == "__main__"` blocks for testing
- Profile data is parsed once and reused across modules
- Job embeddings are created on-demand (could cache if needed for performance)
- CLI uses argparse with subcommands pattern
- Scoring weights and thresholds are externalized to config for easy tuning

### Important Patterns
- Profile is source of truth - never edit generated files manually
- Jobs are immutable except for score updates
- Resume generation is deterministic given same job input
- Embedding model can be swapped without changing code logic
