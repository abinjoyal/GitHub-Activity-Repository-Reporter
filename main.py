"""
Main CLI entry point for the GitHub Activity & Repo Reporter application.
"""

import sys
import os
import argparse
from typing import List, Dict, Any

from dotenv import load_dotenv

# Ensure `src` module is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.github_client import GitHubClient, GitHubAPIError
from src.analytics.statistics import GitHubAnalytics
from src.exporters.markdown_exporter import MarkdownExporter
from src.utils.formatting import print_console_report


def main() -> None:
    # Load environment variables from .env if present
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="GitHub Activity & Repository Reporter - Command Line Utility"
    )
    parser.add_argument(
        "-u", "--username",
        type=str,
        help="Target GitHub username (e.g., abinjoyal)"
    )
    parser.add_argument(
        "-t", "--token",
        type=str,
        help="Optional GitHub Personal Access Token to avoid rate limiting"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Custom filepath for output Markdown report (default: reports/<username>-report.md)"
    )

    args = parser.parse_args()

    # Interactive prompt if username argument is missing
    username = args.username
    if not username:
        try:
            username = input("Enter GitHub username: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)

    if not username:
        print("Error: GitHub username cannot be empty.", file=sys.stderr)
        sys.exit(1)

    # Determine dynamic output report path if not explicitly provided
    output_target = args.output if args.output else os.path.join("reports", f"{username}-report.md")

    print(f"Fetching GitHub data for user: '{username}'...")

    try:
        client = GitHubClient(token=args.token)
        profile = client.get_user_profile(username)
        repos = client.get_user_repos(username)
        events = client.get_user_events(username)

        # Collect language byte counts for up to 30 most recently updated repos to preserve API quota
        print(f"Analyzing repository language statistics ({len(repos)} total repos)...")
        repo_languages: List[Dict[str, int]] = []
        for repo in repos[:30]:
            langs_url = repo.get("languages_url")
            if langs_url:
                repo_langs = client.get_repo_languages(langs_url)
                if repo_langs:
                    repo_languages.append(repo_langs)

        # Process analytics
        repo_stats = GitHubAnalytics.process_repositories(repos)
        language_stats = GitHubAnalytics.process_language_distribution(repo_languages)
        activity_stats = GitHubAnalytics.process_events(events)

        # Console report display
        print_console_report(profile, repo_stats, language_stats, activity_stats)

        # Markdown report generation
        output_file = MarkdownExporter.generate_report(
            profile=profile,
            repo_stats=repo_stats,
            language_stats=language_stats,
            activity_stats=activity_stats,
            output_filepath=output_target
        )

        print(f"Successfully generated Markdown report: {os.path.abspath(output_file)}")

    except GitHubAPIError as err:
        print(f"\n[GitHub API Error]: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"\n[Unexpected Error]: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
