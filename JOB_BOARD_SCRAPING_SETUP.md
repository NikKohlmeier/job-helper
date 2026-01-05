# Job Board Scraping Setup

## ✅ What's Been Implemented

### 1. Job Board Scraper Module (`src/job_board_scraper.py`)

**Features:**
- ✅ `JobBoardScraper` class
- ✅ Support for multiple job boards
- ✅ Keyword filtering
- ✅ Duplicate removal
- ✅ Rate limiting (delays between requests)

**Supported Boards:**
- ✅ **We Work Remotely** - Simple HTML scraping
- ✅ **RemoteOK** - Simple HTML scraping
- ⚠️ **GitHub Jobs** - API-based (may be deprecated)

### 2. API Endpoint

**Route:** `POST /api/jobs/search-boards`

**Request Body:**
```json
{
  "keywords": ["wordpress", "frontend", "javascript"],
  "boards": ["we_work_remotely", "remoteok"],
  "max_results": 20
}
```

**Response:**
```json
{
  "success": true,
  "jobs": [
    {
      "url": "https://...",
      "title": "Job Title",
      "company": "Company Name",
      "location": "Remote",
      "remote": true,
      "source": "We Work Remotely",
      "description": null
    }
  ],
  "count": 5
}
```

### 3. UI Integration

**New Features:**
- ✅ "Search Job Boards" button in navigation
- ✅ Search modal with:
  - Keyword input (defaults to profile keywords)
  - Board selection checkboxes
  - Max results per board setting
- ✅ Results display with:
  - Job title, company, location
  - Source badge
  - "Add" button for each job
- ✅ One-click add: Click "Add" → Opens Add Job modal → Auto-fetches details

## 🧪 Testing

### Manual Testing Steps

1. **Start the server:**
   ```bash
   python3 app.py
   ```

2. **Open the web interface:**
   - Go to http://localhost:5001
   - Click "Search Job Boards" button

3. **Run a search:**
   - Enter keywords (or use defaults)
   - Select job boards
   - Click "Search Job Boards"
   - Wait for results

4. **Review and add jobs:**
   - Review the list of found jobs
   - Click "Add" on any job you want
   - The Add Job modal opens with URL pre-filled
   - Click "Fetch" to get full details
   - Review and save

### Testing the Scraper Directly

```bash
# Test We Work Remotely
python3 src/job_board_scraper.py

# Or test in Python
python3 -c "
import sys
sys.path.insert(0, 'src')
from job_board_scraper import JobBoardScraper
scraper = JobBoardScraper()
jobs = scraper.search_we_work_remotely(max_results=5)
print(f'Found {len(jobs)} jobs')
"
```

## ⚠️ Known Issues

### 403 Forbidden Errors

Some job boards may block automated requests. This is common and expected.

**Solutions:**
1. **Add delays** - Already implemented (1 second between boards)
2. **Better headers** - Already implemented (realistic browser headers)
3. **Use browser automation** - Would require Playwright/Selenium (future)
4. **Try different boards** - Some are more permissive than others

### Site Structure Changes

Job boards frequently change their HTML structure. If scraping stops working:
1. Inspect the site's HTML structure
2. Update selectors in `job_board_scraper.py`
3. Test with a small `max_results` value first

## 🔧 Configuration

### Keywords

Default keywords come from `config.py`:
```python
SCRAPE_KEYWORDS = ["wordpress", "frontend", "javascript", "php", "web developer"]
```

You can override in the UI or via API.

### Adding New Job Boards

To add a new job board:

1. **Add a new method** in `JobBoardScraper`:
   ```python
   def search_new_board(self, keywords, max_results=20):
       # Implementation
       return jobs
   ```

2. **Add to `search_all_boards()`:**
   ```python
   elif board == 'new_board':
       jobs = self.search_new_board(keywords, max_results=max_results_per_board)
   ```

3. **Add checkbox in UI** (`templates/index.html`)

## 📋 Next Steps (For Scheduling & Emails)

### 1. Scheduled Scraping

**Option A: Cron Job**
```bash
# Add to crontab
0 9 * * * cd /path/to/job-helper && python3 -c "from src.job_board_scraper import JobBoardScraper; ..."
```

**Option B: Python Scheduler**
- Use `schedule` library
- Run in background thread
- Or use `APScheduler` for more features

### 2. Email Notifications

**When to send:**
- New high-match jobs found
- Daily summary of new jobs
- Weekly digest

**Implementation:**
- Use existing SMTP config in `config.py`
- Create `email_notifier.py` module
- Integrate with scraper results

### 3. Deduplication

**Current:** Removes duplicates by URL within a single search

**Future:**
- Track previously seen jobs in database/file
- Only notify about truly new jobs
- Store search history

## 🎯 Usage Workflow

### Current (Manual)
1. Click "Search Job Boards"
2. Review results
3. Click "Add" on interesting jobs
4. Review full details
5. Save and match

### Future (Automated)
1. Scheduled job runs daily
2. Scrapes job boards
3. Filters by keywords
4. Matches against profile
5. Sends email with high-match jobs
6. User reviews and adds jobs

## 📝 Notes

- **Rate Limiting:** Be respectful - 1 second delay between boards
- **Error Handling:** Scrapers fail gracefully, continue with other boards
- **Data:** Jobs are not saved automatically - user must click "Add"
- **Privacy:** No personal data is sent to job boards



