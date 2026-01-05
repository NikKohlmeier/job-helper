# Data Storage & Job Board Scraping Status

## 📦 Data Storage (How Jobs Are Saved)

### Current Implementation

**Storage Method:** File-based JSON storage (NOT browser localStorage)

**Location:** `data/jobs/*.json` files

**How It Works:**
- Each job is saved as a separate JSON file: `{job_id}.json`
- Files are stored in: `/Users/nkohlmeier/Projects/job-helper/data/jobs/`
- Jobs persist across server restarts
- Data is stored on disk, not in browser

**Example Structure:**
```
data/
  ├── jobs/
  │   ├── abc123-def456.json  (Job 1)
  │   ├── xyz789-ghi012.json  (Job 2)
  │   └── ...
  ├── resumes/
  ├── cache/
  └── scraped/
```

**Code Location:** `src/job_manager.py`
- `add_job()` - Saves job to JSON file
- `get_all_jobs()` - Reads all JSON files from directory
- `get_job(job_id)` - Reads specific JSON file
- `delete_job(job_id)` - Deletes JSON file

### Why You Lost Data

**Possible Reasons:**
1. **Directory was cleared** - If `data/jobs/` was deleted or cleared
2. **Different branch** - You might have switched branches
3. **Different machine** - Data is local to the machine
4. **Git ignored** - The `data/jobs/` directory is in `.gitignore`, so it's not tracked in git

**Current Status:** `data/jobs/` directory is empty (no jobs found)

### Data Persistence Going Forward

✅ **Good News:** The current system is persistent:
- Jobs are saved to disk immediately when added
- They persist across server restarts
- They're not dependent on browser storage

⚠️ **Recommendations for Data Safety:**
1. **Backup the `data/` directory** regularly
2. **Add to `.gitignore`** (already done) - prevents accidental commits of personal data
3. **Consider adding a backup script** to copy `data/jobs/` to a backup location
4. **Add application status tracking** - Track which jobs you've applied to (planned feature)

---

## 🔍 Job Board Scraping Status

### Current State: ❌ NOT IMPLEMENTED

**What EXISTS:**
- ✅ **Individual URL Scraping** - You can paste a single job URL and fetch it
- ✅ **AI Scraper** - Extracts job details from a single URL
- ✅ **Basic Scraper** - Fallback for single URLs

**What DOESN'T EXIST:**
- ❌ **Job Board Crawling** - No automated search of job boards
- ❌ **Bulk Job Discovery** - Can't search for multiple jobs at once
- ❌ **Scheduled Scraping** - No automatic daily/weekly searches
- ❌ **Job Board Integration** - No LinkedIn, Indeed, etc. integration

### Current Workflow

**What You Can Do Now:**
1. Find a job posting URL manually (browse job boards yourself)
2. Copy the URL
3. In the web UI, click "Add Job"
4. Paste the URL in the "Paste Job URL" field
5. Click "Fetch" button
6. Review and save

**Limitation:** You must find and paste URLs one at a time

### Planned Features (From Roadmap)

From `README.md` and `CLAUDE.md`:
- [ ] Automated job board scraping (LinkedIn, Indeed)
- [ ] Scheduled scraping (daily/weekly)
- [ ] Glassdoor integration for company reviews
- [ ] Application tracking (Applied, Interviewing, Rejected, Offer)

**Status:** These are planned but not yet implemented

---

## 🎯 What's in the UI Right Now

### Available Features

1. **Add Job Modal:**
   - ✅ URL input field (for single job URLs)
   - ✅ "Fetch" button (scrapes individual URL)
   - ✅ Manual entry form (if URL fetch fails)

2. **Job List:**
   - ✅ Shows all saved jobs
   - ✅ Filter by: All, Passing Filters, Remote Only
   - ✅ Sort by: Score, Date

3. **Job Details:**
   - ✅ View full job description
   - ✅ See match scores
   - ✅ AI Insights button
   - ✅ Generate Resume button
   - ✅ Cover Letter button

### Missing from UI

❌ **Job Board Search:**
- No "Search Job Boards" button
- No "Scrape LinkedIn" option
- No "Search Indeed" feature
- No bulk import functionality

❌ **Application Tracking:**
- No status badges (Applied, Interviewing, etc.)
- No application date tracking
- No follow-up reminders

---

## 🚀 Recommendations

### For Data Persistence

1. **Add Backup Script:**
   ```bash
   # Backup jobs directory
   cp -r data/jobs data/jobs_backup_$(date +%Y%m%d)
   ```

2. **Add Application Status:**
   - Extend Job model to include `application_status` field
   - Add UI to mark jobs as "Applied", "Interviewing", "Rejected", "Offer"
   - Track dates for follow-ups

3. **Add Export Feature:**
   - Export all jobs to CSV/JSON
   - Backup before major changes

### For Job Board Scraping

1. **Implement Job Board Scraper:**
   - Create `job_board_scraper.py` module
   - Support for LinkedIn, Indeed, etc.
   - Search by keywords, location, remote
   - Return list of job URLs

2. **Add to UI:**
   - "Search Job Boards" button in main interface
   - Search form: keywords, location, remote
   - Results list with "Add" buttons
   - Bulk import option

3. **Scheduled Scraping:**
   - Background job scheduler
   - Daily/weekly automatic searches
   - Email notifications for new high-match jobs

---

## 📝 Summary

**Data Storage:**
- ✅ Jobs are saved to disk (JSON files)
- ✅ Data persists across restarts
- ⚠️ Currently empty (data was lost)
- 💡 Need to add backup/export features

**Job Board Scraping:**
- ❌ Not implemented yet
- ✅ Individual URL scraping works
- 📋 Planned for future
- 💡 Would need significant development

**Next Steps:**
1. Start adding jobs again (they'll persist now)
2. Consider implementing job board scraping
3. Add application tracking
4. Set up regular backups



