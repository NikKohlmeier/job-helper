// JobHelper - Frontend JavaScript (Vanilla JS)

let jobs = [];
let currentJobId = null;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    loadJobs();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Add job button
    document.getElementById('save-job-btn').addEventListener('click', saveJob);

    // Fetch URL button
    document.getElementById('fetch-url-btn').addEventListener('click', fetchJobFromUrl);

    // Filter and sort
    document.getElementById('filter-select').addEventListener('change', renderJobs);
    document.getElementById('sort-select').addEventListener('change', renderJobs);

    // Delete job button
    document.getElementById('delete-job-btn').addEventListener('click', deleteJob);

    // Generate resume button
    document.getElementById('generate-resume-btn').addEventListener('click', generateResume);

    // AI insights button
    document.getElementById('show-ai-insights-btn').addEventListener('click', showAIInsights);

    // Cover letter button
    document.getElementById('generate-cover-letter-btn').addEventListener('click', generateCoverLetter);
}

// Load all jobs from API
async function loadJobs() {
    showLoading(true);

    try {
        const response = await fetch('/api/jobs');
        if (!response.ok) throw new Error('Failed to load jobs');

        jobs = await response.json();
        renderJobs();
    } catch (error) {
        console.error('Error loading jobs:', error);
        showError('Failed to load jobs. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Render jobs list
function renderJobs() {
    const jobList = document.getElementById('job-list');
    const emptyState = document.getElementById('empty-state');

    // Apply filters
    let filteredJobs = filterJobs();

    // Apply sorting
    filteredJobs = sortJobs(filteredJobs);

    // Update stats
    updateStats();

    // Show empty state if no jobs
    if (filteredJobs.length === 0) {
        jobList.innerHTML = '';
        emptyState.style.display = 'block';
        return;
    }

    emptyState.style.display = 'none';

    // Render job cards
    jobList.innerHTML = filteredJobs.map(job => createJobCard(job)).join('');

    // Add click listeners to job cards
    document.querySelectorAll('.job-card').forEach(card => {
        card.addEventListener('click', () => {
            const jobId = card.dataset.jobId;
            showJobDetail(jobId);
        });
    });
}

// Filter jobs based on selected filter
function filterJobs() {
    const filter = document.getElementById('filter-select').value;

    if (filter === 'all') {
        return jobs;
    } else if (filter === 'passing') {
        return jobs.filter(job => job.scores && job.scores.passed_filters);
    } else if (filter === 'remote') {
        return jobs.filter(job => job.remote);
    }

    return jobs;
}

// Sort jobs based on selected sort option
function sortJobs(jobsToSort) {
    const sort = document.getElementById('sort-select').value;

    const sorted = [...jobsToSort];

    if (sort === 'score-desc') {
        sorted.sort((a, b) => {
            const scoreA = a.scores ? a.scores.overall_score : 0;
            const scoreB = b.scores ? b.scores.overall_score : 0;
            return scoreB - scoreA;
        });
    } else if (sort === 'score-asc') {
        sorted.sort((a, b) => {
            const scoreA = a.scores ? a.scores.overall_score : 0;
            const scoreB = b.scores ? b.scores.overall_score : 0;
            return scoreA - scoreB;
        });
    } else if (sort === 'date-desc') {
        // Jobs are already in order, newest first
    }

    return sorted;
}

// Update stats overview
function updateStats() {
    const totalJobs = jobs.length;
    const strongMatches = jobs.filter(job => job.scores && job.scores.passed_filters).length;

    const avgScore = jobs.length > 0
        ? jobs.reduce((sum, job) => sum + (job.scores ? job.scores.overall_score : 0), 0) / jobs.length
        : 0;

    document.getElementById('total-jobs').textContent = totalJobs;
    document.getElementById('strong-matches').textContent = strongMatches;
    document.getElementById('avg-score').textContent = Math.round(avgScore * 100) + '%';
}

// Create job card HTML
function createJobCard(job) {
    const overallScore = job.scores ? job.scores.overall_score : 0;
    const technicalScore = job.scores ? job.scores.technical_score : 0;
    const cultureScore = job.scores ? job.scores.culture_score : 0;
    const passed = job.scores ? job.scores.passed_filters : false;

    const badgeClass = passed ? 'bg-success' : 'bg-warning';
    const badgeText = passed ? 'PASSES' : 'Below Threshold';

    const salaryText = job.salary_min && job.salary_max
        ? `$${(job.salary_min / 1000).toFixed(0)}k - $${(job.salary_max / 1000).toFixed(0)}k`
        : job.salary_min
        ? `$${(job.salary_min / 1000).toFixed(0)}k+`
        : 'Not specified';

    return `
        <div class="col-md-6 col-lg-4 mb-3">
            <div class="card job-card h-100" data-job-id="${job.job_id}" style="cursor: pointer;">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h5 class="card-title mb-0">${escapeHtml(job.title)}</h5>
                        <span class="badge ${badgeClass}">${badgeText}</span>
                    </div>
                    <p class="text-muted mb-2">
                        <i class="bi bi-building"></i> ${escapeHtml(job.company)}
                    </p>
                    <p class="text-muted small mb-3">
                        <i class="bi bi-geo-alt"></i> ${escapeHtml(job.location || 'Not specified')}
                        ${job.remote ? '<span class="badge bg-info ms-2">Remote</span>' : ''}
                    </p>
                    <p class="text-muted small mb-3">
                        <i class="bi bi-cash"></i> ${salaryText}
                    </p>

                    <div class="mb-2">
                        <div class="d-flex justify-content-between mb-1">
                            <small>Overall Score</small>
                            <small class="fw-bold">${Math.round(overallScore * 100)}%</small>
                        </div>
                        <div class="progress" style="height: 8px;">
                            <div class="progress-bar ${getScoreColor(overallScore)}"
                                 style="width: ${overallScore * 100}%"></div>
                        </div>
                    </div>

                    <div class="row text-center small mt-3">
                        <div class="col-6">
                            <div class="text-muted">Technical</div>
                            <div class="fw-bold">${Math.round(technicalScore * 100)}%</div>
                        </div>
                        <div class="col-6">
                            <div class="text-muted">Culture</div>
                            <div class="fw-bold">${Math.round(cultureScore * 100)}%</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Show job detail modal
function showJobDetail(jobId) {
    const job = jobs.find(j => j.job_id === jobId);
    if (!job) return;

    currentJobId = jobId;

    // Update modal title
    document.getElementById('detail-job-title').textContent = job.title;
    document.getElementById('detail-job-company').textContent = job.company;

    // Build detail content
    const overallScore = job.scores ? job.scores.overall_score : 0;
    const technicalScore = job.scores ? job.scores.technical_score : 0;
    const cultureScore = job.scores ? job.scores.culture_score : 0;
    const passed = job.scores ? job.scores.passed_filters : false;

    const salaryText = job.salary_min && job.salary_max
        ? `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}`
        : job.salary_min
        ? `$${job.salary_min.toLocaleString()}+`
        : 'Not specified';

    const content = `
        <div class="mb-4">
            <h6>Job Information</h6>
            <p><strong>Location:</strong> ${escapeHtml(job.location || 'Not specified')}
               ${job.remote ? '<span class="badge bg-info ms-2">Remote</span>' : ''}
            </p>
            <p><strong>Salary:</strong> ${salaryText}</p>
            ${job.url ? `<p><strong>URL:</strong> <a href="${escapeHtml(job.url)}" target="_blank">${escapeHtml(job.url)}</a></p>` : ''}
        </div>

        <div class="mb-4">
            <h6>Match Scores</h6>
            <div class="alert ${passed ? 'alert-success' : 'alert-warning'}">
                <strong>${passed ? '✓ PASSES' : '✗ Does Not Meet'} Thresholds</strong>
            </div>

            <div class="mb-3">
                <div class="d-flex justify-content-between mb-1">
                    <span>Overall Score</span>
                    <strong>${Math.round(overallScore * 100)}%</strong>
                </div>
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar ${getScoreColor(overallScore)}"
                         style="width: ${overallScore * 100}%">${Math.round(overallScore * 100)}%</div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span>Technical Fit</span>
                        <strong>${Math.round(technicalScore * 100)}%</strong>
                    </div>
                    <div class="progress">
                        <div class="progress-bar ${getScoreColor(technicalScore)}"
                             style="width: ${technicalScore * 100}%"></div>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="d-flex justify-content-between mb-1">
                        <span>Culture Fit</span>
                        <strong>${Math.round(cultureScore * 100)}%</strong>
                    </div>
                    <div class="progress">
                        <div class="progress-bar ${getScoreColor(cultureScore)}"
                             style="width: ${cultureScore * 100}%"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="mb-4">
            <h6>Job Description</h6>
            <div style="max-height: 400px; overflow-y: auto; white-space: pre-wrap; font-size: 0.9rem;">
${escapeHtml(job.description)}
            </div>
        </div>
    `;

    document.getElementById('job-detail-content').innerHTML = content;

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('jobDetailModal'));
    modal.show();
}

// Fetch job from URL
async function fetchJobFromUrl() {
    const urlInput = document.getElementById('job-url');
    const url = urlInput.value.trim();

    if (!url) {
        showError('Please enter a URL');
        return;
    }

    const btn = document.getElementById('fetch-url-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Fetching...';

    try {
        const response = await fetch('/api/jobs/fetch-url', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        if (!response.ok) throw new Error('Failed to fetch job');

        const job = await response.json();

        // Populate form
        document.getElementById('job-title').value = job.title || '';
        document.getElementById('job-company').value = job.company || '';
        document.getElementById('job-description').value = job.description || '';
        document.getElementById('job-location').value = job.location || '';
        document.getElementById('job-remote').checked = job.remote || false;

        showSuccess('Job details fetched! Review and save.');
    } catch (error) {
        console.error('Error fetching job:', error);
        showError('Could not fetch job from URL. Try manual entry.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-download"></i> Fetch';
    }
}

// Save new job
async function saveJob() {
    const title = document.getElementById('job-title').value.trim();
    const company = document.getElementById('job-company').value.trim();
    const description = document.getElementById('job-description').value.trim();

    if (!title || !company || !description) {
        showError('Please fill in all required fields');
        return;
    }

    const jobData = {
        title,
        company,
        description,
        url: document.getElementById('job-url').value.trim() || null,
        location: document.getElementById('job-location').value.trim() || null,
        remote: document.getElementById('job-remote').checked,
        salary_min: parseInt(document.getElementById('job-salary-min').value) || null,
        salary_max: parseInt(document.getElementById('job-salary-max').value) || null
    };

    const btn = document.getElementById('save-job-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';

    try {
        const response = await fetch('/api/jobs', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jobData)
        });

        if (!response.ok) throw new Error('Failed to save job');

        const result = await response.json();

        showSuccess('Job added and matched successfully!');

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('addJobModal'));
        modal.hide();

        // Reset form
        document.getElementById('add-job-form').reset();
        document.getElementById('job-url').value = '';

        // Reload jobs
        await loadJobs();
    } catch (error) {
        console.error('Error saving job:', error);
        showError('Failed to save job. Please try again.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-check-circle"></i> Save & Match';
    }
}

// Delete job
async function deleteJob() {
    if (!currentJobId) return;

    if (!confirm('Are you sure you want to delete this job?')) {
        return;
    }

    try {
        const response = await fetch(`/api/jobs/${currentJobId}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete job');

        showSuccess('Job deleted successfully!');

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('jobDetailModal'));
        modal.hide();

        currentJobId = null;

        // Reload jobs
        await loadJobs();
    } catch (error) {
        console.error('Error deleting job:', error);
        showError('Failed to delete job. Please try again.');
    }
}

// Generate resume
async function generateResume() {
    if (!currentJobId) return;

    const btn = document.getElementById('generate-resume-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generating...';

    try {
        const response = await fetch(`/api/jobs/${currentJobId}/resume`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ format: 'markdown' })
        });

        if (!response.ok) throw new Error('Failed to generate resume');

        const result = await response.json();

        showSuccess('Resume generated successfully!');

        // Download the resume
        window.open(`/api/jobs/${currentJobId}/resume/download?format=markdown`, '_blank');
    } catch (error) {
        console.error('Error generating resume:', error);
        showError('Failed to generate resume. Please try again.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-file-earmark-text"></i> Generate Resume';
    }
}

// Show AI insights
async function showAIInsights() {
    if (!currentJobId) return;

    const section = document.getElementById('ai-insights-section');
    const content = document.getElementById('ai-insights-content');

    // Show section with loading
    section.style.display = 'block';
    content.innerHTML = `
        <div class="text-center py-3">
            <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <span class="ms-2">Analyzing job fit with AI...</span>
        </div>
    `;

    try {
        const response = await fetch(`/api/jobs/${currentJobId}/ai-insights`);

        if (!response.ok) {
            if (response.status === 503) {
                content.innerHTML = `
                    <div class="alert alert-warning">
                        <strong>OpenAI API Key Required</strong>
                        <p class="mb-0">AI insights require an OpenAI API key. Add your key to the .env file and restart the server.</p>
                    </div>
                `;
                return;
            }
            throw new Error('Failed to get AI insights');
        }

        const insights = await response.json();

        // Render insights
        content.innerHTML = `
            <div class="row">
                <div class="col-md-6 mb-3">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h6 class="card-title">
                                <i class="bi bi-check-circle text-success"></i> Transferable Skills
                            </h6>
                            <ul class="mb-0">
                                ${insights.transferable_skills.map(skill => `<li>${escapeHtml(skill)}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
                <div class="col-md-6 mb-3">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h6 class="card-title">
                                <i class="bi bi-exclamation-circle text-warning"></i> Skill Gaps
                            </h6>
                            <ul class="mb-0">
                                ${insights.skill_gaps.map(skill => `<li>${escapeHtml(skill)}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>

            <div class="mb-3">
                <div class="card bg-light">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="bi bi-star text-primary"></i> Why This Is A Good Fit
                        </h6>
                        <p class="mb-0">${escapeHtml(insights.why_good_fit)}</p>
                    </div>
                </div>
            </div>

            ${insights.concerns ? `
                <div class="mb-3">
                    <div class="card bg-light">
                        <div class="card-body">
                            <h6 class="card-title">
                                <i class="bi bi-flag text-danger"></i> Potential Concerns
                            </h6>
                            <p class="mb-0">${escapeHtml(insights.concerns)}</p>
                        </div>
                    </div>
                </div>
            ` : ''}

            <div class="mb-3">
                <div class="card bg-light">
                    <div class="card-body">
                        <h6 class="card-title">
                            <i class="bi bi-lightbulb text-info"></i> Recommendations
                        </h6>
                        <ul class="mb-0">
                            ${insights.recommendations.map(rec => `<li>${escapeHtml(rec)}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>

            <div class="card bg-light">
                <div class="card-body">
                    <h6 class="card-title">
                        <i class="bi bi-list-check"></i> Key Requirements
                    </h6>
                    <ul class="mb-0">
                        ${insights.key_requirements.map(req => `<li>${escapeHtml(req)}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;

    } catch (error) {
        console.error('Error loading AI insights:', error);
        content.innerHTML = `
            <div class="alert alert-danger">
                Failed to load AI insights. Please try again.
            </div>
        `;
    }
}

// Generate cover letter
async function generateCoverLetter() {
    if (!currentJobId) return;

    const btn = document.getElementById('generate-cover-letter-btn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Generating...';

    try {
        const response = await fetch(`/api/jobs/${currentJobId}/cover-letter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            if (response.status === 503) {
                alert('OpenAI API Key Required\n\nCover letter generation requires an OpenAI API key. Add your key to the .env file and restart the server.');
                return;
            }
            throw new Error('Failed to generate cover letter');
        }

        const result = await response.json();

        // Show cover letter in a modal or alert
        const coverLetterWindow = window.open('', '_blank', 'width=800,height=600');
        coverLetterWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Cover Letter</title>
                <style>
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
                        padding: 40px;
                        max-width: 800px;
                        margin: 0 auto;
                        line-height: 1.6;
                    }
                    h1 {
                        color: #333;
                        border-bottom: 2px solid #0d6efd;
                        padding-bottom: 10px;
                    }
                    .cover-letter {
                        white-space: pre-wrap;
                        font-size: 14px;
                    }
                    .actions {
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #ccc;
                    }
                    button {
                        padding: 10px 20px;
                        background: #0d6efd;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        margin-right: 10px;
                    }
                    button:hover {
                        background: #0b5ed7;
                    }
                </style>
            </head>
            <body>
                <h1>Cover Letter</h1>
                <div class="cover-letter">${escapeHtml(result.cover_letter)}</div>
                <div class="actions">
                    <button onclick="window.print()">Print / Save as PDF</button>
                    <button onclick="navigator.clipboard.writeText(document.querySelector('.cover-letter').textContent)">Copy to Clipboard</button>
                </div>
            </body>
            </html>
        `);

        showSuccess('Cover letter generated! Check the new window.');

    } catch (error) {
        console.error('Error generating cover letter:', error);
        showError('Failed to generate cover letter. Please try again.');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-envelope"></i> Cover Letter';
    }
}

// Utility functions
function showLoading(show) {
    document.getElementById('loading').style.display = show ? 'block' : 'none';
}

function showError(message) {
    alert('Error: ' + message);
}

function showSuccess(message) {
    alert('Success: ' + message);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function getScoreColor(score) {
    if (score >= 0.8) return 'bg-success';
    if (score >= 0.6) return 'bg-info';
    if (score >= 0.4) return 'bg-warning';
    return 'bg-danger';
}
