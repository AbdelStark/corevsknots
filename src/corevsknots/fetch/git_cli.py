"""
Git command-line operations for local repository analysis.

This module provides a wrapper for Git command-line operations to analyze
local repository metrics that may not be available through the GitHub API.
"""

import os
import re
import subprocess
import tempfile
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger
from ..utils.time_utils import format_date_for_git, months_ago

logger = get_logger(__name__)


class GitCLI:
    """
    Wrapper for Git command-line operations.
    """

    def __init__(self, repo_path: Optional[str] = None, clone_url: Optional[str] = None, default_branch_hint: Optional[str] = None):
        """
        Initialize the Git CLI wrapper.

        Args:
            repo_path: Path to the local repository (if None, a temporary directory will be used)
            clone_url: URL to clone the repository (if None and repo_path doesn't exist, an error will be raised)
            default_branch_hint: A hint for the default branch name (e.g., 'main', 'master')
        """
        self.repo_path = repo_path
        self.temp_dir = None

        if repo_path and not os.path.exists(os.path.join(repo_path, ".git")):
            if clone_url:
                logger.info(f"Cloning repository {clone_url} to {repo_path}")
                os.makedirs(repo_path, exist_ok=True)
                self._execute_git_command(["clone", clone_url, repo_path])
                if default_branch_hint:
                    try:
                        logger.info(f"Attempting to checkout default branch hint: {default_branch_hint} in {repo_path}")
                        self._execute_git_command(["checkout", default_branch_hint], cwd=repo_path) # Ensure cwd is correct for checkout
                    except subprocess.CalledProcessError as e:
                        logger.warning(f"Failed to checkout branch {default_branch_hint} in {repo_path}, continuing with current HEAD: {e}")
            else:
                raise ValueError(f"Repository not found at {repo_path} and clone_url not provided")
        elif not repo_path:
            if not clone_url:
                raise ValueError("Either repo_path or clone_url must be provided")
            self.temp_dir = tempfile.TemporaryDirectory()
            self.repo_path = self.temp_dir.name
            logger.info(f"Cloning repository {clone_url} to temporary directory {self.repo_path}")
            # For temp clones, the clone command itself sets up the repo_path, subsequent commands use it as cwd by default
            self._execute_git_command(["clone", clone_url, "."], cwd=self.repo_path) # Clone into the temp dir
            if default_branch_hint:
                try:
                    logger.info(f"Attempting to checkout default branch hint: {default_branch_hint} in temp clone {self.repo_path}")
                    self._execute_git_command(["checkout", default_branch_hint]) # cwd will default to self.repo_path
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to checkout branch {default_branch_hint} in temp clone, continuing with current HEAD: {e}")
        # If repo_path is provided and valid, we assume it's already setup and potentially on the desired branch.

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

        try:
            output = self._execute_git_command(args)
            return int(output)
        except subprocess.CalledProcessError as e:
            if "Needed a single revision" in e.stderr or \
               (hasattr(e, 'stdout') and e.stdout == "" and e.stderr and "fatal:" in e.stderr):
                logger.warning(f"Git rev-list command for count failed (likely no revisions in range for branch '{branch}' since '{since}', until '{until}'), returning 0. stderr: {e.stderr.strip()}")
                return 0
            else:
                logger.error(f"Git rev-list command for count failed unexpectedly for branch '{branch}'. stderr: {e.stderr.strip()}")
                raise
        except ValueError as e:
            error_arg_detail = str(e.args[0]) if hasattr(e, "args") and e.args else "N/A"
            logger.error(f"Git rev-list output for count was not an integer for branch '{branch}'. Output: '{error_arg_detail}'. Error: {e}")
            return 0

    def get_commits(
        self,
        since: Optional[str] = None,
        until: Optional[str] = None,
        branch: str = "HEAD",
        max_count: Optional[int] = None,
        format_string: str = "%H%x00%an%x00%ae%x00%at%x00%s",
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

        # Add --no-show-signature to prevent signature data from interfering with parsing
        args.append("--no-show-signature")

        output = self._execute_git_command(args)
        commits = []
        for i, line in enumerate(output.split('\n')):
            if not line:
                continue
            parts = line.split("\x00")  # Split by null byte
            if len(parts) >= 5:
                try:
                    commit = {
                        "sha": parts[0],
                        "author_name": parts[1],
                        "author_email": parts[2],
                        "timestamp": int(parts[3]),
                        "message": parts[4],
                    }
                    commits.append(commit)
                except ValueError as ve:
                    logger.error(f"Error parsing commit line {i+1} for timestamp: '{line}'. Parts: {parts}. Error: {ve}")
                except Exception as e:
                    logger.error(f"Generic error parsing commit line {i+1}: '{line}'. Error: {e}")
            else:
                logger.warning(f"Skipping malformed commit line {i+1} (expected >= 5 parts, got {len(parts)}): '{line}'")
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

        output: Optional[str] = None
        try:
            output = self._execute_git_command(args)
        except subprocess.CalledProcessError as e:
            if "Needed a single revision" in e.stderr or \
               (hasattr(e, 'stdout') and e.stdout == "" and e.stderr and "fatal:" in e.stderr):
                logger.warning(f"Git shortlog command failed (likely no revisions in range since '{since}', until '{until}'), returning empty contributors. stderr: {e.stderr.strip()}")
                return {}
            else:
                logger.error(f"Git shortlog command failed unexpectedly. stderr: {e.stderr.strip()}")
                return {} # Return empty on other unexpected errors to prevent cascading failures

        contributors = {}
        if output: # Process output only if command was successful and output is not None
            for line in output.split('\n'):
                if not line:
                    continue
                match = re.match(r"^\s*(\d+)\s+(.+)\s+<(.+)>$", line)
                if match:
                    count, name, email = match.groups()
                    try:
                        contributors[email] = {"name": name, "email": email, "commits": int(count)}
                    except ValueError:
                        logger.error(f"Could not parse commit count '{count}' for contributor: {name} <{email}>")
        return contributors

    def get_file_changes(
        self, since: Optional[str] = None, until: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get the number of files changed, insertions, and deletions.

        Args:
            since: Start date (YYYY-MM-DD format for Git)
            until: End date (YYYY-MM-DD format for Git)

        Returns:
            Dictionary with file change statistics
        """
        args = ["log", "--shortstat", "--pretty=format:"]  # Empty pretty format to only get stats

        if since:
            args.append(f"--since={since}")
        if until:
            args.append(f"--until={until}")

        # If neither since nor until is specified, get stats for all commits on current HEAD
        # This might be very slow for large repos. Consider defaulting to a limited range or specific commit.
        if not since and not until:
            args.append("HEAD")

        output = self._execute_git_command(args)

        total_files_changed = 0
        total_insertions = 0
        total_deletions = 0

        # Each commit's stats are on a new line after an empty line from pretty=format:
        # Example: " 1 file changed, 1 insertion(+)"
        for line in output.split("\n"):
            line = line.strip()
            if not line:  # Skip empty lines from pretty format
                continue

            match_files = re.search(r"(\d+) files? changed", line)
            if match_files:
                total_files_changed += int(match_files.group(1))

            match_insertions = re.search(r"(\d+) insertions?\(\+\)", line)
            if match_insertions:
                total_insertions += int(match_insertions.group(1))

            match_deletions = re.search(r"(\d+) deletions?\(-\)", line)
            if match_deletions:
                total_deletions += int(match_deletions.group(1))

        return {"files_changed": total_files_changed, "insertions": total_insertions, "deletions": total_deletions}

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
        since_for_git = format_date_for_git(since_date)

        args = ["log", "--date=format:%Y-%m", "--pretty=format:%cd", f"--since={since_for_git}", "HEAD"]

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
        since_for_git = format_date_for_git(since_date)

        logger.info(f"Analyzing repository at {self.repo_path} for the last {months} months (since {since_for_git})")

        metrics = {}

        # Basic repository information
        try:
            origin_url = self._execute_git_command(["config", "--get", "remote.origin.url"])
            metrics["repo_url"] = origin_url
        except subprocess.CalledProcessError:
            metrics["repo_url"] = None

        # Commit count
        try:
            metrics["commit_count"] = self.get_commit_count(since=since_for_git)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get commit count: {e}")
            metrics["commit_count"] = 0

        # Contributors
        try:
            metrics["contributors"] = self.get_contributors(since=since_for_git)
            metrics["contributor_count"] = len(metrics["contributors"])
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get contributors: {e}")
            metrics["contributors"] = {}
            metrics["contributor_count"] = 0

        # Commit distribution
        try:
            metrics["commit_distribution"] = self.get_commit_authors_distribution(since=since_for_git)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to get commit distribution: {e}")
            metrics["commit_distribution"] = {}

        # File changes
        try:
            metrics["file_changes"] = self.get_file_changes(since=since_for_git)
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
            main_branch = None
            # Try to detect the main branch: main, then master, then development, then dev
            for branch_candidate in ["main", "master", "development", "dev"]:
                try:
                    self._execute_git_command(["rev-parse", "--verify", branch_candidate])
                    main_branch = branch_candidate
                    logger.debug(f"Detected main branch for git operations: {main_branch}")
                    break
                except subprocess.CalledProcessError:
                    continue

            if not main_branch:
                logger.warning("Could not reliably determine main branch for git operations, defaulting to trying 'HEAD' for direct commits.")
                main_branch = "HEAD" # Fallback to HEAD which might give all local branches not ideal but better than erroring

            direct_commits = self.get_direct_commits_to_branch(branch=main_branch, since=since_for_git)
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
