"""
Pull request analysis metrics.

This module calculates metrics related to repository pull request patterns,
review process, and lifecycle.
"""

from collections import Counter
from typing import Any, Dict, List

from ..utils.logger import get_logger
from ..utils.time_utils import parse_date

logger = get_logger(__name__)


def calculate_pr_metrics(github_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate pull request related metrics from GitHub API data.

    Args:
        github_data: Repository data fetched from GitHub API

    Returns:
        Dictionary of pull request metrics
    """
    metrics = {}

    # Extract pull requests from GitHub data
    pull_requests = github_data.get("pull_requests", [])

    # Basic PR count
    metrics["total_prs"] = len(pull_requests)

    # If no PRs, return empty metrics
    if metrics["total_prs"] == 0:
        logger.warning("No pull requests found in GitHub data")
        return metrics

    # PR state distribution
    metrics.update(calculate_pr_state_distribution(pull_requests))

    # PR review metrics
    metrics.update(calculate_pr_review_metrics(pull_requests, github_data))

    # PR lifecycle metrics
    metrics.update(calculate_pr_lifecycle_metrics(pull_requests))

    # PR size metrics
    metrics.update(calculate_pr_size_metrics(pull_requests))

    # PR author distribution
    metrics.update(calculate_pr_author_distribution(pull_requests))

    return metrics


def calculate_pr_state_distribution(pull_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate distribution of pull request states.

    Args:
        pull_requests: List of pull requests

    Returns:
        Dictionary of pull request state metrics
    """
    if not pull_requests:
        return {
            "open_prs": 0,
            "closed_prs": 0,
            "merged_prs": 0,
            "open_ratio": 0,
            "merged_ratio": 0,
            "closed_unmerged_ratio": 0,
        }

    open_prs = sum(1 for pr in pull_requests if pr["state"] == "open")
    closed_prs = sum(1 for pr in pull_requests if pr["state"] == "closed")
    merged_prs = sum(1 for pr in pull_requests if pr.get("merged"))

    total = len(pull_requests)
    open_ratio = open_prs / total
    merged_ratio = merged_prs / total
    closed_unmerged_ratio = (closed_prs - merged_prs) / total

    return {
        "open_prs": open_prs,
        "closed_prs": closed_prs,
        "merged_prs": merged_prs,
        "open_ratio": round(open_ratio, 3),
        "merged_ratio": round(merged_ratio, 3),
        "closed_unmerged_ratio": round(closed_unmerged_ratio, 3),
    }


def calculate_pr_review_metrics(
    pull_requests: List[Dict[str, Any]], github_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate metrics related to pull request reviews.

    Args:
        pull_requests: List of pull requests
        github_data: Repository data fetched from GitHub API

    Returns:
        Dictionary of pull request review metrics
    """
    if not pull_requests:
        return {"avg_review_count": 0, "reviewed_pr_ratio": 0, "self_merged_ratio": 0}

    # Extract PR reviews
    pr_reviews = github_data.get("pr_reviews", {})
    pr_comments = github_data.get("pr_comments", {})

    # Count reviews for sampled PRs
    reviews_per_pr = []
    prs_with_reviews = 0
    self_merged = 0

    for pr in pull_requests:
        pr_number = pr.get("number")
        author_login = pr.get("user", {}).get("login")

        # Check if this PR has reviews in our sample
        if pr_number in pr_reviews:
            reviews = pr_reviews[pr_number]
            review_count = len(reviews)
            reviews_per_pr.append(review_count)

            if review_count > 0:
                prs_with_reviews += 1

        # Check for comments as a signal of review
        elif pr_number in pr_comments:
            comments = pr_comments[pr_number]
            if comments:
                reviews_per_pr.append(1)  # Count as at least one review
                prs_with_reviews += 1
            else:
                reviews_per_pr.append(0)

        # Check if PR was self-merged
        if pr.get("merged") and pr.get("merged_by", {}).get("login") == author_login:
            self_merged += 1

    # Calculate metrics
    avg_review_count = sum(reviews_per_pr) / len(reviews_per_pr) if reviews_per_pr else 0
    reviewed_pr_ratio = prs_with_reviews / len(pull_requests) if pull_requests else 0
    merged_prs = sum(1 for pr in pull_requests if pr.get("merged"))
    self_merged_ratio = self_merged / merged_prs if merged_prs else 0

    return {
        "avg_review_count": round(avg_review_count, 2),
        "reviewed_pr_ratio": round(reviewed_pr_ratio, 3),
        "self_merged_ratio": round(self_merged_ratio, 3),
    }


def calculate_pr_lifecycle_metrics(pull_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate metrics related to pull request lifecycle.

    Args:
        pull_requests: List of pull requests

    Returns:
        Dictionary of pull request lifecycle metrics
    """
    if not pull_requests:
        return {"avg_time_to_merge": 0, "avg_time_to_close": 0, "pr_velocity_score": 0}

    time_to_merge = []
    time_to_close = []

    for pr in pull_requests:
        created_at = parse_date(pr["created_at"])

        if pr.get("merged"):
            merged_at = parse_date(pr["merged_at"])
            merge_hours = (merged_at - created_at).total_seconds() / 3600
            time_to_merge.append(merge_hours)

        if pr["state"] == "closed" and not pr.get("merged"):
            closed_at = parse_date(pr["closed_at"])
            close_hours = (closed_at - created_at).total_seconds() / 3600
            time_to_close.append(close_hours)

    # Calculate metrics
    avg_time_to_merge = sum(time_to_merge) / len(time_to_merge) if time_to_merge else 0
    avg_time_to_close = sum(time_to_close) / len(time_to_close) if time_to_close else 0

    # PR velocity score (0-10)
    if avg_time_to_merge:
        # Heuristic: 24 hours -> 10 points, 7 days -> 5 points, 30 days -> 1 point
        if avg_time_to_merge <= 24:
            velocity_score = 10
        elif avg_time_to_merge <= 168:  # 7 days
            velocity_score = 5 + (168 - avg_time_to_merge) / (168 - 24) * 5
        elif avg_time_to_merge <= 720:  # 30 days
            velocity_score = 1 + (720 - avg_time_to_merge) / (720 - 168) * 4
        else:
            velocity_score = max(0, 1 - (avg_time_to_merge - 720) / 720)
    else:
        velocity_score = 0

    return {
        "avg_time_to_merge": round(avg_time_to_merge, 2),
        "avg_time_to_close": round(avg_time_to_close, 2),
        "pr_velocity_score": round(velocity_score, 1),
    }


def calculate_pr_size_metrics(pull_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate metrics related to pull request size.

    Args:
        pull_requests: List of pull requests

    Returns:
        Dictionary of pull request size metrics
    """
    if not pull_requests:
        return {"avg_pr_size": 0, "large_pr_ratio": 0}

    sizes = []
    large_prs = 0

    for pr in pull_requests:
        additions = pr.get("additions", 0)
        deletions = pr.get("deletions", 0)
        total_changes = additions + deletions
        sizes.append(total_changes)

        if total_changes > 1000:
            large_prs += 1

    avg_pr_size = sum(sizes) / len(sizes) if sizes else 0
    large_pr_ratio = large_prs / len(pull_requests)

    return {"avg_pr_size": round(avg_pr_size, 2), "large_pr_ratio": round(large_pr_ratio, 3)}


def calculate_pr_author_distribution(pull_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate distribution of pull request authors.

    Args:
        pull_requests: List of pull requests

    Returns:
        Dictionary of pull request author metrics
    """
    if not pull_requests:
        return {"unique_pr_authors": 0, "top_pr_authors": [], "external_pr_ratio": 0}

    authors = Counter()
    external_prs = 0

    for pr in pull_requests:
        author = pr.get("user", {}).get("login")
        if author:
            authors[author] += 1

        # Check if PR author is not a core contributor
        # (heuristic: author is not in top 10 committers)
        # This would need to be refined with actual core team data
        is_external = pr.get("author_association") not in ["OWNER", "MEMBER", "COLLABORATOR"]
        if is_external:
            external_prs += 1

    top_authors = authors.most_common(5)
    external_ratio = external_prs / len(pull_requests)

    return {
        "unique_pr_authors": len(authors),
        "top_pr_authors": top_authors,
        "external_pr_ratio": round(external_ratio, 3),
    }
