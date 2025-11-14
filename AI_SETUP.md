# AI Features Setup Guide

JobHelper now includes powerful AI features powered by OpenAI! Here's how to set them up.

## Features

### 🤖 Smart Job Scraping
- Paste ANY job URL (LinkedIn, Indeed, Greenhouse, company sites)
- AI extracts all details automatically
- Works across all job boards without site-specific code

### 💡 AI Job Insights
- Analyzes how well you fit the role
- Identifies skill gaps and transferable skills
- Provides personalized recommendations
- Highlights key requirements

### ✉️ AI Cover Letter Generator
- Creates personalized cover letters
- References specific job requirements
- Highlights relevant accomplishments
- Professional and compelling

## Setup Instructions

### 1. Get an OpenAI API Key

1. Go to https://platform.openai.com/signup
2. Create an account (or sign in)
3. Navigate to https://platform.openai.com/api-keys
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)

**Cost:** Very affordable!
- Uses GPT-4o-mini model
- ~$0.01-0.02 per job posting
- ~$0.03-0.05 per cover letter
- $5 credit lasts for 100-200 jobs

### 2. Add Key to Your Environment

Edit your `.env` file:

```bash
# Open .env file
nano .env
# or
open .env
```

Find this line:
```
# OPENAI_API_KEY=your_key_here
```

Uncomment and replace with your actual key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

Save the file.

### 3. Restart the Server

Stop the server (Ctrl+C) and restart:

```bash
./venv/bin/python app.py
```

That's it! 🎉

## How to Use

### Smart Job Scraping

1. Click "Add Job"
2. Paste any job URL
3. Click "Fetch"
4. AI extracts all details instantly!

Works with:
- LinkedIn Jobs
- Indeed
- Greenhouse
- Lever
- Company career pages
- Any job posting URL

### AI Job Insights

1. Open any job card
2. Click "AI Insights" button
3. Get instant analysis:
   - Which of your skills apply
   - What skills you're missing
   - Why this is a good (or bad) fit
   - Recommendations for your application

### Cover Letter Generation

1. Open any job card
2. Click "Cover Letter" button
3. Get a personalized cover letter instantly
4. Print/save as PDF or copy to clipboard

## Troubleshooting

**"OpenAI API Key Required" message:**
- Make sure you added the key to `.env`
- Key should start with `sk-`
- No quotes around the key
- Restart the server after adding

**"Rate limit exceeded":**
- You've hit OpenAI's free tier limit
- Add payment method to your OpenAI account
- Very affordable: $5 lasts months for job searching

**AI features not working:**
- Check your OpenAI account has credits
- Verify key is valid at https://platform.openai.com/api-keys
- Check terminal for error messages

## Without AI Key

The app still works great without an OpenAI key:
- ✅ Job matching and scoring
- ✅ Resume generation
- ✅ Job management
- ✅ Basic URL scraping (hit or miss)
- ❌ Smart AI scraping
- ❌ AI insights
- ❌ Cover letter generation

## Privacy & Data

- All AI processing happens through OpenAI's API
- Your profile and job descriptions are sent to OpenAI
- OpenAI's data policy: https://openai.com/policies/privacy-policy
- Data is not used to train models (per OpenAI's API policy)
- Your data stays private and is not shared

## Tips for Best Results

**Job Scraping:**
- Use direct job posting URLs (not search results)
- LinkedIn "Easy Apply" URLs work best
- Company career page URLs usually work well

**AI Insights:**
- More detailed job descriptions = better insights
- Update your profile regularly for better analysis

**Cover Letters:**
- Review and personalize before sending
- AI gives you a strong starting point
- Add specific details about the company

## Cost Management

**To minimize costs:**
- Only use AI scraping for jobs you're seriously interested in
- Review jobs in the system before requesting insights
- Generate cover letters only for applications you'll submit

**Average Usage:**
- Actively job searching (20 jobs/week): ~$1-2/week
- Casual browsing (5 jobs/week): ~$0.25-0.50/week
- Heavy usage (50 jobs/week): ~$3-5/week

## Need Help?

If you run into issues:
1. Check the terminal for error messages
2. Review this guide
3. Check your OpenAI account dashboard
4. Verify your .env file has the correct key

Enjoy the AI-powered job search! 🚀
