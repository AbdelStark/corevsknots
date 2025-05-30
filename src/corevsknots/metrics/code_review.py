"""
Code review process metrics.

This module calculates metrics related to the code review process,
review thoroughness, and review culture.
"""

from collections import Counter
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger
from ..utils.time_utils import parse_date

# from ..fetch.github_api import GitHubAPIClient # Import if type hinting client

logger = get_logger(__name__)


def calculate_code_review_metrics(github_data: Dict[str, Any],
                                  repo_name: Optional[str] = None,
                                  github_client: Optional[Any] = None # Actual type GitHubAPIClient but avoid circular for now
                                 ) -> Dict[str, Any]:
    """
    Calculate code review related metrics from GitHub API data.

    Args:
        github_data: Repository data fetched from GitHub API
        repo_name: Name of the repository
        github_client: GitHub API client

    Returns:
        Dictionary of code review metrics
    """
    metrics = {}

    # Extract pull requests and review data
    pull_requests = github_data.get("pull_requests", [])
    pr_reviews = github_data.get("pr_reviews", {})
    pr_comments = github_data.get("pr_comments", {})

    # If no PRs or review data, return empty metrics
    if not pull_requests or (not pr_reviews and not pr_comments):
        logger.warning("No pull requests or review data found in GitHub data")
        return metrics

    # Review volume and distribution
    metrics.update(calculate_review_volume_metrics(pull_requests, pr_reviews, pr_comments))

    # Review thoroughness and quality
    metrics.update(calculate_review_thoroughness_metrics(pull_requests, pr_reviews, pr_comments))

    # Review participants diversity
    metrics.update(calculate_review_diversity_metrics(pull_requests, pr_reviews, pr_comments))

    # Review responsiveness
    metrics.update(calculate_review_responsiveness_metrics(pull_requests, pr_reviews))

    # Self-merge patterns - pass client and repo_name
    metrics.update(calculate_self_merge_metrics(pull_requests, repo_name, github_client))

    return metrics


def calculate_review_volume_metrics(
    pull_requests: List[Dict[str, Any]],
    pr_reviews: Dict[int, List[Dict[str, Any]]],
    pr_comments: Dict[int, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Calculate metrics related to review volume.

    Args:
        pull_requests: List of pull requests
        pr_reviews: Dictionary mapping PR number to list of reviews
        pr_comments: Dictionary mapping PR number to list of comments

    Returns:
        Dictionary of review volume metrics
    """
    if not pull_requests:
        return {
            "total_reviews": 0,
            "total_review_comments": 0,
            "reviews_per_pr": 0,
            "comments_per_pr": 0,
        }

    # Count reviews and comments
    total_reviews = sum(len(reviews) for reviews in pr_reviews.values())
    total_comments = sum(len(comments) for comments in pr_comments.values())

    # Calculate per-PR metrics
    sample_size = len(pr_reviews)
    reviews_per_pr = total_reviews / sample_size if sample_size > 0 else 0
    comments_per_pr = total_comments / sample_size if sample_size > 0 else 0

    return {
        "total_reviews": total_reviews,
        "total_review_comments": total_comments,
        "reviews_per_pr": round(reviews_per_pr, 2),
        "comments_per_pr": round(comments_per_pr, 2),
    }


def calculate_review_thoroughness_metrics(
    pull_requests: List[Dict[str, Any]],
    pr_reviews: Dict[int, List[Dict[str, Any]]],
    pr_comments: Dict[int, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Calculate metrics related to review thoroughness.

    Args:
        pull_requests: List of pull requests
        pr_reviews: Dictionary mapping PR number to list of reviews
        pr_comments: Dictionary mapping PR number to list of comments

    Returns:
        Dictionary of review thoroughness metrics
    """
    if not pull_requests:
        return {
            "multi_reviewer_ratio": 0,
            "substantive_review_ratio": 0,
            "review_thoroughness_score": 0,
        }

    # Count PRs with multiple reviewers
    multi_reviewer_prs = 0
    substantive_review_prs = 0

    for pr_number, reviews in pr_reviews.items():
        # Check unique reviewers
        reviewers = set(
            review.get("user", {}).get("login") for review in reviews if review.get("user")
        )
        if len(reviewers) > 1:
            multi_reviewer_prs += 1

        # Check for substantive reviews (comments or requested changes)
        comments = pr_comments.get(pr_number, [])
        comment_count = len(comments)

        has_requested_changes = any(
            review.get("state") == "CHANGES_REQUESTED" for review in reviews
        )

        if comment_count >= 3 or has_requested_changes:
            substantive_review_prs += 1

    # Calculate metrics
    sample_size = len(pr_reviews)
    multi_reviewer_ratio = multi_reviewer_prs / sample_size if sample_size > 0 else 0
    substantive_review_ratio = substantive_review_prs / sample_size if sample_size > 0 else 0

    # Thoroughness score (0-10)
    review_thoroughness_score = multi_reviewer_ratio * 5 + substantive_review_ratio * 5

    return {
        "multi_reviewer_ratio": round(multi_reviewer_ratio, 3),
        "substantive_review_ratio": round(substantive_review_ratio, 3),
        "review_thoroughness_score": round(review_thoroughness_score, 1),
    }


def calculate_review_diversity_metrics(
    pull_requests: List[Dict[str, Any]],
    pr_reviews: Dict[int, List[Dict[str, Any]]],
    pr_comments: Dict[int, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    """
    Calculate metrics related to review participant diversity.

    Args:
        pull_requests: List of pull requests
        pr_reviews: Dictionary mapping PR number to list of reviews
        pr_comments: Dictionary mapping PR number to list of comments

    Returns:
        Dictionary of review diversity metrics
    """
    if not pull_requests:
        return {"unique_reviewers": 0, "top_reviewers": [], "reviewer_to_author_ratio": 0}

    # Count unique reviewers and reviews per reviewer
    reviewers = Counter()
    unique_authors = set()

    for pr_number, reviews in pr_reviews.items():
        # Count reviewers
        for review in reviews:
            reviewer = review.get("user", {}).get("login")
            if reviewer:
                reviewers[reviewer] += 1

        # Count unique PR authors
        for pr in pull_requests:
            if pr.get("number") == pr_number:
                author = pr.get("user", {}).get("login")
                if author:
                    unique_authors.add(author)
                break

    # Additional reviewers from comments
    for pr_number, comments in pr_comments.items():
        for comment in comments:
            reviewer = comment.get("user", {}).get("login")
            if reviewer:
                reviewers[reviewer] += 1

    # Calculate metrics
    unique_reviewers = len(reviewers)
    top_reviewers = reviewers.most_common(5)
    reviewer_to_author_ratio = unique_reviewers / len(unique_authors) if unique_authors else 0

    return {
        "unique_reviewers": unique_reviewers,
        "top_reviewers": top_reviewers,
        "reviewer_to_author_ratio": round(reviewer_to_author_ratio, 2),
    }


def calculate_review_responsiveness_metrics(
    pull_requests: List[Dict[str, Any]], pr_reviews: Dict[int, List[Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Calculate metrics related to review responsiveness.

    Args:
        pull_requests: List of pull requests
        pr_reviews: Dictionary mapping PR number to list of reviews

    Returns:
        Dictionary of review responsiveness metrics
    """
    if not pull_requests:
        return {"avg_time_to_first_review": 0, "review_responsiveness_score": 0}

    time_to_first_review = []

    for pr_number, reviews in pr_reviews.items():
        # Find the PR creation time
        pr_created_at = None
        for pr in pull_requests:
            if pr.get("number") == pr_number:
                pr_created_at = parse_date(pr["created_at"])
                break

        if not pr_created_at or not reviews:
            continue

        # Find the first review time
        review_times = sorted(
            [parse_date(review["submitted_at"]) for review in reviews if "submitted_at" in review]
        )

        if not review_times:
            continue

        first_review_time = review_times[0]
        hours_to_review = (first_review_time - pr_created_at).total_seconds() / 3600
        time_to_first_review.append(hours_to_review)

    # Calculate metrics
    avg_time_to_first_review = (
        sum(time_to_first_review) / len(time_to_first_review) if time_to_first_review else 0
    )

    # Responsiveness score (0-10)
    if avg_time_to_first_review:
        # Heuristic: 2 hours -> 10 points, 24 hours -> 7 points, 3 days -> 3 points, 7+ days -> 0-1 points
        if avg_time_to_first_review <= 2:
            responsiveness_score = 10
        elif avg_time_to_first_review <= 24:
            responsiveness_score = 7 + (24 - avg_time_to_first_review) / (24 - 2) * 3
        elif avg_time_to_first_review <= 72:
            responsiveness_score = 3 + (72 - avg_time_to_first_review) / (72 - 24) * 4
        elif avg_time_to_first_review <= 168:
            responsiveness_score = (168 - avg_time_to_first_review) / (168 - 72) * 3
        else:
            responsiveness_score = 0
    else:
        responsiveness_score = 0

    return {
        "avg_time_to_first_review": round(avg_time_to_first_review, 2),
        "review_responsiveness_score": round(responsiveness_score, 1),
    }


def calculate_self_merge_metrics(pull_requests: List[Dict[str, Any]],
                                 repo_name: Optional[str] = None,
                                 github_client: Optional[Any] = None
                                ) -> Dict[str, Any]:
    """Calculate metrics related to self-merge practices."""
    if not pull_requests: # Check only for PRs; repo_name & client check can be more granular
        logger.warning(f"[{repo_name or 'unknown'}] No pull requests provided for self-merge calculation.")
        return {"self_merged_count": 0, "self_merged_ratio": 0, "self_merged_prs_analyzed": 0}
    if not repo_name or not github_client:
        logger.warning(f"[{repo_name or 'unknown'}] Missing repo_name or github_client for accurate self-merge calculation. Using basic merged_by check only.")
        # Fallback to basic check if client is missing, or return empty if strictness is preferred

    self_merged_count = 0
    merged_prs_count = 0
    prs_analyzed_for_self_merge = 0

    for pr in pull_requests:
        # Check if the PR was merged by looking at the 'merged_at' field
        if not pr.get("merged_at"):
            continue

        merged_prs_count += 1
        prs_analyzed_for_self_merge += 1

        pr_number = pr.get("number", "N/A")
        author_login = pr.get("user", {}).get("login")
        merged_by_login = pr.get("merged_by", {}).get("login")
        logger.debug(f"[{repo_name}] PR #{pr_number}: Author={author_login}, MergedBy={merged_by_login}, MergedAt={pr.get('merged_at')}")

        is_self_merge = False
        if author_login and merged_by_login and author_login == merged_by_login:
            is_self_merge = True
            logger.debug(f"  PR #{pr_number}: Identified as self-merge (merged_by field).")
        elif author_login and not merged_by_login and pr.get("merge_commit_sha") and github_client and repo_name:
            merge_sha = pr.get("merge_commit_sha")
            logger.debug(f"  PR #{pr_number}: merged_by is null. Fetching merge commit {merge_sha}...")
            commit_details = github_client.get_commit_details(repo_name, merge_sha)
            if commit_details:
                commit_author_login = commit_details.get("author", {}).get("login")
                commit_committer_login = commit_details.get("committer", {}).get("login")
                logger.debug(f"    Merge commit {merge_sha}: Author={commit_author_login}, Committer={commit_committer_login}")
                if commit_author_login == author_login or commit_committer_login == author_login:
                    is_self_merge = True
                    logger.debug(f"  PR #{pr_number}: Identified as self-merge (merge commit author/committer match).")
            else:
                logger.warning(f"  PR #{pr_number}: Could not fetch details for merge commit {merge_sha}.")

        if is_self_merge:
            self_merged_count += 1

    self_merged_ratio = self_merged_count / merged_prs_count if merged_prs_count > 0 else 0
    logger.info(f"[{repo_name or 'unknown'}] Self-merge analysis: {self_merged_count} self-merged out of {merged_prs_count} merged PRs analyzed (Ratio: {self_merged_ratio:.2%}).")
    return {
        "self_merged_count": self_merged_count,
        "self_merged_ratio": round(self_merged_ratio, 3),
        "self_merged_prs_analyzed": prs_analyzed_for_self_merge
    }
