# JobHelper 🎯

An AI-powered job search assistant that uses vector embeddings and OpenAI to intelligently match job postings with your career profile, provide personalized insights, generate tailored resumes, and create compelling cover letters.

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### Core Matching & Scoring
- 🎯 **Smart Job Matching** - Vector-based semantic similarity between your profile and job requirements
- 📊 **Dual Scoring System** - Technical fit (60%) + Culture fit (40%) = Overall match score
- 🔍 **Intelligent Filtering** - Configurable thresholds to surface only relevant opportunities

### AI-Powered Features (OpenAI)
- 🤖 **Smart Job Scraping** - Paste any job URL and AI extracts all details automatically
- 💡 **AI Insights** - Identifies skill gaps, transferable skills, and provides personalized recommendations
- ✉️ **Cover Letter Generation** - Creates tailored cover letters that reference specific job requirements
- 🎨 **Works Across All Sites** - Greenhouse, Lever, Indeed, company career pages, and more

### Resume & Document Generation
- 📄 **Tailored Resumes** - Generates customized resumes emphasizing relevant experience for each role
- 🔄 **Multiple Formats** - Supports Markdown, TXT, HTML, and DOCX (via Pandoc)
- 🎯 **Role-Specific Optimization** - Different emphasis for WordPress, Full-stack, Frontend, Agency roles

### Modern Web Interface
- 🌐 **Beautiful Dashboard** - Clean, responsive UI with job cards and match scores
- 📱 **Mobile-Friendly** - Works on desktop, tablet, and mobile
- ⚡ **Real-Time Updates** - Instant feedback and dynamic filtering
- 🎨 **Professional Design** - Bootstrap 5 with custom styling

### CLI Tools
- 💻 **Command-Line Interface** - Full-featured CLI for power users
- 🔧 **Scriptable** - Easy to integrate into workflows

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (tested on 3.12)
- OpenAI API key (optional, for AI features)
- Pandoc (optional, for DOCX resume generation)

### Installation

```bash
# Clone or download the repository
cd JobHelper

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy configuration template
cp .env.example .env

# Add your OpenAI API key to .env (optional)
# OPENAI_API_KEY=sk-your-key-here
```

### Initialize Your Profile

```bash
# Generate profile embeddings (one-time setup)
python src/main.py init
```

### Start the Web Interface

```bash
# Start the web server
python app.py

# Open your browser to:
# http://localhost:5001
```

---

## 🎨 Tech Stack

### Backend
- **Python 3.12** - Core language
- **Flask 3.0** - Web framework
- **OpenAI API** - AI-powered scraping, insights, and cover letter generation
- **sentence-transformers** - Open-source semantic embeddings (all-MiniLM-L6-v2)
- **scikit-learn** - Vector similarity calculations
- **BeautifulSoup4** - HTML parsing for web scraping
- **Jinja2** - Template rendering for resumes

### Frontend
- **Vanilla JavaScript** - No frameworks, clean and fast
- **Bootstrap 5.3** - UI components and responsive grid
- **Bootstrap Icons** - Icon library
- **Custom CSS** - Polished design and animations

### Data & Storage
- **JSON** - Job storage (simple, portable, human-readable)
- **NumPy** - Profile embedding storage (.npy format)
- **python-dotenv** - Environment configuration

### Optional Tools
- **Pandoc** - Markdown to DOCX conversion for resumes

---

## 📚 Usage

### Web Interface (Recommended)

1. **Start the server:**
   ```bash
   python app.py
   ```

2. **Open your browser:**
   ```
   http://localhost:5001
   ```

3. **Add jobs:**
   - Click "Add Job"
   - Paste any job URL
   - Click "Fetch" (AI extracts details)
   - Review and click "Save & Match"

4. **View job details:**
   - Click any job card
   - See match scores and full description
   - Click "AI Insights" for personalized analysis
   - Click "Cover Letter" to generate one
   - Click "Generate Resume" for a tailored resume

5. **Filter and sort:**
   - Use dropdowns to filter by passing jobs or remote only
   - Sort by score or date added

### CLI Usage

```bash
# Add a job posting
python src/main.py add-job

# Match all jobs against your profile
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

---

## 📁 Project Structure

```
JobHelper/
├── app.py                          # Flask web application
├── job_profile_document.md         # Your career profile (source of truth)
├── requirements.txt                # Python dependencies
├── .env.example                    # Configuration template
├── .env                            # Your configuration (not in git)
├── README.md                       # This file
├── CLAUDE.md                       # Development guide for Claude
├── AI_SETUP.md                     # AI features setup guide
├── src/
│   ├── main.py                     # CLI entry point
│   ├── config.py                   # Configuration management
│   ├── profile_vectorizer.py      # Profile parsing & embedding
│   ├── job_manager.py              # Job storage & retrieval
│   ├── job_matcher.py              # Vector matching & scoring
│   ├── resume_generator.py         # Tailored resume generation
│   └── ai_scraper.py               # OpenAI-powered scraping & insights
├── templates/
│   └── index.html                  # Web interface template
├── static/
│   ├── css/
│   │   └── style.css               # Custom styles
│   └── js/
│       └── app.js                  # Frontend JavaScript
└── data/
    ├── profile_embedding.npy       # Profile vector (generated)
    ├── jobs/                       # Job postings (JSON)
    ├── resumes/                    # Generated resumes
    └── cache/                      # Temporary cache files
```

---

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# Embedding Model
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Scoring Weights (must sum to 1.0)
TECHNICAL_WEIGHT=0.6
CULTURE_WEIGHT=0.4

# Minimum Scores (0.0 to 1.0)
MIN_TECHNICAL_SCORE=0.65
MIN_CULTURE_SCORE=0.50
MIN_OVERALL_SCORE=0.60

# OpenAI API Key (for AI features)
OPENAI_API_KEY=sk-your-key-here
```

---

## 🤖 AI Features Setup

### Getting Started with AI

1. **Get an OpenAI API key:**
   - Visit https://platform.openai.com/signup
   - Create an account (free)
   - Go to https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

2. **Add key to `.env`:**
   ```bash
   OPENAI_API_KEY=sk-your-actual-key-here
   ```

3. **Restart the server:**
   ```bash
   python app.py
   ```

### Cost Information

JobHelper uses GPT-4o-mini (fast and cheap):
- **Job scraping:** ~$0.01-0.02 per job
- **AI insights:** ~$0.02-0.03 per job
- **Cover letter:** ~$0.03-0.05 per job

**Example:** $5 = 100-200 job operations (scraping + insights + cover letters)

For active job searching (20 jobs/week), this costs ~$1-2/week.

See `AI_SETUP.md` for detailed setup instructions and troubleshooting.

---

## 🎯 How It Works

### 1. Profile Analysis
Parses `job_profile_document.md` to extract:
- Technical skills (tiered: Expert, Intermediate, Foundational)
- Work preferences (remote, compensation, location)
- Culture priorities and red flags
- Key accomplishments

### 2. Vector Embeddings
Uses sentence-transformers to create semantic embeddings:
- Profile embedding (created once during init)
- Job posting embeddings (created per job)
- Enables semantic similarity matching beyond keyword matching

### 3. Dual Scoring System

**Technical Score (60%):**
- Cosine similarity between profile and job embeddings
- Captures skill overlap and experience relevance

**Culture Score (40%):**
- Work arrangement match (remote, salary, location)
- Culture priorities (keywords: work-life balance, growth, mission)
- Red flags detection (micromanagement, poor balance, toxic keywords)
- Bonuses for role type alignment

**Overall Score:**
- Weighted combination of technical and culture scores
- Jobs must pass minimum thresholds for all three scores

### 4. AI-Powered Enhancements

**Smart Scraping:**
- Fetches job page HTML
- Sends to OpenAI for extraction
- Returns structured JSON with all job details
- Works across any job site

**AI Insights:**
- Analyzes job description against your profile
- Identifies skill gaps and transferable skills
- Provides recommendations for application
- Highlights key requirements

**Cover Letter Generation:**
- Creates personalized cover letters
- References specific job requirements
- Highlights relevant accomplishments
- Professional and compelling format

---

## 🎨 Features Showcase

### Dashboard
- **Stats Overview:** Total jobs, strong matches, average score
- **Job Cards:** Visual cards with match scores and key info
- **Filters:** All jobs, passing filters, remote only
- **Sorting:** By score (high/low) or date added

### Job Detail View
- **Full Information:** Description, location, salary, URL
- **Match Breakdown:** Technical, culture, and overall scores
- **Color-Coded Progress Bars:** Visual representation of fit
- **Action Buttons:** AI insights, cover letter, resume, delete

### AI Features
- **One-Click Insights:** Skill gaps, recommendations, transferable skills
- **Cover Letter Generator:** Opens in new window with print/copy options
- **Resume Generator:** Downloads tailored resume in chosen format

---

## 🛠️ Development

### Running Tests
```bash
# Test individual modules
python src/profile_vectorizer.py
python src/job_matcher.py
python src/resume_generator.py
python src/ai_scraper.py
```

### Adding a New Job Site
The AI scraper should work automatically for most sites. For sites with heavy JavaScript (Workday, LinkedIn), manual entry is recommended.

### Extending the Matching Algorithm
Edit `src/job_matcher.py`:
- Adjust weights in `_calculate_culture_score()`
- Add new criteria to culture scoring
- Modify technical scoring in `_calculate_technical_score()`

### Customizing Resumes
Edit `src/resume_generator.py`:
- Modify `_detect_role_type()` for role detection
- Update templates in `_generate_markdown_resume()`
- Add new format support

---

## 📝 Tips & Best Practices

### Job Scraping
- **Use direct job posting URLs** (not search results)
- **Greenhouse and Lever work best** (very common in tech)
- **Workday requires manual entry** (JavaScript-heavy, bot detection)
- **LinkedIn is hit-or-miss** (strong anti-scraping measures)

### Matching Accuracy
- **Keep your profile updated** - Review `job_profile_document.md` regularly
- **Adjust thresholds** - Modify `.env` if you're getting too many/few matches
- **Review AI insights** - Use them to identify blind spots in your profile

### Cost Management
- **Be selective** - Only use AI scraping for jobs you're seriously interested in
- **Review matches first** - Check vector scores before requesting AI insights
- **Generate cover letters last** - Only for applications you'll actually submit

---

## 🚧 Known Limitations

- **Workday sites don't auto-scrape** - Require manual entry (JavaScript rendering)
- **LinkedIn has bot detection** - Manual entry recommended
- **No automated job board crawling** - Must add jobs individually
- **Local storage only** - No cloud sync or multi-device support
- **Single user** - No authentication or multi-user support

---

## 🗺️ Roadmap

**Completed:**
- [x] CLI interface
- [x] Web interface
- [x] Vector-based matching
- [x] Dual scoring (technical + culture)
- [x] Resume generation (multiple formats)
- [x] AI-powered job scraping
- [x] AI insights
- [x] Cover letter generation

**Potential Future Enhancements:**
- [ ] Selenium/Playwright for JavaScript-heavy sites
- [ ] Glassdoor integration for company reviews
- [ ] Application tracking (Applied, Interviewing, Rejected, Offer)
- [ ] Email notifications for high-match jobs
- [ ] Automated job board scraping (scheduled)
- [ ] Interview preparation based on job description
- [ ] Analytics dashboard with charts
- [ ] Export to CSV/Excel
- [ ] Cloud deployment (Heroku, Railway)
- [ ] PostgreSQL for better scalability

---

## 🤝 Contributing

This is a personal project, but suggestions are welcome! Feel free to:
- Open issues for bugs or feature requests
- Fork and experiment
- Share improvements

---

## 📄 License

MIT License - Feel free to use and modify for your own job search!

---

## 🙏 Acknowledgments

- **sentence-transformers** - For open-source semantic embeddings
- **OpenAI** - For powerful AI capabilities via GPT-4o-mini
- **Bootstrap** - For beautiful, responsive UI components
- **Flask** - For simple, elegant web framework

---

## 📞 Support

For setup help, see:
- `AI_SETUP.md` - Detailed AI features setup
- `CLAUDE.md` - Development guide and architecture notes

---

**Built with ❤️ for job seekers who value quality over quantity**

*JobHelper helps you find the right opportunities, not just any opportunities.*
