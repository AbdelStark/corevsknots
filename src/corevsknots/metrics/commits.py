"""
Commit patterns analysis metrics.

This module calculates metrics related to repository commit patterns,
frequency, and distribution.
"""

import re
from collections import Counter
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger
from ..utils.time_utils import parse_date
from .contributor import CORE_REPO_IDENTIFIER, KNOTS_REPO_IDENTIFIER, is_core_merge_commit

logger = get_logger(__name__)

# Temporary re-definition for is_core_merge_commit for standalone use if needed for this edit
# (Ideally, move to a shared util if used by multiple metric modules)
TEMP_KNOTS_REPO_IDENTIFIER = "bitcoinknots/bitcoin"

def temp_is_core_merge_commit(commit_message: str) -> bool:
    core_merge_patterns = [
        "Merge bitcoin/bitcoin#", "Merge remote-tracking branch 'upstream/master'",
        "Merge remote-tracking branch 'upstream/main'", "Merge pull request #\\d+ from bitcoin/bitcoin",
        "Sync with bitcoin/bitcoin"
    ]
    for pattern in core_merge_patterns:
        if pattern.lower() in commit_message.lower(): return True
    if re.match(r"Merge branch \'.*\' of https://github.com/bitcoin/bitcoin into ", commit_message, re.IGNORECASE):
        return True
    return False

def calculate_commit_metrics(
    github_data: Dict[str, Any], git_data: Optional[Dict[str, Any]] = None,
    repo_name: Optional[str] = None, core_commit_shas: Optional[set[str]] = None
) -> Dict[str, Any]:
    """
    Calculate commit-related metrics from GitHub API data and Git CLI data.

    Args:
        github_data: Repository data fetched from GitHub API
        git_data: Repository data fetched from Git CLI (optional)
        repo_name: Repository name (optional)
        core_commit_shas: Set of core commit SHAs (optional)

    Returns:
        Dictionary of commit metrics
    """
    metrics = {}
    is_knots_repo = repo_name == KNOTS_REPO_IDENTIFIER

    raw_commits = github_data.get("commits", [])
    original_commits_for_repo = []

    if is_knots_repo and core_commit_shas is not None:
        logger.info(f"[{repo_name}] Filtering Knots commits against {len(core_commit_shas)} Core SHAs.")
        for commit in raw_commits:
            # Primary check: SHA matching against Core commits
            if commit.get('sha') in core_commit_shas:
                # This commit is from Core, skip for original Knots analysis
                continue
            # Secondary check: message patterns (for commits not found in Core by SHA, e.g. rebased merges)
            if is_core_merge_commit(commit.get("commit", {}).get("message", "")):
                # This looks like a Core merge by message, even if SHA differs, skip.
                continue
            original_commits_for_repo.append(commit)
        logger.info(f"[{repo_name}] Found {len(original_commits_for_repo)} original Knots commits out of {len(raw_commits)} total fetched for period after SHA and message filtering.")
    else: # For Core or if core_commit_shas not provided (or not a Knots repo)
        if repo_name == CORE_REPO_IDENTIFIER: # Use imported CORE_REPO_IDENTIFIER
            for commit in raw_commits:
                if not is_core_merge_commit(commit.get("commit", {}).get("message", "")):
                    original_commits_for_repo.append(commit)
        else:
            original_commits_for_repo = raw_commits

    metrics["total_commits_in_period"] = len(raw_commits) # Total fetched in period
    metrics["original_commits_in_period"] = len(original_commits_for_repo) # Original after filtering for Knots

    if not original_commits_for_repo:
        logger.warning(f"[{repo_name or 'unknown'}] No original commits to analyze for the period.")
        # Return basic counts and empty/default for other metrics
        metrics.update({"commits_per_day": 0, "commit_frequency": "inactive", "commit_message_quality": {"quality_score": 0}})
        return metrics

    # All subsequent metrics based on original_commits_for_repo
    metrics.update(calculate_commit_frequency(original_commits_for_repo))
    metrics.update(calculate_commit_size_metrics(original_commits_for_repo))
    metrics["commit_message_quality"] = analyze_commit_messages(original_commits_for_repo)
    metrics.update(analyze_commit_authorship(original_commits_for_repo)) # This now reflects authors of original commits
    metrics.update(analyze_merge_commits(original_commits_for_repo)) # Merge commits within the original set (e.g. feature branches in Knots)
    metrics.update(analyze_commit_activity_patterns(original_commits_for_repo))

    # direct_commit_ratio might need context if it was based on total_commits vs original_commits for Knots
    if git_data and "direct_commit_count" in git_data:
        metrics["direct_commit_count_git"] = git_data["direct_commit_count"]
        # Ratio of direct to original commits might be more insightful for Knots
        metrics["direct_to_original_commit_ratio"] = (
            git_data["direct_commit_count"] / len(original_commits_for_repo)
            if original_commits_for_repo
            else 0
        )

    return metrics


def calculate_commit_frequency(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate commit frequency metrics.

    Args:
        commits: List of commits

    Returns:
        Dictionary of commit frequency metrics
    """
    # Sort commits by date
    dated_commits = []
    for commit in commits:
        if "commit" in commit and "committer" in commit["commit"]:
            date_str = commit["commit"]["committer"].get("date")
            if date_str:
                dated_commits.append((parse_date(date_str), commit))

    if not dated_commits:
        return {
            "commits_per_day": 0,
            "commits_per_week": 0,
            "commits_per_month": 0,
            "commit_activity_days": 0,
            "commit_frequency": "inactive",
        }

    # Sort by date
    dated_commits.sort(key=lambda x: x[0])

    # Calculate time span
    first_date = dated_commits[0][0]
    last_date = dated_commits[-1][0]
    delta = (last_date - first_date).days + 1  # Add 1 to include both first and last day

    if delta <= 0:
        delta = 1  # Avoid division by zero

    # Count commits per day
    commits_by_day = Counter()
    for date, _ in dated_commits:
        commits_by_day[date.date()] += 1

    # Calculate metrics
    commits_per_day = len(commits) / delta
    commits_per_week = commits_per_day * 7
    commits_per_month = commits_per_day * 30
    active_days = len(commits_by_day)

    # Determine commit frequency category
    if commits_per_day > 3:
        frequency = "very_active"
    elif commits_per_day > 1:
        frequency = "active"
    elif commits_per_week > 1:
        frequency = "moderate"
    elif commits_per_month > 1:
        frequency = "low"
    else:
        frequency = "inactive"

    return {
        "commits_per_day": round(commits_per_day, 2),
        "commits_per_week": round(commits_per_week, 2),
        "commits_per_month": round(commits_per_month, 2),
        "commit_activity_days": active_days,
        "commit_activity_ratio": active_days / delta if delta > 0 else 0,
        "commit_frequency": frequency,
    }


def calculate_commit_size_metrics(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate metrics related to commit size.

    Args:
        commits: List of commits

    Returns:
        Dictionary of commit size metrics
    """
    stats = []

    for commit in commits:
        if "stats" in commit:
            additions = commit["stats"].get("additions", 0)
            deletions = commit["stats"].get("deletions", 0)
            total = additions + deletions
            stats.append((additions, deletions, total))

    if not stats:
        return {"avg_commit_size": 0, "large_commit_ratio": 0}

    total_changes = [t for _, _, t in stats]

    # Average commit size
    avg_commit_size = sum(total_changes) / len(stats)

    # Ratio of large commits (>300 lines)
    large_commits = [t for t in total_changes if t > 300]
    large_commit_ratio = len(large_commits) / len(stats) if stats else 0

    return {
        "avg_commit_size": round(avg_commit_size, 2),
        "large_commit_ratio": round(large_commit_ratio, 3),
    }


def analyze_commit_messages(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze commit message quality.

    Args:
        commits: List of commits

    Returns:
        Dictionary of commit message quality metrics
    """
    if not commits:
        return {"avg_message_length": 0, "descriptive_ratio": 0, "quality_score": 0}

    message_lengths = []
    descriptive_count = 0

    for commit in commits:
        if "commit" in commit and "message" in commit["commit"]:
            message = commit["commit"]["message"]

            # Get first line of commit message
            first_line = message.split("\n")[0].strip()
            message_lengths.append(len(first_line))

            # Check if message is descriptive (more than 5 words)
            words = first_line.split()
            if len(words) > 5:
                descriptive_count += 1

    if not message_lengths:
        return {"avg_message_length": 0, "descriptive_ratio": 0, "quality_score": 0}

    avg_length = sum(message_lengths) / len(message_lengths)
    descriptive_ratio = descriptive_count / len(commits)

    # Calculate quality score (0-10)
    length_score = min(10, avg_length / 5)  # 50 chars -> 10 points
    descriptive_score = descriptive_ratio * 10
    quality_score = (length_score + descriptive_score) / 2

    return {
        "avg_message_length": round(avg_length, 2),
        "descriptive_ratio": round(descriptive_ratio, 3),
        "quality_score": round(quality_score, 1),
    }


def analyze_commit_authorship(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze commit authorship patterns.

    Args:
        commits: List of commits

    Returns:
        Dictionary of commit authorship metrics
    """
    if not commits:
        return {"unique_authors": 0, "top_authors": []}

    authors = Counter()

    for commit in commits:
        author = None

        # Try to get GitHub username first
        if commit.get("author") and commit["author"].get("login"):
            author = commit["author"]["login"]
        # Fall back to name from commit data
        elif commit.get("commit", {}).get("author", {}).get("name"):
            author = commit["commit"]["author"]["name"]

        if author:
            authors[author] += 1

    # Top authors (by commit count)
    top_authors = authors.most_common(5)

    return {"unique_authors": len(authors), "top_authors": top_authors}


def analyze_merge_commits(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze merge commits vs direct commits.

    Args:
        commits: List of commits

    Returns:
        Dictionary of merge commit metrics
    """
    if not commits:
        return {"merge_commit_count": 0, "merge_commit_ratio": 0}

    merge_commits = 0

    for commit in commits:
        if "commit" in commit and "message" in commit["commit"]:
            message = commit["commit"]["message"]

            # Check if it's a merge commit
            if message.startswith("Merge") and (
                "pull request" in message or "branch" in message or "into" in message
            ):
                merge_commits += 1

    merge_ratio = merge_commits / len(commits)

    return {"merge_commit_count": merge_commits, "merge_commit_ratio": round(merge_ratio, 3)}


def analyze_commit_activity_patterns(commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze commit activity patterns by day of week and hour.

    Args:
        commits: List of commits

    Returns:
        Dictionary of commit activity pattern metrics
    """
    if not commits:
        return {"commits_by_day": {}, "commits_by_hour": {}}

    # Count commits by day of week and hour
    commits_by_day = Counter()
    commits_by_hour = Counter()

    for commit in commits:
        if "commit" in commit and "committer" in commit["commit"]:
            date_str = commit["commit"]["committer"].get("date")
            if date_str:
                date = parse_date(date_str)
                day = date.strftime("%A")  # Monday, Tuesday, etc.
                hour = date.hour

                commits_by_day[day] += 1
                commits_by_hour[hour] += 1

    # Sort by day of week
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    commits_by_day = {day: commits_by_day.get(day, 0) for day in days_order}

    # Sort by hour
    commits_by_hour = {str(hour): commits_by_hour.get(hour, 0) for hour in range(24)}

    return {"commits_by_day": commits_by_day, "commits_by_hour": commits_by_hour}
