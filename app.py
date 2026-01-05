#!/usr/bin/env python3
"""JobHelper - Flask Web Application."""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from job_manager import Job, JobManager
from job_matcher import JobMatcher
from resume_generator import ResumeGenerator
from profile_vectorizer import ProfileVectorizer
from ai_scraper import AIJobScraper
from job_board_scraper import JobBoardScraper
from config import PROFILE_EMBEDDING_PATH, OPENAI_API_KEY, SCRAPE_KEYWORDS

app = Flask(__name__)
CORS(app)

# Initialize managers
job_manager = JobManager()
ai_scraper = AIJobScraper()
job_board_scraper = JobBoardScraper()


@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')


@app.route('/api/status')
def status():
    """Check if profile is initialized."""
    return jsonify({
        'initialized': PROFILE_EMBEDDING_PATH.exists(),
        'profile_path': str(PROFILE_EMBEDDING_PATH)
    })


@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Get all jobs."""
    try:
        jobs = job_manager.get_all_jobs()
        return jsonify([job.to_dict() for job in jobs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    """Get a specific job."""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        return jsonify(job.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs', methods=['POST'])
def add_job():
    """Add a new job."""
    try:
        data = request.json

        # Create job object
        job = Job(
            title=data.get('title'),
            company=data.get('company'),
            description=data.get('description'),
            url=data.get('url'),
            location=data.get('location'),
            remote=data.get('remote', False),
            salary_min=data.get('salary_min'),
            salary_max=data.get('salary_max')
        )

        # Add to database
        job_id = job_manager.add_job(job)

        # Match the job
        matcher = JobMatcher()
        scores = matcher.match_job(job)
        job_manager.update_job_scores(job_id, scores)

        # Get updated job
        job = job_manager.get_job(job_id)

        return jsonify({
            'success': True,
            'job': job.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    """Delete a job."""
    try:
        success = job_manager.delete_job(job_id)
        if not success:
            return jsonify({'error': 'Job not found'}), 404
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/<job_id>/match', methods=['POST'])
def match_job(job_id):
    """Re-match a specific job."""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        matcher = JobMatcher()
        scores = matcher.match_job(job)
        job_manager.update_job_scores(job_id, scores)

        return jsonify(scores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/<job_id>/resume', methods=['POST'])
def generate_resume(job_id):
    """Generate a resume for a specific job."""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        format_type = request.json.get('format', 'markdown')

        generator = ResumeGenerator()
        filepath = generator.save_resume(job, format=format_type)

        return jsonify({
            'success': True,
            'filepath': str(filepath),
            'format': format_type
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/<job_id>/resume/download', methods=['GET'])
def download_resume(job_id):
    """Download the resume file."""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        format_type = request.args.get('format', 'markdown')

        generator = ResumeGenerator()
        filepath = generator.save_resume(job, format=format_type)

        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/fetch-url', methods=['POST'])
def fetch_job_url():
    """Fetch job details from URL using AI."""
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Try AI scraper first
        job_data = ai_scraper.fetch_job_from_url(url)

        # Fallback to basic scraper if AI fails or not configured
        if not job_data:
            print("AI scraper failed, falling back to basic scraper...")
            job = job_manager.fetch_from_url(url)
            if not job:
                return jsonify({'error': 'Could not fetch job from URL'}), 400
            job_data = job.to_dict()

        return jsonify(job_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/<job_id>/ai-insights', methods=['GET'])
def get_ai_insights(job_id):
    """Get AI-powered insights for a specific job."""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        # Get profile summary
        vectorizer = ProfileVectorizer()
        profile = vectorizer.parse_profile()

        # Create profile summary for AI
        profile_summary = f"""
Skills:
- Expert: {', '.join(profile.get('skills', {}).get('expert', []))}
- Intermediate: {', '.join(profile.get('skills', {}).get('intermediate', []))}

Work Preferences:
- Remote: {profile.get('work_preferences', {}).get('remote', 'high')} preference
- Salary Range: ${profile.get('work_preferences', {}).get('salary_min', 70000)}-${profile.get('work_preferences', {}).get('salary_max', 90000)}

Key Accomplishments:
{chr(10).join('- ' + acc for acc in profile.get('accomplishments', [])[:5])}
        """

        # Get AI insights
        insights = ai_scraper.analyze_job_fit(job.description, profile_summary)

        if not insights:
            return jsonify({'error': 'AI insights not available. Check OpenAI API key.'}), 503

        return jsonify(insights)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/<job_id>/cover-letter', methods=['POST'])
def generate_cover_letter(job_id):
    """Generate a cover letter for a specific job."""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404

        # Get profile summary
        vectorizer = ProfileVectorizer()
        profile = vectorizer.parse_profile()

        profile_summary = f"""
Name: Nik Kohlmeier
Location: Fort Wayne, Indiana

Skills:
- Expert: {', '.join(profile.get('skills', {}).get('expert', []))}
- Intermediate: {', '.join(profile.get('skills', {}).get('intermediate', []))}

Experience:
- 8+ years WordPress development
- Marketing/Web Developer role for 6+ years

Key Accomplishments:
{chr(10).join('- ' + acc for acc in profile.get('accomplishments', [])[:5])}

Work Preferences:
- Remote-first (80%+ preference)
- Mission-driven organizations (education, healthcare, social good)
- Salary Range: $70k-$90k
        """

        # Generate cover letter
        cover_letter = ai_scraper.generate_cover_letter(
            job.description,
            profile_summary,
            job.company,
            job.title
        )

        if not cover_letter:
            return jsonify({'error': 'AI cover letter generation not available. Check OpenAI API key.'}), 503

        return jsonify({'cover_letter': cover_letter})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/jobs/search-boards', methods=['POST'])
def search_job_boards():
    """Search job boards for matching jobs."""
    try:
        data = request.json or {}
        keywords = data.get('keywords', SCRAPE_KEYWORDS)
        boards = data.get('boards', ['we_work_remotely', 'remoteok'])
        max_results = data.get('max_results', 20)
        
        # Search job boards
        jobs = job_board_scraper.search_all_boards(
            keywords=keywords,
            boards=boards,
            max_results_per_board=max_results
        )
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'count': len(jobs)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 JobHelper Web Interface Starting...")
    print("="*60)

    if not PROFILE_EMBEDDING_PATH.exists():
        print("\n⚠️  WARNING: Profile not initialized!")
        print("   Run: python src/main.py init")
        print()

    print("\n📱 Open your browser to: http://localhost:5001")
    print("\n   Press Ctrl+C to stop the server")
    print("="*60 + "\n")

    app.run(debug=True, port=5001)
