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
from src.utils.formatting import print_console_report, print_console_comparison


def fetch_user_dataset(client: GitHubClient, username: str) -> Dict[str, Any]:
    """Helper to fetch profile, repos, languages, and events for a user."""
    profile = client.get_user_profile(username)
    repos = client.get_user_repos(username)
    events = client.get_user_events(username)

    repo_languages: List[Dict[str, int]] = []
    for repo in repos[:30]:
        langs_url = repo.get("languages_url")
        if langs_url:
            repo_langs = client.get_repo_languages(langs_url)
            if repo_langs:
                repo_languages.append(repo_langs)

    repo_stats = GitHubAnalytics.process_repositories(repos)
    language_stats = GitHubAnalytics.process_language_distribution(repo_languages)
    activity_stats = GitHubAnalytics.process_events(events)

    return {
        "profile": profile,
        "repo_stats": repo_stats,
        "language_stats": language_stats,
        "activity_stats": activity_stats
    }


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
        "-c", "--compare",
        type=str,
        help="Second GitHub username to compare in Side-by-Side VS Mode"
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
        help="Custom filepath for output Markdown report"
    )

    args = parser.parse_args()

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

    try:
        client = GitHubClient(token=args.token)

        # Developer VS Mode Branch
        if args.compare:
            user2_name = args.compare.strip()
            print(f"Comparing User 1 ('{username}') vs User 2 ('{user2_name}')...")

            u1_data = fetch_user_dataset(client, username)
            u2_data = fetch_user_dataset(client, user2_name)

            comp_res = GitHubAnalytics.compare_users(u1_data, u2_data)
            print_console_comparison(comp_res)

            output_target = args.output if args.output else os.path.join("reports", f"vs-{username}-vs-{user2_name}.md")
            output_file = MarkdownExporter.generate_comparison_report(
                user1_data=u1_data,
                user2_data=u2_data,
                comp_res=comp_res,
                output_filepath=output_target
            )
            print(f"Successfully generated VS Mode report: {os.path.abspath(output_file)}")
            return

        # Single Profile Mode Branch
        output_target = args.output if args.output else os.path.join("reports", f"{username}-report.md")
        print(f"Fetching GitHub data for user: '{username}'...")

        u1_data = fetch_user_dataset(client, username)

        # Console report display
        print_console_report(
            u1_data["profile"], u1_data["repo_stats"], u1_data["language_stats"], u1_data["activity_stats"]
        )

        # Markdown report generation
        output_file = MarkdownExporter.generate_report(
            profile=u1_data["profile"],
            repo_stats=u1_data["repo_stats"],
            language_stats=u1_data["language_stats"],
            activity_stats=u1_data["activity_stats"],
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
