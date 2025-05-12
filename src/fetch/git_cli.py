"""
Git command-line operations for local repository analysis.

This module provides a wrapper for Git command-line operations to analyze
local repository metrics that may not be available through the GitHub API.
"""

import logging
import os
import re
import subprocess
import tempfile
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from ..utils.logger import get_logger
from ..utils.time_utils import format_date, months_ago, parse_date

logger = get_logger(__name__)


class GitCLI:
    """
    Wrapper for Git command-line operations.
    """

    def __init__(self, repo_path: Optional[str] = None, clone_url: Optional[str] = None):
        """
        Initialize the Git CLI wrapper.

        Args:
            repo_path: Path to the local repository (if None, a temporary directory will be used)
            clone_url: URL to clone the repository (if None and repo_path doesn't exist, an error will be raised)
        """
        self.repo_path = repo_path
        self.temp_dir = None

        # Check if repo_path exists
        if repo_path and not os.path.exists(os.path.join(repo_path, ".git")):
            # If repo_path doesn't exist but clone_url is provided, clone the repository
            if clone_url:
                logger.info(f"Cloning repository {clone_url} to {repo_path}")
                os.makedirs(repo_path, exist_ok=True)
                self._execute_git_command(["clone", clone_url, repo_path])
            else:
                raise ValueError(f"Repository not found at {repo_path} and clone_url not provided")

        # If repo_path is not provided, create a temporary directory and clone the repository
        elif not repo_path:
            if not clone_url:
                raise ValueError("Either repo_path or clone_url must be provided")

            self.temp_dir = tempfile.TemporaryDirectory()
            self.repo_path = self.temp_dir.name

            logger.info(f"Cloning repository {clone_url} to temporary directory {self.repo_path}")
            self._execute_git_command(["clone", clone_url, self.repo_path])

    def __del__(self):
        """
        Clean up temporary directory when the object is destroyed.
        """
        if self.temp_dir:
            self.temp_dir.cleanup()

    def _execute_git_command(self, args: List[str], cwd: Optional[str] = None) -> str:
        """
        Execute a Git command.

        Args:
            args: Command arguments (without 'git')
            cwd: Working directory

        Returns:
            Command output

        Raises:
            subprocess.CalledProcessError: If the command fails
        """
        cmd = ["git"] + args
        cwd = cwd or self.repo_path

        logger.debug(f"Executing git command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            return result.stdout.strip()

        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {e.stderr}")
            raise

    def get_commit_count(
        self, since: Optional[str] = None, until: Optional[str] = None, branch: str = "HEAD"
    ) -> int:
        """
        Get the number of commits in the repository.

        Args:
            since: Start date (ISO 8601 format or Git-compatible date format)
            until: End date (ISO 8601 format or Git-compatible date format)
            branch: Branch name

        Returns:
            Number of commits
        """
        args = ["rev-list", "--count", branch]

        if since:
            args.append(f"--since={since}")
        if until:
            args.append(f"--until={until}")

        output = self._execute_git_command(args)
        return int(output)

    def get_commits(
        self,
        since: Optional[str] = None,
        until: Optional[str] = None,
        branch: str = "HEAD",
        max_count: Optional[int] = None,
        format_string: str = "%H|%an|%ae|%at|%s",
    ) -> List[Dict[str, Any]]:
        """
        Get commits from the repository.

        Args:
            since: Start date (ISO 8601 format or Git-compatible date format)
            until: End date (ISO 8601 format or Git-compatible date format)
            branch: Branch name
            max_count: Maximum number of commits to return
            format_string: Format string for git log

        Returns:
            List of commits
        """
        args = ["log", f"--pretty=format:{format_string}", branch]

        if since:
            args.append(f"--since={since}")
        if until:
            args.append(f"--until={until}")
        if max_count:
            args.append(f"--max-count={max_count}")

        output = self._execute_git_command(args)
        commits = []

        for line in output.split("\n"):
            if not line:
                continue

            parts = line.split("|")
            if len(parts) >= 5:
                commit = {
                    "sha": parts[0],
                    "author_name": parts[1],
                    "author_email": parts[2],
                    "timestamp": int(parts[3]),
                    "message": parts[4],
                }
                commits.append(commit)

        return commits

    def get_contributors(
        self, since: Optional[str] = None, until: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get contributors to the repository.

        Args:
            since: Start date (ISO 8601 format or Git-compatible date format)
            until: End date (ISO 8601 format or Git-compatible date format)

        Returns:
            Dictionary mapping email to contributor information
        """
        args = ["shortlog", "-sne", "HEAD"]

        if since:
            args.append(f"--since={since}")
        if until:
            args.append(f"--until={until}")

        output = self._execute_git_command(args)
        contributors = {}

        for line in output.split("\n"):
            if not line:
                continue

            # Parse the shortlog output (e.g., "123\tJohn Doe <john@example.com>")
            match = re.match(r"^\s*(\d+)\s+(.+)\s+<(.+)>$", line)
            if match:
                count, name, email = match.groups()
                contributors[email] = {"name": name, "email": email, "commits": int(count)}

        return contributors

    def get_file_changes(
        self, since: Optional[str] = None, until: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get the number of files changed, insertions, and deletions.

        Args:
            since: Start date (ISO 8601 format or Git-compatible date format)
            until: End date (ISO 8601 format or Git-compatible date format)

        Returns:
            Dictionary with file change statistics
        """
        args = ["diff", "--shortstat"]

        if since:
            args.append(f"{since}..HEAD")
        elif until:
            args.append(f"HEAD..{until}")

        output = self._execute_git_command(args)

        # Parse the shortstat output (e.g., "10 files changed, 100 insertions(+), 50 deletions(-)")
        files = insertions = deletions = 0

        match_files = re.search(r"(\d+) files? changed", output)
        if match_files:
            files = int(match_files.group(1))

        match_insertions = re.search(r"(\d+) insertions?\(\+\)", output)
        if match_insertions:
            insertions = int(match_insertions.group(1))

        match_deletions = re.search(r"(\d+) deletions?\(-\)", output)
        if match_deletions:
            deletions = int(match_deletions.group(1))

        return {"files_changed": files, "insertions": insertions, "deletions": deletions}

    def get_branch_count(self) -> int:
        """
        Get the number of branches in the repository.

        Returns:
            Number of branches
        """
        output = self._execute_git_command(["branch", "-a"])
        branches = [b.strip() for b in output.split("\n") if b.strip()]
        return len(branches)

    def get_tag_count(self) -> int:
        """
        Get the number of tags in the repository.

        Returns:
            Number of tags
        """
        output = self._execute_git_command(["tag"])
        tags = [t.strip() for t in output.split("\n") if t.strip()]
        return len(tags)

    def get_direct_commits_to_branch(
        self, branch: str = "master", since: Optional[str] = None, max_count: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get commits that were pushed directly to a branch (not through a pull request).

        Args:
            branch: Branch name
            since: Start date (ISO 8601 format or Git-compatible date format)
            max_count: Maximum number of commits to analyze

        Returns:
            List of direct commits
        """
        # First, get the merge commits
        merge_commits_args = ["log", "--merges", "--pretty=format:%H", branch]

        if since:
            merge_commits_args.append(f"--since={since}")
        if max_count:
            merge_commits_args.append(f"--max-count={max_count}")

        merge_commits_output = self._execute_git_command(merge_commits_args)
        merge_commit_shas = set(merge_commits_output.split("\n"))

        # Then, get all commits
        all_commits = self.get_commits(since=since, branch=branch, max_count=max_count)

        # Filter out merge commits
        direct_commits = [
            commit for commit in all_commits if commit["sha"] not in merge_commit_shas
        ]

        return direct_commits

    def get_commit_authors_distribution(
        self, since: Optional[str] = None, until: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get the distribution of commits by author.

        Args:
            since: Start date (ISO 8601 format or Git-compatible date format)
            until: End date (ISO 8601 format or Git-compatible date format)

        Returns:
            Dictionary mapping author email to commit count
        """
        contributors = self.get_contributors(since=since, until=until)
        return {email: info["commits"] for email, info in contributors.items()}

    def get_commit_activity_by_month(self, months: int = 12) -> Dict[str, int]:
        """
        Get commit activity by month.

        Args:
            months: Number of months to analyze

        Returns:
            Dictionary mapping month to commit count
        """
        since_date = months_ago(months)
        since = format_date(since_date)

        args = ["log", "--date=format:%Y-%m", "--pretty=format:%cd", f"--since={since}", "HEAD"]

        output = self._execute_git_command(args)
        activity = {}

        for line in output.split("\n"):
            if not line:
                continue

            month = line.strip()
            if month in activity:
                activity[month] += 1
            else:
                activity[month] = 1

        return activity

    def get_test_files_count(self) -> int:
        """
        Get the number of test files in the repository.

        Returns:
            Number of test files
        """
        # Look for common test file patterns
        patterns = [
            "**/test_*.py",
            "**/*_test.py",
            "**/test-*.js",
            "**/*-test.js",
            "**/test_*.cpp",
            "**/*_test.cpp",
            "**/test-*.cpp",
            "**/*-test.cpp",
            "**/test/*.py",
            "**/test/*.js",
            "**/test/*.cpp",
            "**/tests/*.py",
            "**/tests/*.js",
            "**/tests/*.cpp",
        ]

        test_files = set()

        for pattern in patterns:
            try:
                args = ["ls-files", pattern]
                output = self._execute_git_command(args)

                for line in output.split("\n"):
                    if line.strip():
                        test_files.add(line.strip())

            except subprocess.CalledProcessError:
                # Ignore errors (pattern might not match any files)
                pass

        return len(test_files)

    def get_ci_config_files(self) -> List[str]:
        """
        Get CI configuration files in the repository.

        Returns:
            List of CI configuration files
        """
        # Common CI configuration files
        ci_files = [
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
            ".travis.yml",
            ".circleci/config.yml",
            "azure-pipelines.yml",
            "Jenkinsfile",
            ".gitlab-ci.yml",
            ".appveyor.yml",
            "bitbucket-pipelines.yml",
        ]

        found_files = []

        for pattern in ci_files:
            try:
                args = ["ls-files", pattern]
                output = self._execute_git_command(args)

                for line in output.split("\n"):
                    if line.strip():
                        found_files.append(line.strip())

            except subprocess.CalledProcessError:
                # Ignore errors (pattern might not match any files)
                pass

        return found_files

    def get_repository_metrics(self, months: int = 12) -> Dict[str, Any]:
        """
        Get comprehensive repository metrics.

        Args:
            months: Number of months to analyze

        Returns:
            Dictionary of repository metrics
        """
        since_date = months_ago(months)
        since = format_date(since_date)

        logger.info(f"Analyzing repository at {self.repo_path} for the last {months} months")

        metrics = {}

        # Basic repository information
        try:
            origin_url = self._execute_git_command(["config", "--get", "remote.origin.url"])
            metrics["repo_url"] = origin_url
        except subprocess.CalledProcessError:
            metrics["repo_url"] = None

        # Commit count
        try:
            metrics["commit_count"] = self.get_commit_count(since=since)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get commit count: {e}")
            metrics["commit_count"] = 0

        # Contributors
        try:
            metrics["contributors"] = self.get_contributors(since=since)
            metrics["contributor_count"] = len(metrics["contributors"])
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get contributors: {e}")
            metrics["contributors"] = {}
            metrics["contributor_count"] = 0

        # Commit distribution
        try:
            metrics["commit_distribution"] = self.get_commit_authors_distribution(since=since)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get commit distribution: {e}")
            metrics["commit_distribution"] = {}

        # File changes
        try:
            metrics["file_changes"] = self.get_file_changes(since=since)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get file changes: {e}")
            metrics["file_changes"] = {"files_changed": 0, "insertions": 0, "deletions": 0}

        # Branch and tag count
        try:
            metrics["branch_count"] = self.get_branch_count()
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get branch count: {e}")
            metrics["branch_count"] = 0

        try:
            metrics["tag_count"] = self.get_tag_count()
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get tag count: {e}")
            metrics["tag_count"] = 0

        # Direct commits to main branch
        try:
            # Try to detect the main branch
            for branch in ["master", "main", "development", "dev"]:
                try:
                    self._execute_git_command(["rev-parse", "--verify", branch])
                    main_branch = branch
                    break
                except subprocess.CalledProcessError:
                    continue
            else:
                # Default to master if no branch is found
                main_branch = "master"

            direct_commits = self.get_direct_commits_to_branch(branch=main_branch, since=since)
            metrics["direct_commits"] = direct_commits
            metrics["direct_commit_count"] = len(direct_commits)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get direct commits: {e}")
            metrics["direct_commits"] = []
            metrics["direct_commit_count"] = 0

        # Monthly commit activity
        try:
            metrics["monthly_activity"] = self.get_commit_activity_by_month(months=months)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get monthly activity: {e}")
            metrics["monthly_activity"] = {}

        # Testing
        try:
            metrics["test_files_count"] = self.get_test_files_count()
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get test files count: {e}")
            metrics["test_files_count"] = 0

        # CI/CD
        try:
            metrics["ci_config_files"] = self.get_ci_config_files()
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get CI config files: {e}")
            metrics["ci_config_files"] = []

        return metrics
