#!/usr/bin/env python3
"""JobHelper - Main CLI interface."""

import sys
import argparse
from pathlib import Path

from profile_vectorizer import ProfileVectorizer
from job_manager import Job, JobManager, interactive_add_job
from job_matcher import JobMatcher
from resume_generator import ResumeGenerator
from config import PROFILE_PATH, PROFILE_EMBEDDING_PATH


def cmd_init(args):
    """Initialize profile embedding."""
    print("\n=== Initializing JobHelper ===\n")

    # Check if profile exists
    if not PROFILE_PATH.exists():
        print(f"ERROR: Profile not found at {PROFILE_PATH}")
        print("Please create job_profile_document.md in the project root.")
        return 1

    print("Loading and parsing profile...")
    vectorizer = ProfileVectorizer()
    profile = vectorizer.parse_profile()

    print("\n" + vectorizer.get_profile_summary())

    # Create embedding
    print("\n" + "="*50)
    force = args.force if hasattr(args, 'force') else False

    if PROFILE_EMBEDDING_PATH.exists() and not force:
        print("Profile embedding already exists.")
        print("Use --force to recreate it.")
    else:
        embedding = vectorizer.create_embedding(force_recreate=force)
        print(f"✓ Profile embedding created successfully!")
        print(f"  Dimensions: {embedding.shape[0]}")

    print("\n✓ Initialization complete!")
    print("\nNext steps:")
    print("  1. Add jobs: python src/main.py add-job")
    print("  2. Match jobs: python src/main.py match")
    return 0


def cmd_add_job(args):
    """Add a new job posting."""
    job = interactive_add_job()

    if not job:
        print("Job creation cancelled.")
        return 1

    manager = JobManager()
    job_id = manager.add_job(job)

    print(f"\n✓ Job added successfully!")
    print(f"  ID: {job_id}")
    print(f"  Title: {job.title}")
    print(f"  Company: {job.company}")

    # Ask if they want to match immediately
    match_now = input("\nMatch this job against your profile now? (y/n): ").strip().lower()
    if match_now == 'y':
        matcher = JobMatcher()
        scores = matcher.match_job(job)
        manager.update_job_scores(job_id, scores)

        print("\n=== Match Results ===")
        print(f"Technical Score: {scores['technical_score']:.1%}")
        print(f"Culture Score: {scores['culture_score']:.1%}")
        print(f"Overall Score: {scores['overall_score']:.1%}")

        if scores['passed_filters']:
            print("✓ This job PASSES your filter thresholds!")
        else:
            print("✗ This job does not meet minimum thresholds.")

    return 0


def cmd_list_jobs(args):
    """List all saved jobs."""
    manager = JobManager()
    jobs = manager.get_all_jobs()

    if not jobs:
        print("No jobs found.")
        print("\nAdd a job: python src/main.py add-job")
        return 0

    print(f"\n=== Saved Jobs ({len(jobs)}) ===\n")

    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job.title} at {job.company}")
        print(f"   ID: {job.job_id}")

        if job.location:
            print(f"   Location: {job.location}", end="")
            if job.remote:
                print(" (Remote)", end="")
            print()

        if job.scores:
            overall = job.scores.get('overall_score', 0)
            passed = job.scores.get('passed_filters', False)
            status = "✓" if passed else "✗"
            print(f"   Score: {overall:.1%} {status}")

        print()

    return 0


def cmd_match(args):
    """Match all jobs against profile."""
    # Check if profile is initialized
    if not PROFILE_EMBEDDING_PATH.exists():
        print("ERROR: Profile not initialized.")
        print("Run: python src/main.py init")
        return 1

    print("\n=== Matching Jobs ===\n")

    matcher = JobMatcher()
    results = matcher.match_all_jobs()

    if not results:
        print("No jobs to match.")
        print("\nAdd a job: python src/main.py add-job")
        return 0

    show_all = args.all if hasattr(args, 'all') else False
    matcher.print_match_results(results, show_all=show_all)

    return 0


def cmd_show_job(args):
    """Show details for a specific job."""
    manager = JobManager()
    job = manager.get_job(args.job_id)

    if not job:
        print(f"ERROR: Job not found: {args.job_id}")
        return 1

    print("\n" + "="*80)
    print(f"{job.title} at {job.company}")
    print("="*80 + "\n")

    print(f"ID: {job.job_id}")

    if job.location:
        print(f"Location: {job.location}")

    if job.remote:
        print("Remote: Yes")

    if job.salary_min:
        if job.salary_max:
            print(f"Salary: ${job.salary_min:,} - ${job.salary_max:,}")
        else:
            print(f"Salary: ${job.salary_min:,}+")

    if job.url:
        print(f"URL: {job.url}")

    if job.scores:
        print(f"\n--- Scores ---")
        print(f"Technical: {job.scores['technical_score']:.1%}")
        print(f"Culture: {job.scores['culture_score']:.1%}")
        print(f"Overall: {job.scores['overall_score']:.1%}")

        if job.scores['passed_filters']:
            print("Status: ✓ PASSES filters")
        else:
            print("Status: ✗ Does not meet thresholds")

    print(f"\n--- Description ---")
    print(job.description[:500])
    if len(job.description) > 500:
        print(f"... ({len(job.description) - 500} more characters)")

    print("\n" + "="*80)

    return 0


def cmd_generate_resume(args):
    """Generate a custom resume for a specific job."""
    manager = JobManager()
    job = manager.get_job(args.job_id)

    if not job:
        print(f"ERROR: Job not found: {args.job_id}")
        return 1

    print(f"\n=== Generating Resume ===")
    print(f"Job: {job.title} at {job.company}\n")

    format_choice = args.format if hasattr(args, 'format') else 'markdown'

    generator = ResumeGenerator()
    filepath = generator.save_resume(job, format=format_choice)

    print(f"\n✓ Resume generated successfully!")
    print(f"  Location: {filepath}")
    print(f"  Format: {format_choice}")

    # Show preview
    show_preview = input("\nShow preview? (y/n): ").strip().lower()
    if show_preview == 'y':
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            preview_lines = lines[:30]
            print("\n--- Preview (first 30 lines) ---")
            print('\n'.join(preview_lines))
            if len(lines) > 30:
                print(f"... ({len(lines) - 30} more lines)")

    return 0


def cmd_delete_job(args):
    """Delete a job posting."""
    manager = JobManager()
    job = manager.get_job(args.job_id)

    if not job:
        print(f"ERROR: Job not found: {args.job_id}")
        return 1

    print(f"Delete: {job.title} at {job.company}")
    confirm = input("Are you sure? (yes/no): ").strip().lower()

    if confirm == 'yes':
        manager.delete_job(args.job_id)
        print("✓ Job deleted.")
        return 0
    else:
        print("Cancelled.")
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="JobHelper - Personalized job matching and resume generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python src/main.py init                    # Initialize profile
  python src/main.py add-job                 # Add a new job
  python src/main.py match                   # Match all jobs
  python src/main.py match --all             # Show all jobs, even low scores
  python src/main.py list                    # List all jobs
  python src/main.py show <job-id>           # Show job details
  python src/main.py generate-resume <id>    # Generate resume
  python src/main.py delete <job-id>         # Delete a job
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # init command
    parser_init = subparsers.add_parser('init', help='Initialize profile embedding')
    parser_init.add_argument('--force', action='store_true', help='Force recreate embedding')
    parser_init.set_defaults(func=cmd_init)

    # add-job command
    parser_add = subparsers.add_parser('add-job', help='Add a new job posting')
    parser_add.set_defaults(func=cmd_add_job)

    # list command
    parser_list = subparsers.add_parser('list', help='List all saved jobs')
    parser_list.set_defaults(func=cmd_list_jobs)

    # match command
    parser_match = subparsers.add_parser('match', help='Match jobs against profile')
    parser_match.add_argument('--all', action='store_true', help='Show all jobs, not just passing')
    parser_match.set_defaults(func=cmd_match)

    # show command
    parser_show = subparsers.add_parser('show', help='Show job details')
    parser_show.add_argument('job_id', help='Job ID to show')
    parser_show.set_defaults(func=cmd_show_job)

    # generate-resume command
    parser_resume = subparsers.add_parser('generate-resume', help='Generate custom resume')
    parser_resume.add_argument('job_id', help='Job ID to generate resume for')
    parser_resume.add_argument('--format', choices=['markdown', 'txt', 'html'], default='markdown',
                              help='Output format (default: markdown)')
    parser_resume.set_defaults(func=cmd_generate_resume)

    # delete command
    parser_delete = subparsers.add_parser('delete', help='Delete a job posting')
    parser_delete.add_argument('job_id', help='Job ID to delete')
    parser_delete.set_defaults(func=cmd_delete_job)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Run command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
