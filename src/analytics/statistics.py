"""
Data Analytics and Aggregation Engine.
Processes raw profile, repository, and event data into summarized statistics.
"""

from typing import Any, Dict, List, Tuple


class GitHubAnalytics:
    """Engine for computing statistics from raw GitHub REST API responses."""

    @staticmethod
    def process_repositories(repos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate stargazers, forks, open issues, and sort repositories.
        """
        total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
        total_forks = sum(repo.get("forks_count", 0) for repo in repos)
        total_open_issues = sum(repo.get("open_issues_count", 0) for repo in repos)

        # Sort repos by star count descending
        sorted_by_stars = sorted(
            repos, key=lambda r: r.get("stargazers_count", 0), reverse=True
        )

        top_starred = [
            {
                "name": r.get("name"),
                "stars": r.get("stargazers_count", 0),
                "forks": r.get("forks_count", 0),
                "language": r.get("language") or "N/A",
                "html_url": r.get("html_url"),
                "description": r.get("description") or "No description provided."
            }
            for r in sorted_by_stars[:5]
        ]

        return {
            "total_repositories": len(repos),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "total_open_issues": total_open_issues,
            "top_starred_repos": top_starred
        }

    @staticmethod
    def process_language_distribution(
        languages_by_repo: List[Dict[str, int]]
    ) -> List[Tuple[str, float, int]]:
        """
        Calculate global language statistics (percentage and total bytes).
        
        :return: List of tuples (language_name, percentage, byte_count) sorted descending.
        """
        totals: Dict[str, int] = {}
        for repo_langs in languages_by_repo:
            for lang, bytes_cnt in repo_langs.items():
                totals[lang] = totals.get(lang, 0) + bytes_cnt

        global_bytes = sum(totals.values())
        if global_bytes == 0:
            return []

        lang_percentages = []
        for lang, count in totals.items():
            percentage = round((count / global_bytes) * 100, 2)
            lang_percentages.append((lang, percentage, count))

        # Sort by percentage descending
        lang_percentages.sort(key=lambda x: x[1], reverse=True)
        return lang_percentages

    @staticmethod
    def process_events(events: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Extract activity metrics from recent GitHub user event stream.
        """
        commits_count = 0
        pull_requests_count = 0
        issues_count = 0
        stars_given_count = 0
        repo_created_count = 0

        for event in events:
            event_type = event.get("type")
            if event_type == "PushEvent":
                payload = event.get("payload", {})
                commits = payload.get("commits", [])
                commits_count += len(commits) if commits else 1
            elif event_type == "PullRequestEvent":
                pull_requests_count += 1
            elif event_type == "IssuesEvent":
                issues_count += 1
            elif event_type == "WatchEvent":
                stars_given_count += 1
            elif event_type == "CreateEvent":
                payload = event.get("payload", {})
                if payload.get("ref_type") == "repository":
                    repo_created_count += 1

        return {
            "commits": commits_count,
            "pull_requests": pull_requests_count,
            "issues": issues_count,
            "stars_given": stars_given_count,
            "repositories_created": repo_created_count,
            "total_recent_events": len(events)
        }
