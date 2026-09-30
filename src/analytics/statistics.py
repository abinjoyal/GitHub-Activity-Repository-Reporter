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

    @staticmethod
    def compare_users(
        user1_data: Dict[str, Any],
        user2_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Side-by-side comparison engine for two GitHub developer profiles.
        """
        u1_name = user1_data["profile"].get("login", "User 1")
        u2_name = user2_data["profile"].get("login", "User 2")

        metrics_list = [
            ("Public Repositories", "total_repositories", "repo_stats"),
            ("Total Stars Received", "total_stars", "repo_stats"),
            ("Total Repository Forks", "total_forks", "repo_stats"),
            ("Recent Commits Pushed", "commits", "activity_stats"),
            ("Recent Pull Requests", "pull_requests", "activity_stats"),
        ]

        comparison_results = []
        u1_score = 0
        u2_score = 0

        for label, key, group in metrics_list:
            val1 = user1_data[group].get(key, 0)
            val2 = user2_data[group].get(key, 0)

            if val1 > val2:
                winner = u1_name
                u1_score += 1
            elif val2 > val1:
                winner = u2_name
                u2_score += 1
            else:
                winner = "Tie 🤝"

            comparison_results.append({
                "metric": label,
                "val1": val1,
                "val2": val2,
                "winner": winner
            })

        if u1_score > u2_score:
            overall_winner = f"🏆 {u1_name}"
        elif u2_score > u1_score:
            overall_winner = f"🏆 {u2_name}"
        else:
            overall_winner = "🤝 Equal Match!"

        return {
            "user1_name": u1_name,
            "user2_name": u2_name,
            "user1_score": u1_score,
            "user2_score": u2_score,
            "overall_winner": overall_winner,
            "metrics": comparison_results
        }

