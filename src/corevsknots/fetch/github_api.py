"""
GitHub API client for fetching repository data.

This module provides a client for interacting with the GitHub API to fetch
data about repositories, commits, pull requests, issues, and other metrics.
"""

import os
import time
from typing import Any, Dict, List, Optional

import requests

from ..utils.logger import get_logger
from ..utils.time_utils import format_date, months_ago, parse_date
from .cache import Cache

logger = get_logger(__name__)


class GitHubAPIClient:
    """
    Client for interacting with the GitHub API.

    This class provides methods for fetching repository data from GitHub,
    handling authentication, rate limiting, and pagination.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        api_url: str = "https://api.github.com",
        use_cache: bool = True,
        cache_dir: str = "./.cache",
        cache_expiry: int = 24,
    ):
        """
        Initialize the GitHub API client.

        Args:
            token: GitHub personal access token (optional)
            api_url: GitHub API URL (default: https://api.github.com)
            use_cache: Whether to use cache for API responses
            cache_dir: Directory to store cache files
            cache_expiry: Cache expiry time in hours
        """
        self.api_url = api_url.rstrip("/")
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }

        if token:
            self.headers["Authorization"] = f"token {token}"
        elif "GITHUB_TOKEN" in os.environ:
            self.headers["Authorization"] = f'token {os.environ["GITHUB_TOKEN"]}'

        self.use_cache = use_cache
        self.cache = Cache(cache_dir, cache_expiry) if use_cache else None
        self.rate_limit_remaining = None
        self.rate_limit_reset = None

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a request to the GitHub API.

        Args:
            endpoint: API endpoint (e.g., '/repos/bitcoin/bitcoin')
            params: Query parameters

        Returns:
            Response JSON

        Raises:
            requests.HTTPError: If the request fails
        """
        url = f"{self.api_url}{endpoint}"
        cache_key = f"{url}_{str(params)}"

        if self.use_cache and self.cache:
            cached_response = self.cache.get(cache_key)
            if cached_response:
                logger.debug(f"Using cached response for {url} (Params: {params})")
                return cached_response
            else:
                logger.debug(f"Cache miss for {url} (Params: {params})")

        if self.rate_limit_remaining is not None and self.rate_limit_remaining <= 1:
            wait_time = (self.rate_limit_reset or time.time()) - time.time()
            if wait_time > 0:
                logger.warning(f"Rate limit nearly exceeded. Waiting {wait_time:.1f} seconds before request to {url}...")
                time.sleep(wait_time + 1)

        logger.info(f"Fetching data from GitHub API: {url} (Params: {params})")
        response = requests.get(url, headers=self.headers, params=params)

        if "X-RateLimit-Remaining" in response.headers:
            self.rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
            self.rate_limit_reset = int(response.headers["X-RateLimit-Reset"])
            logger.debug(f"Rate limit: {self.rate_limit_remaining} remaining, resets at {self.rate_limit_reset}")

        response.raise_for_status()
        data = response.json()

        if self.use_cache and self.cache:
            self.cache.set(cache_key, data)
            logger.debug(f"Cached response for {url} (Params: {params})")

        return data

    def _paginate_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Make a paginated request to the GitHub API.

        Args:
            endpoint: API endpoint (e.g., '/repos/bitcoin/bitcoin/pulls')
            params: Query parameters

        Returns:
            List of response items

        Raises:
            requests.HTTPError: If the request fails
        """
        if params is None:
            params = {}

        if "per_page" not in params:
            params["per_page"] = 100

        all_items: List[Dict[str, Any]] = []
        page = 1
        more_pages = True
        logger.info(f"Fetching paginated data from endpoint: {endpoint} (Params: {params})")

        while more_pages:
            params["page"] = page
            logger.debug(f"Fetching page {page} for {endpoint}...")
            try:
                response_data = self._make_request(endpoint, params)

                if isinstance(response_data, list):
                    if not response_data:
                        more_pages = False
                        logger.debug(f"No more items found for {endpoint} on page {page}.")
                    else:
                        all_items.extend(response_data)
                        logger.debug(f"Fetched {len(response_data)} items on page {page} for {endpoint}. Total so far: {len(all_items)}.")
                        if len(response_data) < params["per_page"]:
                            more_pages = False
                            logger.debug(f"Last page detected for {endpoint} (items < per_page).")
                else:
                    logger.warning(f"Unexpected response type (not a list) for paginated request to {endpoint} on page {page}. Response: {response_data}")
                    if isinstance(response_data, dict) and response_data:
                        all_items.append(response_data)
                    more_pages = False

            except requests.HTTPError as e:
                logger.error(f"HTTP error fetching page {page} for {endpoint}: {e}")
                more_pages = False
            except Exception as e:
                logger.error(f"Generic error fetching page {page} for {endpoint}: {e}")
                more_pages = False

            if more_pages:
                page += 1
            if page > 30:
                logger.warning(f"Reached page limit (30) for {endpoint}. Stopping pagination.")
                more_pages = False

        logger.info(f"Finished fetching paginated data for {endpoint}. Total items: {len(all_items)}.")
        return all_items

    def get_repository(self, repo: str) -> Dict[str, Any]:
        """
        Get repository information.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')

        Returns:
            Repository information
        """
        endpoint = f"/repos/{repo}"
        return self._make_request(endpoint)

    def get_contributors(self, repo: str, since: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get repository contributors.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')
            since: ISO 8601 formatted timestamp to filter by contribution date

        Returns:
            List of contributors
        """
        endpoint = f"/repos/{repo}/contributors"
        params = {}
        if since:
            params["since"] = since

        return self._paginate_request(endpoint, params)

    def get_commits(
        self,
        repo: str,
        since: Optional[str] = None,
        until: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get repository commits.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')
            since: ISO 8601 formatted timestamp for start date
            until: ISO 8601 formatted timestamp for end date
            branch: Branch name

        Returns:
            List of commits
        """
        endpoint = f"/repos/{repo}/commits"
        params = {}

        if since:
            params["since"] = since
        if until:
            params["until"] = until
        if branch:
            params["sha"] = branch

        return self._paginate_request(endpoint, params)

    def get_pull_requests(
        self,
        repo: str,
        state: str = "all",
        since: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get repository pull requests.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')
            state: PR state ('open', 'closed', 'all')
            since: ISO 8601 formatted timestamp
            branch: Branch name

        Returns:
            List of pull requests
        """
        endpoint = f"/repos/{repo}/pulls"
        params = {"state": state}

        if branch:
            params["base"] = branch

        prs = self._paginate_request(endpoint, params)

        # Filter by date if needed (GitHub API doesn't support 'since' for PRs)
        if since:
            since_date = parse_date(since)
            prs = [pr for pr in prs if parse_date(pr["created_at"]) >= since_date]

        return prs

    def get_pull_request_reviews(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get reviews for a pull request.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')
            pr_number: Pull request number

        Returns:
            List of reviews
        """
        endpoint = f"/repos/{repo}/pulls/{pr_number}/reviews"
        return self._paginate_request(endpoint)

    def get_pull_request_comments(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """
        Get comments for a pull request.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')
            pr_number: Pull request number

        Returns:
            List of comments
        """
        endpoint = f"/repos/{repo}/pulls/{pr_number}/comments"
        return self._paginate_request(endpoint)

    def get_issues(
        self,
        repo: str,
        state: str = "all",
        since: Optional[str] = None,
        labels: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get repository issues.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')
            state: Issue state ('open', 'closed', 'all')
            since: ISO 8601 formatted timestamp
            labels: List of label names

        Returns:
            List of issues
        """
        endpoint = f"/repos/{repo}/issues"
        params = {"state": state}

        if since:
            params["since"] = since
        if labels:
            params["labels"] = ",".join(labels)

        # Filter out pull requests from the issues list
        all_issues = self._paginate_request(endpoint, params)
        return [issue for issue in all_issues if "pull_request" not in issue]

    def get_workflow_runs(self, repo: str, branch: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get workflow runs for the repository.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')
            branch: Branch name

        Returns:
            List of workflow runs
        """
        endpoint = f"/repos/{repo}/actions/runs"
        params = {}

        if branch:
            params["branch"] = branch

        response = self._make_request(endpoint, params)
        return response.get("workflow_runs", [])

    def get_commit_status(self, repo: str, commit_sha: str) -> Dict[str, Any]:
        """
        Get the combined status for a commit.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')
            commit_sha: Commit SHA

        Returns:
            Combined status information
        """
        endpoint = f"/repos/{repo}/commits/{commit_sha}/status"
        return self._make_request(endpoint)

    def get_repository_traffic(self, repo: str) -> Dict[str, Any]:
        """
        Get repository traffic statistics.

        Note: Requires push access to the repository.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')

        Returns:
            Traffic statistics
        """
        # Views
        views = self._make_request(f"/repos/{repo}/traffic/views")

        # Clones
        clones = self._make_request(f"/repos/{repo}/traffic/clones")

        # Popular content
        popular_paths = self._make_request(f"/repos/{repo}/traffic/popular/paths")
        popular_referrers = self._make_request(f"/repos/{repo}/traffic/popular/referrers")

        return {
            "views": views,
            "clones": clones,
            "popular_paths": popular_paths,
            "popular_referrers": popular_referrers,
        }

    def get_repository_stats(self, repo: str) -> Dict[str, Any]:
        """
        Get various repository statistics.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')

        Returns:
            Dictionary of repository statistics
        """
        stats = {}

        # Contributors statistics
        try:
            endpoint = f"/repos/{repo}/stats/contributors"
            stats["contributors"] = self._make_request(endpoint)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get contributor stats: {e}")
            stats["contributors"] = []

        # Commit activity
        try:
            endpoint = f"/repos/{repo}/stats/commit_activity"
            stats["commit_activity"] = self._make_request(endpoint)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get commit activity: {e}")
            stats["commit_activity"] = []

        # Code frequency
        try:
            endpoint = f"/repos/{repo}/stats/code_frequency"
            stats["code_frequency"] = self._make_request(endpoint)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get code frequency: {e}")
            stats["code_frequency"] = []

        # Participation
        try:
            endpoint = f"/repos/{repo}/stats/participation"
            stats["participation"] = self._make_request(endpoint)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get participation stats: {e}")
            stats["participation"] = []

        # Punch card
        try:
            endpoint = f"/repos/{repo}/stats/punch_card"
            stats["punch_card"] = self._make_request(endpoint)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get punch card stats: {e}")
            stats["punch_card"] = []

        return stats

    def get_repository_metrics(self, repo: str, months: int = 12) -> Dict[str, Any]:
        """
        Get comprehensive repository metrics.

        Args:
            repo: Repository name (e.g., 'bitcoin/bitcoin')
            months: Number of months to analyze

        Returns:
            Dictionary of repository metrics
        """
        since_date = months_ago(months)
        since = format_date(since_date)

        logger.info(f"Fetching metrics for {repo} since {since}")

        metrics = {}

        # Basic repository information
        try:
            metrics["repo_info"] = self.get_repository(repo)
        except requests.HTTPError as e:
            logger.error(f"Failed to get repository info: {e}")
            return {}

        # Contributors
        try:
            metrics["contributors"] = self.get_contributors(repo)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get contributors: {e}")
            metrics["contributors"] = []

        # Commits
        try:
            metrics["commits"] = self.get_commits(repo, since=since)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get commits: {e}")
            metrics["commits"] = []

        # Pull requests
        try:
            metrics["pull_requests"] = self.get_pull_requests(repo, state="all", since=since)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get pull requests: {e}")
            metrics["pull_requests"] = []

        # Issues
        try:
            metrics["issues"] = self.get_issues(repo, state="all", since=since)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get issues: {e}")
            metrics["issues"] = []

        # PR reviews and comments (sample for the first 10 PRs)
        metrics["pr_reviews"] = {}
        metrics["pr_comments"] = {}

        for pr in metrics["pull_requests"][:10]:
            pr_number = pr["number"]
            try:
                metrics["pr_reviews"][pr_number] = self.get_pull_request_reviews(repo, pr_number)
            except requests.HTTPError as e:
                logger.warning(f"Failed to get reviews for PR #{pr_number}: {e}")
                metrics["pr_reviews"][pr_number] = []

            try:
                metrics["pr_comments"][pr_number] = self.get_pull_request_comments(repo, pr_number)
            except requests.HTTPError as e:
                logger.warning(f"Failed to get comments for PR #{pr_number}: {e}")
                metrics["pr_comments"][pr_number] = []

        # Workflow runs
        try:
            metrics["workflow_runs"] = self.get_workflow_runs(repo)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get workflow runs: {e}")
            metrics["workflow_runs"] = []

        # Repository statistics
        try:
            metrics["stats"] = self.get_repository_stats(repo)
        except requests.HTTPError as e:
            logger.warning(f"Failed to get repository stats: {e}")
            metrics["stats"] = {}

        return metrics
