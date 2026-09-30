"""
Terminal Formatting Module.
Renders clean, structured terminal summaries for the CLI output.
"""

from typing import Any, Dict, List, Tuple


def print_console_report(
    profile: Dict[str, Any],
    repo_stats: Dict[str, Any],
    language_stats: List[Tuple[str, float, int]],
    activity_stats: Dict[str, int]
) -> None:
    """Print structured report to stdout."""
    username = profile.get("login", "Unknown")
    name = profile.get("name") or username

    print("\n" + "=" * 60)
    print(f" GITHUB REPORT: {name} (@{username})")
    print("=" * 60)
    print(f" Profile URL  : {profile.get('html_url')}")
    print(f" Bio          : {profile.get('bio') or 'N/A'}")
    print(f" Location     : {profile.get('location') or 'N/A'}")
    print(f" Company      : {profile.get('company') or 'N/A'}")
    print("-" * 60)
    print(" REPOSITORY OVERVIEW")
    print("-" * 60)
    print(f" Repositories : {repo_stats.get('total_repositories', 0)}")
    print(f" Total Stars  : {repo_stats.get('total_stars', 0)}")
    print(f" Total Forks  : {repo_stats.get('total_forks', 0)}")
    print(f" Open Issues  : {repo_stats.get('total_open_issues', 0)}")

    print("-" * 60)
    print(" RECENT ACTIVITY (EVENTS)")
    print("-" * 60)
    print(f" Commits Pushed : {activity_stats.get('commits', 0)}")
    print(f" Pull Requests  : {activity_stats.get('pull_requests', 0)}")
    print(f" Issues Opened  : {activity_stats.get('issues', 0)}")
    print(f" Stars Given    : {activity_stats.get('stars_given', 0)}")

    print("-" * 60)
    print(" TOP LANGUAGES DISTRIBUTION")
    print("-" * 60)
    if language_stats:
        for lang, pct, _ in language_stats[:8]:
            bar_len = 20
            filled = int(round(bar_len * pct / 100))
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f" {lang:<15} {pct:>5.1f}%  [{bar}]")
    else:
        print(" No language statistics available.")

    print("-" * 60)
    print(" TOP STARRED REPOSITORIES")
    print("-" * 60)
    top_repos = repo_stats.get("top_starred_repos", [])
    if top_repos:
        for repo in top_repos:
            print(f" • {repo['name']:<25} ⭐ {repo['stars']:<5} [{repo['language']}]")
    else:
        print(" No repositories found.")
    print("=" * 60 + "\n")


def print_console_comparison(comp_res: Dict[str, Any]) -> None:
    """Print side-by-side comparison table to stdout."""
    u1 = comp_res["user1_name"]
    u2 = comp_res["user2_name"]

    print("\n" + "=" * 65)
    print(f" DEVELOPER VS MODE: @{u1} vs @{u2}")
    print("=" * 65)
    print(f" {'METRIC':<25} | {u1:<12} | {u2:<12} | ADVANTAGE")
    print("-" * 65)

    for m in comp_res["metrics"]:
        print(f" {m['metric']:<25} | {m['val1']:<12} | {m['val2']:<12} | {m['winner']}")

    print("-" * 65)
    print(f" MATCH WINNER: {comp_res['overall_winner']}")
    print("=" * 65 + "\n")

