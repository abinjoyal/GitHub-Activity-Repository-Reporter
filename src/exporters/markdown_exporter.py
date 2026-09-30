"""
Markdown Exporter Implementation.
Compiles user profile statistics and repository analytics into a standardized Markdown file.
"""

import os
from typing import Any, Dict, List, Tuple
from datetime import datetime


class MarkdownExporter:
    """Exports processed GitHub metrics to a clean, professional Markdown report."""

    @staticmethod
    def generate_report(
        profile: Dict[str, Any],
        repo_stats: Dict[str, Any],
        language_stats: List[Tuple[str, float, int]],
        activity_stats: Dict[str, int],
        output_filepath: str = "reports/github-report.md"
    ) -> str:
        """
        Generate and write the Markdown report to disk.
        
        :return: Absolute or relative filepath of the generated report.
        """
        # Ensure output is placed in reports/ directory if not explicitly directed elsewhere
        if not os.path.dirname(output_filepath):
            output_filepath = os.path.join("reports", output_filepath)

        # Create output directory if it does not exist
        output_dir = os.path.dirname(output_filepath)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        username = profile.get("login", "Unknown")
        name = profile.get("name") or username
        bio = profile.get("bio") or "N/A"
        location = profile.get("location") or "N/A"
        company = profile.get("company") or "N/A"
        blog = profile.get("blog") or "N/A"
        followers = profile.get("followers", 0)
        following = profile.get("following", 0)
        profile_url = profile.get("html_url", f"https://github.com/{username}")
        generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        lines = [
            "# GitHub Activity & Repository Report",
            "",
            f"**Target User:** [{name} (@{username})]({profile_url})  ",
            f"**Report Generated:** {generated_at}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            "| Metric | Value |",
            "| :--- | :--- |",
            f"| Public Repositories | {repo_stats.get('total_repositories', 0)} |",
            f"| Total Stars Received | {repo_stats.get('total_stars', 0)} |",
            f"| Total Repository Forks | {repo_stats.get('total_forks', 0)} |",
            f"| Followers | {followers} |",
            f"| Following | {following} |",
            f"| Location | {location} |",
            f"| Organization / Company | {company} |",
            "",
            "---",
            "",
            "## Programming Language Statistics",
            "",
            "Language usage breakdown calculated across all public repositories:",
            "",
            "| Language | Share (%) | Total Bytes | Progress Bar |",
            "| :--- | :--- | :--- | :--- |"
        ]

        if language_stats:
            for lang, pct, count in language_stats[:10]:
                bar_length = 20
                filled = int(round(bar_length * pct / 100))
                bar = "█" * filled + "░" * (bar_length - filled)
                lines.append(f"| {lang} | {pct:.1f}% | {count:,} bytes | `{bar}` |")
        else:
            lines.append("| N/A | N/A | N/A | N/A |")

        lines.extend([
            "",
            "---",
            "",
            "## Recent Activity Breakdown",
            "",
            "Activity aggregated from the latest public event log:",
            "",
            "| Event Type | Count |",
            "| :--- | :--- |",
            f"| Commits Pushed | {activity_stats.get('commits', 0)} |",
            f"| Pull Requests Opened/Updated | {activity_stats.get('pull_requests', 0)} |",
            f"| Issues Created/Updated | {activity_stats.get('issues', 0)} |",
            f"| Repositories Starred | {activity_stats.get('stars_given', 0)} |",
            f"| Repositories Created | {activity_stats.get('repositories_created', 0)} |",
            "",
            "---",
            "",
            "## Top Starred Repositories",
            "",
            "| Repository | Primary Language | Stars | Forks | Description |",
            "| :--- | :--- | :--- | :--- | :--- |"
        ])

        top_repos = repo_stats.get("top_starred_repos", [])
        if top_repos:
            for r in top_repos:
                name_link = f"[{r['name']}]({r['html_url']})"
                desc = r["description"].replace("\n", " ")
                lines.append(
                    f"| {name_link} | {r['language']} | {r['stars']} | {r['forks']} | {desc} |"
                )
        else:
            lines.append("| N/A | N/A | N/A | N/A | N/A |")

        lines.extend([
            "",
            "---",
            "",
            "*Report generated automatically by GitHub Activity & Repo Reporter.*"
        ])

        content = "\n".join(lines)
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return output_filepath
