"""Custom resume generator based on profile and job match."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from jinja2 import Template

from config import RESUMES_DIR
from profile_vectorizer import ProfileVectorizer
from job_manager import Job


class ResumeGenerator:
    """Generates tailored resumes for specific job matches."""

    def __init__(self):
        """Initialize the resume generator."""
        self.vectorizer = ProfileVectorizer()
        self.profile_data = self.vectorizer.parse_profile()

    def generate_resume(
        self,
        job: Job,
        format: str = "markdown"
    ) -> str:
        """Generate a custom resume tailored for a specific job.

        Args:
            job: The job posting to tailor the resume for
            format: Output format ("markdown", "txt", or "html")

        Returns:
            Formatted resume as string
        """
        # Determine role type from job title
        role_type = self._detect_role_type(job.title)

        # Get relevant accomplishments and skills
        accomplishments = self._select_accomplishments(job, role_type)
        skills = self._select_skills(job)

        # Build resume data
        resume_data = {
            'name': 'Nik Kohlmeier',
            'email': 'kohlmeier.nik@gmail.com',
            'phone': '260-580-1490',
            'location': 'Fort Wayne, Indiana',
            'linkedin': 'https://www.linkedin.com/in/nik-kohlmeier/',
            'github': 'https://github.com/NikKohlmeier',
            'target_role': job.title,
            'target_company': job.company,
            'summary': self._generate_summary(job, role_type),
            'skills': skills,
            'accomplishments': accomplishments,
            'experience': self._format_experience(role_type),
            'education': self._format_education(),
            'generated_date': datetime.now().strftime("%Y-%m-%d"),
        }

        # Generate resume based on format
        if format == "markdown":
            resume = self._generate_markdown(resume_data)
        elif format == "txt":
            resume = self._generate_text(resume_data)
        elif format == "html":
            resume = self._generate_html(resume_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

        return resume

    def _detect_role_type(self, job_title: str) -> str:
        """Detect role type from job title."""
        title_lower = job_title.lower()

        if 'wordpress' in title_lower:
            return 'wordpress'
        elif 'frontend' in title_lower or 'front-end' in title_lower or 'front end' in title_lower:
            return 'frontend'
        elif 'full-stack' in title_lower or 'full stack' in title_lower or 'fullstack' in title_lower:
            return 'full-stack'
        elif any(word in title_lower for word in ['agency', 'client', 'consulting']):
            return 'agency'
        elif any(word in title_lower for word in ['education', 'nonprofit', 'healthcare', 'mission']):
            return 'mission-driven'
        else:
            return 'full-stack'  # Default

    def _select_accomplishments(self, job: Job, role_type: str) -> List[str]:
        """Select and order accomplishments based on role type."""
        all_accomplishments = self.profile_data['accomplishments']

        # Get role-specific anchors
        anchors = self.profile_data.get('resume_anchors', {})
        role_anchors = anchors.get(role_type, [])

        # Priority order based on role
        priority_keywords = {
            'wordpress': ['WordPress', 'plugin', 'custom development', 'uptime'],
            'frontend': ['accessibility', 'user experience', 'design', 'JavaScript'],
            'full-stack': ['cross-functional', 'database', 'backend', 'frontend'],
            'agency': ['client', 'requirements', 'multiple projects', 'communication'],
            'mission-driven': ['collaboration', 'impact', 'reliability', 'problem-solving'],
        }

        keywords = priority_keywords.get(role_type, [])

        # Score accomplishments by relevance
        scored = []
        for accomp in all_accomplishments:
            score = 0

            # Check for keyword matches
            accomp_lower = accomp.lower()
            for keyword in keywords:
                if keyword.lower() in accomp_lower:
                    score += 2

            # Check for matches in job description
            job_desc_lower = job.description.lower()
            words = accomp_lower.split()
            for word in words:
                if len(word) > 4 and word in job_desc_lower:
                    score += 1

            scored.append((score, accomp))

        # Sort by score and take top 5
        scored.sort(reverse=True, key=lambda x: x[0])
        selected = [accomp for score, accomp in scored[:5]]

        return selected

    def _select_skills(self, job: Job) -> Dict[str, List[str]]:
        """Select relevant skills based on job requirements."""
        all_skills = self.profile_data['technical_skills']
        job_desc_lower = job.description.lower() + " " + job.title.lower()

        # Filter skills that appear in job description
        relevant_skills = {
            'expert': [],
            'intermediate': [],
            'foundational': [],
        }

        for tier, skills_list in all_skills.items():
            for skill in skills_list:
                skill_lower = skill.lower()
                # Extract the main technology name (before parentheses or details)
                main_skill = skill.split('(')[0].strip()
                main_skill_lower = main_skill.lower()

                # Check if skill is mentioned in job
                if main_skill_lower in job_desc_lower:
                    relevant_skills[tier].append(skill)
                # Also include if it's a core skill
                elif main_skill_lower in ['wordpress', 'javascript', 'php', 'html/css', 'sql', 'css']:
                    relevant_skills[tier].append(skill)

        return relevant_skills

    def _generate_summary(self, job: Job, role_type: str) -> str:
        """Generate a tailored summary for the job."""
        summaries = {
            'wordpress': (
                "WordPress specialist with 8+ years of experience building custom themes, plugins, "
                "and optimizing site performance. Proven track record of cost optimization through "
                "custom development and maintaining 99%+ uptime for production sites."
            ),
            'frontend': (
                "Frontend developer with 8+ years of experience and strong design background (BFA). "
                "Expertise in vanilla JavaScript, HTML/CSS, and accessibility. Combines technical "
                "skill with user-centered design thinking to create exceptional web experiences."
            ),
            'full-stack': (
                "Full-stack web developer with 8+ years of experience spanning WordPress, JavaScript, "
                "PHP, and SQL. Skilled at translating business requirements into technical solutions, "
                "with proven ability to deliver cost-effective, maintainable applications."
            ),
            'agency': (
                "Web developer with 8+ years of client-focused experience managing multiple projects "
                "simultaneously. Strong communicator who excels at translating business requirements "
                "into technical solutions while collaborating across teams."
            ),
            'mission-driven': (
                "Web developer with 8+ years of experience and 6+ years of commitment to current "
                "organization. Passionate about using technology to support mission-driven work in "
                "education and healthcare. Proven collaborator with cross-functional teams."
            ),
        }

        return summaries.get(role_type, summaries['full-stack'])

    def _format_experience(self, role_type: str) -> str:
        """Format work experience section."""
        # This would be expanded with actual experience details
        # For now, returning a placeholder
        experience = """
**Marketing/Web Developer**
*Current Organization | Fort Wayne, IN | 6+ years*

- Led all WordPress development, maintenance, and custom plugin creation for organization
- Designed and implemented cost-saving custom plugin as alternative to Google Maps API
- Improved website accessibility standards and compliance across multiple properties
- Collaborated with marketing team to translate business requirements into technical solutions
- Maintained 99%+ uptime on WordPress sites serving thousands of users
"""
        return experience.strip()

    def _format_education(self) -> str:
        """Format education section."""
        education = """
**Bachelor of Fine Arts (BFA)**
*University Name*

**Certifications:**
- LevelAccess Design and Web Accessibility Certification
"""
        return education.strip()

    def _generate_markdown(self, data: Dict) -> str:
        """Generate resume in Markdown format."""
        template = """# {{name}}

{{location}} | {{email}} | {{phone}}
[LinkedIn]({{linkedin}}) | [GitHub]({{github}})

---

## Professional Summary

{{summary}}

---

## Technical Skills

{% if skills.expert %}
**Expert Level:**
{% for skill in skills.expert %}
- {{skill}}
{% endfor %}
{% endif %}

{% if skills.intermediate %}
**Intermediate Level:**
{% for skill in skills.intermediate %}
- {{skill}}
{% endfor %}
{% endif %}

{% if skills.foundational %}
**Foundational:**
{% for skill in skills.foundational %}
- {{skill}}
{% endfor %}
{% endif %}

---

## Key Accomplishments

{% for accomp in accomplishments %}
- {{accomp}}
{% endfor %}

---

## Professional Experience

{{experience}}

---

## Education

{{education}}

---

*Resume generated {{generated_date}} for {{target_role}} position at {{target_company}}*
"""
        t = Template(template)
        return t.render(**data)

    def _generate_text(self, data: Dict) -> str:
        """Generate resume in plain text format."""
        # Similar to markdown but without formatting
        lines = []
        lines.append(f"{data['name']}")
        lines.append(f"{data['location']} | {data['email']} | {data['phone']}")
        lines.append(f"LinkedIn: {data['linkedin']} | GitHub: {data['github']}")
        lines.append("")
        lines.append("="*80)
        lines.append("PROFESSIONAL SUMMARY")
        lines.append("="*80)
        lines.append(data['summary'])
        lines.append("")
        lines.append("="*80)
        lines.append("TECHNICAL SKILLS")
        lines.append("="*80)

        if data['skills']['expert']:
            lines.append("Expert Level:")
            for skill in data['skills']['expert']:
                lines.append(f"  - {skill}")

        if data['skills']['intermediate']:
            lines.append("Intermediate Level:")
            for skill in data['skills']['intermediate']:
                lines.append(f"  - {skill}")

        lines.append("")
        lines.append("="*80)
        lines.append("KEY ACCOMPLISHMENTS")
        lines.append("="*80)
        for accomp in data['accomplishments']:
            lines.append(f"- {accomp}")

        lines.append("")
        lines.append("="*80)
        lines.append("PROFESSIONAL EXPERIENCE")
        lines.append("="*80)
        lines.append(data['experience'])

        lines.append("")
        lines.append("="*80)
        lines.append("EDUCATION")
        lines.append("="*80)
        lines.append(data['education'])

        lines.append("")
        lines.append(f"Resume generated {data['generated_date']} for {data['target_role']} at {data['target_company']}")

        return "\n".join(lines)

    def _generate_html(self, data: Dict) -> str:
        """Generate resume in HTML format."""
        template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{name}} - Resume</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; line-height: 1.6; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 5px; margin-top: 30px; }
        .contact { color: #7f8c8d; margin-bottom: 20px; }
        .summary { background: #ecf0f1; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }
        ul { list-style-position: inside; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #bdc3c7; color: #95a5a6; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>{{name}}</h1>
    <div class="contact">
        {{location}} | {{email}} | {{phone}}<br>
        <a href="{{linkedin}}">LinkedIn</a> | <a href="{{github}}">GitHub</a>
    </div>

    <h2>Professional Summary</h2>
    <div class="summary">{{summary}}</div>

    <h2>Technical Skills</h2>
    {% if skills.expert %}
    <strong>Expert Level:</strong>
    <ul>
    {% for skill in skills.expert %}
        <li>{{skill}}</li>
    {% endfor %}
    </ul>
    {% endif %}

    {% if skills.intermediate %}
    <strong>Intermediate Level:</strong>
    <ul>
    {% for skill in skills.intermediate %}
        <li>{{skill}}</li>
    {% endfor %}
    </ul>
    {% endif %}

    <h2>Key Accomplishments</h2>
    <ul>
    {% for accomp in accomplishments %}
        <li>{{accomp}}</li>
    {% endfor %}
    </ul>

    <h2>Professional Experience</h2>
    <div style="white-space: pre-line;">{{experience}}</div>

    <h2>Education</h2>
    <div style="white-space: pre-line;">{{education}}</div>

    <div class="footer">
        Resume generated {{generated_date}} for {{target_role}} position at {{target_company}}
    </div>
</body>
</html>"""
        t = Template(template)
        return t.render(**data)

    def save_resume(
        self,
        job: Job,
        format: str = "markdown",
        filename: Optional[str] = None
    ) -> Path:
        """Generate and save resume to file."""
        resume = self.generate_resume(job, format)

        # Generate filename if not provided
        if not filename:
            safe_company = "".join(c for c in job.company if c.isalnum() or c in (' ', '-', '_'))
            safe_company = safe_company.replace(' ', '_')
            timestamp = datetime.now().strftime("%Y%m%d")
            ext = {'markdown': 'md', 'txt': 'txt', 'html': 'html'}[format]
            filename = f"resume_{safe_company}_{timestamp}.{ext}"

        filepath = RESUMES_DIR / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(resume)

        print(f"Resume saved to: {filepath}")
        return filepath


if __name__ == "__main__":
    # Test resume generation
    from job_manager import Job

    # Create a sample job
    test_job = Job(
        title="WordPress Developer",
        company="Test Company",
        description="Looking for an experienced WordPress developer...",
        remote=True,
        salary_min=75000,
        salary_max=90000,
    )

    generator = ResumeGenerator()
    resume = generator.generate_resume(test_job, format="markdown")
    print(resume)
