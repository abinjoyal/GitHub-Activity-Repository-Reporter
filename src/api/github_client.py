"""
GitHub REST API v3 Client Implementation.
Handles authentication, request headers, pagination, and error reporting.
"""

import os
from typing import Any, Dict, List, Optional
import requests


class GitHubAPIError(Exception):
    """Custom exception raised for GitHub API requests."""
    pass


class GitHubClient:
    """Client for interacting with the GitHub REST API v3."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub API client.
        
        :param token: Optional Personal Access Token for GitHub API authentication.
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Activity-Reporter/1.0"
        })
        if self.token:
            self.session.headers.update({"Authorization": f"token {self.token}"})

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Internal GET request handler with error checking.
        """
        url = endpoint if endpoint.startswith("http") else f"{self.BASE_URL}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=15)
        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error while connecting to GitHub: {e}")

        if response.status_code == 404:
            raise GitHubAPIError(f"Resource not found at target endpoint: {url}")
        elif response.status_code == 403:
            reset_time = response.headers.get("X-RateLimit-Reset", "unknown")
            raise GitHubAPIError(
                f"GitHub API rate limit exceeded or access forbidden. "
                f"Consider providing a GITHUB_TOKEN. Rate limit reset time: {reset_time}"
            )
        elif response.status_code != 200:
            raise GitHubAPIError(
                f"GitHub API returned error status {response.status_code}: {response.text}"
            )

        return response.json()

    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch user profile information."""
        return self._get(f"/users/{username}")

    def get_user_repos(self, username: str) -> List[Dict[str, Any]]:
        """
        Fetch all public repositories owned by the user (handles pagination).
        """
        repos: List[Dict[str, Any]] = []
        page = 1
        per_page = 100

        while True:
            page_repos = self._get(
                f"/users/{username}/repos",
                params={"per_page": per_page, "page": page, "type": "owner", "sort": "updated"}
            )
            if not page_repos or not isinstance(page_repos, list):
                break
            repos.extend(page_repos)
            if len(page_repos) < per_page:
                break
            page += 1

        return repos

    def get_repo_languages(self, languages_url: str) -> Dict[str, int]:
        """Fetch language distribution (in bytes) for a specific repository."""
        try:
            return self._get(languages_url)
        except GitHubAPIError:
            # Fallback if language endpoint fails for a single repo
            return {}

    def get_user_events(self, username: str) -> List[Dict[str, Any]]:
        """Fetch recent public events for the specified user."""
        try:
            return self._get(f"/users/{username}/events", params={"per_page": 100})
        except GitHubAPIError:
            return []
