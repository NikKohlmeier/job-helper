"""Job matching using vector similarity and dual scoring."""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple
import re

from config import (
    EMBEDDING_MODEL,
    TECHNICAL_WEIGHT,
    CULTURE_WEIGHT,
    MIN_TECHNICAL_SCORE,
    MIN_CULTURE_SCORE,
    MIN_OVERALL_SCORE,
)
from profile_vectorizer import ProfileVectorizer
from job_manager import Job, JobManager


class JobMatcher:
    """Matches jobs to profile using vector similarity and culture scoring."""

    def __init__(self):
        """Initialize the matcher."""
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.vectorizer = ProfileVectorizer()

        # Load profile
        self.profile_data = self.vectorizer.parse_profile()
        self.profile_embedding = self.vectorizer.create_embedding()

    def match_job(self, job: Job) -> Dict[str, float]:
        """Match a single job against the profile.

        Returns:
            Dictionary with scores:
            - technical_score: 0-1, semantic similarity
            - culture_score: 0-1, culture fit
            - overall_score: weighted combination
            - passed_filters: boolean, meets minimum thresholds
        """
        # Calculate technical fit (vector similarity)
        technical_score = self._calculate_technical_score(job)

        # Calculate culture fit
        culture_score = self._calculate_culture_score(job)

        # Calculate overall weighted score
        overall_score = (
            technical_score * TECHNICAL_WEIGHT +
            culture_score * CULTURE_WEIGHT
        )

        # Check if passes minimum thresholds
        passed_filters = (
            technical_score >= MIN_TECHNICAL_SCORE and
            culture_score >= MIN_CULTURE_SCORE and
            overall_score >= MIN_OVERALL_SCORE
        )

        scores = {
            'technical_score': float(round(technical_score, 3)),
            'culture_score': float(round(culture_score, 3)),
            'overall_score': float(round(overall_score, 3)),
            'passed_filters': bool(passed_filters),
            'technical_weight': float(TECHNICAL_WEIGHT),
            'culture_weight': float(CULTURE_WEIGHT),
        }

        return scores

    def _calculate_technical_score(self, job: Job) -> float:
        """Calculate technical fit using vector similarity."""
        # Create job embedding
        job_text = job.get_embedding_text()
        job_embedding = self.model.encode(job_text, convert_to_numpy=True)

        # Calculate cosine similarity
        similarity = cosine_similarity(
            self.profile_embedding.reshape(1, -1),
            job_embedding.reshape(1, -1)
        )[0][0]

        # Normalize to 0-1 range (cosine similarity is already -1 to 1, but usually 0-1 for similar texts)
        normalized_score = max(0.0, min(1.0, similarity))

        return normalized_score

    def _calculate_culture_score(self, job: Job) -> float:
        """Calculate culture fit based on profile preferences and red flags.

        Analyzes job description, company info, and metadata against:
        - Work arrangement preferences (remote, location, salary)
        - Culture priorities (green flags)
        - Red flags (deal-breakers)

        Returns score 0-1, where 1 is perfect culture fit.
        """
        score = 0.5  # Start neutral
        job_text_lower = job.description.lower()
        job_title_lower = job.title.lower()
        total_checks = 0
        positive_signals = 0
        negative_signals = 0

        # === WORK ARRANGEMENT CHECKS (40% of culture score) ===

        prefs = self.profile_data['work_preferences']

        # Remote preference (high priority)
        total_checks += 1
        if job.remote or any(word in job_text_lower for word in ['remote', 'work from home', 'wfh']):
            positive_signals += 1
            score += 0.15
        elif any(word in job_text_lower for word in ['on-site', 'onsite', 'in-office', 'office required']):
            negative_signals += 1
            score -= 0.10

        # Salary range match
        if 'salary_min' in prefs and job.salary_min:
            total_checks += 1
            if job.salary_min >= prefs['salary_min']:
                positive_signals += 1
                score += 0.15
            elif job.salary_min < prefs['salary_min'] * 0.9:  # More than 10% below target
                negative_signals += 1
                score -= 0.10

        # Location match
        if 'location' in prefs and job.location:
            total_checks += 1
            profile_location = prefs['location'].lower()
            job_location = job.location.lower()

            # Check for preferred locations
            if any(loc in job_location for loc in ['fort wayne', 'grand rapids', 'remote']):
                positive_signals += 1
                score += 0.10

        # === CULTURE PRIORITIES (30% of culture score) ===

        culture_keywords = {
            'people-first': ['work-life balance', 'flexible', 'supportive', 'employee-focused'],
            'growth': ['learning', 'development', 'career growth', 'professional development'],
            'mission-driven': ['mission', 'impact', 'education', 'healthcare', 'nonprofit'],
            'collaborative': ['collaborative', 'team', 'cross-functional', 'together'],
            'autonomy': ['autonomous', 'ownership', 'trust', 'independent'],
        }

        for priority, keywords in culture_keywords.items():
            total_checks += 1
            if any(keyword in job_text_lower for keyword in keywords):
                positive_signals += 1
                score += 0.06  # 5 priorities * 0.06 = 0.30

        # === RED FLAGS (30% of culture score) ===

        red_flag_keywords = {
            'micromanagement': ['micromanage', 'strict oversight', 'constant supervision'],
            'poor_balance': ['fast-paced', 'high-pressure', 'long hours', 'weekends required', 'always on'],
            'toxic': ['aggressive', 'competitive environment', 'high-stress'],
        }

        for flag_type, keywords in red_flag_keywords.items():
            total_checks += 1
            if any(keyword in job_text_lower for keyword in keywords):
                negative_signals += 1
                score -= 0.10  # Strong penalty for red flags

        # === BONUS SIGNALS ===

        # Role type alignment
        preferred_roles = ['wordpress', 'frontend', 'full-stack', 'web developer', 'php']
        if any(role in job_title_lower for role in preferred_roles):
            positive_signals += 1
            score += 0.05

        # Industry preference
        if 'preferred_industries' in prefs:
            industries = prefs['preferred_industries']
            if any(industry in job_text_lower for industry in industries):
                positive_signals += 1
                score += 0.05

        # Ensure score stays in valid range
        score = max(0.0, min(1.0, score))

        return score

    def match_all_jobs(self) -> List[Tuple[Job, Dict]]:
        """Match all saved jobs against profile.

        Returns:
            List of (Job, scores) tuples, sorted by overall_score descending.
        """
        manager = JobManager()
        jobs = manager.get_all_jobs()

        if not jobs:
            print("No jobs found to match.")
            return []

        print(f"\nMatching {len(jobs)} jobs against your profile...\n")

        results = []
        for job in jobs:
            scores = self.match_job(job)

            # Save scores to job
            manager.update_job_scores(job.job_id, scores)

            results.append((job, scores))

        # Sort by overall score (descending)
        results.sort(key=lambda x: x[1]['overall_score'], reverse=True)

        return results

    def print_match_results(self, results: List[Tuple[Job, Dict]], show_all: bool = False):
        """Print formatted match results.

        Args:
            results: List of (Job, scores) tuples
            show_all: If False, only show jobs that pass filters
        """
        if not results:
            print("No results to display.")
            return

        print("\n" + "="*80)
        print("JOB MATCHING RESULTS")
        print("="*80 + "\n")

        # Filter if needed
        if not show_all:
            results = [(job, scores) for job, scores in results if scores['passed_filters']]
            print(f"Showing {len(results)} jobs that pass minimum thresholds\n")
        else:
            print(f"Showing all {len(results)} jobs\n")

        if not results:
            print("No jobs meet the minimum score thresholds.")
            print(f"  - Technical: {MIN_TECHNICAL_SCORE}")
            print(f"  - Culture: {MIN_CULTURE_SCORE}")
            print(f"  - Overall: {MIN_OVERALL_SCORE}")
            print("\nTry lowering thresholds in .env or add more jobs.")
            return

        for i, (job, scores) in enumerate(results, 1):
            status = "✓ PASS" if scores['passed_filters'] else "✗ FAIL"

            print(f"{i}. {job.title} at {job.company}")
            print(f"   ID: {job.job_id}")
            print(f"   Overall: {scores['overall_score']:.1%} {status}")
            print(f"   Technical: {scores['technical_score']:.1%} | Culture: {scores['culture_score']:.1%}")

            if job.location:
                print(f"   Location: {job.location}", end="")
                if job.remote:
                    print(" (Remote)", end="")
                print()

            if job.salary_min:
                if job.salary_max:
                    print(f"   Salary: ${job.salary_min:,} - ${job.salary_max:,}")
                else:
                    print(f"   Salary: ${job.salary_min:,}+")

            if job.url:
                print(f"   URL: {job.url}")

            print()

        print("="*80)


if __name__ == "__main__":
    # Test the matcher
    matcher = JobMatcher()
    results = matcher.match_all_jobs()
    matcher.print_match_results(results, show_all=True)
