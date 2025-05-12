"""
Issue tracking analysis metrics.

This module calculates metrics related to issue tracking, responsiveness,
and project management practices.
"""

from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..utils.logger import get_logger
from ..utils.time_utils import parse_date

logger = get_logger(__name__)


def calculate_issue_metrics(github_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate issue-related metrics from GitHub API data.

    Args:
        github_data: Repository data fetched from GitHub API

    Returns:
        Dictionary of issue metrics
    """
    metrics = {}

    # Extract issues
    issues = github_data.get("issues", [])

    # Basic issue count
    metrics["total_issues"] = len(issues)

    # If no issues, return empty metrics
    if metrics["total_issues"] == 0:
        logger.warning("No issues found in GitHub data")
        return metrics

    # Issue state distribution
    metrics.update(calculate_issue_state_distribution(issues))

    # Issue responsiveness
    metrics.update(calculate_issue_responsiveness(issues))

    # Issue labels and categorization
    metrics.update(analyze_issue_labels(issues))

    # Issue author distribution
    metrics.update(analyze_issue_authors(issues))

    # Issue closure patterns
    metrics.update(analyze_issue_closure(issues))

    return metrics


def calculate_issue_state_distribution(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate distribution of issue states.

    Args:
        issues: List of issues

    Returns:
        Dictionary of issue state metrics
    """
    if not issues:
        return {"open_issues": 0, "closed_issues": 0, "open_ratio": 0}

    open_issues = sum(1 for issue in issues if issue.get("state") == "open")
    closed_issues = sum(1 for issue in issues if issue.get("state") == "closed")

    total = len(issues)
    open_ratio = open_issues / total

    return {
        "open_issues": open_issues,
        "closed_issues": closed_issues,
        "open_ratio": round(open_ratio, 3),
    }


def calculate_issue_responsiveness(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate metrics related to issue responsiveness.

    Args:
        issues: List of issues

    Returns:
        Dictionary of issue responsiveness metrics
    """
    if not issues:
        return {
            "avg_time_to_first_response": 0,
            "avg_time_to_close": 0,
            "stale_issue_ratio": 0,
            "responsiveness_score": 0,
        }

    # Time to first response (approximated by first comment)
    time_to_first_response = []

    # Time to close
    time_to_close = []

    # Count stale issues (open and not updated in 30+ days)
    stale_issues = 0

    for issue in issues:
        created_at = parse_date(issue["created_at"])

        # First response time (approximate)
        if "comments" in issue and issue["comments"] > 0:
            # Note: We don't have access to actual comment times in the current data model
            # For a complete implementation, we would need to fetch comments separately
            # This is just a placeholder calculation
            updated_at = parse_date(issue["updated_at"])
            time_to_first_response.append((updated_at - created_at).total_seconds() / 3600)

        # Time to close
        if issue["state"] == "closed" and "closed_at" in issue:
            closed_at = parse_date(issue["closed_at"])
            close_time = (closed_at - created_at).total_seconds() / 3600
            time_to_close.append(close_time)

        # Check if issue is stale
        if issue["state"] == "open":
            updated_at = parse_date(issue["updated_at"])
            now = datetime.now()
            if (now - updated_at).days > 30:
                stale_issues += 1

    # Calculate metrics
    avg_time_to_first_response = (
        sum(time_to_first_response) / len(time_to_first_response) if time_to_first_response else 0
    )

    avg_time_to_close = sum(time_to_close) / len(time_to_close) if time_to_close else 0

    open_issues = sum(1 for issue in issues if issue["state"] == "open")
    stale_issue_ratio = stale_issues / open_issues if open_issues > 0 else 0

    # Calculate responsiveness score (0-10)
    if avg_time_to_first_response:
        # Heuristic: 2 hours -> 10 points, 24 hours -> 7 points, 3 days -> 3 points, 7+ days -> 0-1 points
        if avg_time_to_first_response <= 2:
            first_response_score = 10
        elif avg_time_to_first_response <= 24:
            first_response_score = 7 + (24 - avg_time_to_first_response) / (24 - 2) * 3
        elif avg_time_to_first_response <= 72:
            first_response_score = 3 + (72 - avg_time_to_first_response) / (72 - 24) * 4
        elif avg_time_to_first_response <= 168:
            first_response_score = (168 - avg_time_to_first_response) / (168 - 72) * 3
        else:
            first_response_score = 0
    else:
        first_response_score = 0

    # Stale issue impact on score
    stale_score = 10 * (1 - stale_issue_ratio)

    # Overall responsiveness score
    responsiveness_score = first_response_score * 0.7 + stale_score * 0.3

    return {
        "avg_time_to_first_response": round(avg_time_to_first_response, 2),
        "avg_time_to_close": round(avg_time_to_close, 2),
        "stale_issues": stale_issues,
        "stale_issue_ratio": round(stale_issue_ratio, 3),
        "responsiveness_score": round(responsiveness_score, 1),
    }


def analyze_issue_labels(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze issue labels and categorization.

    Args:
        issues: List of issues

    Returns:
        Dictionary of issue label metrics
    """
    if not issues:
        return {"has_labels": False, "label_count": 0, "top_labels": [], "categorization_score": 0}

    # Count issues with labels
    issues_with_labels = sum(1 for issue in issues if issue.get("labels"))

    # Count unique labels
    all_labels = []
    for issue in issues:
        labels = issue.get("labels", [])
        if isinstance(labels, list):
            all_labels.extend(
                [
                    label.get("name")
                    for label in labels
                    if isinstance(label, dict) and "name" in label
                ]
            )

    label_counter = Counter(all_labels)
    unique_labels = len(label_counter)

    # Top labels
    top_labels = label_counter.most_common(5)

    # Calculate labeling ratio
    label_ratio = issues_with_labels / len(issues)

    # Calculate categorization score (0-10)
    if unique_labels >= 10 and label_ratio >= 0.9:
        categorization_score = 10
    elif unique_labels >= 5 and label_ratio >= 0.7:
        categorization_score = 7
    elif unique_labels >= 3 and label_ratio >= 0.5:
        categorization_score = 5
    elif unique_labels > 0:
        categorization_score = 3
    else:
        categorization_score = 0

    return {
        "has_labels": unique_labels > 0,
        "label_count": unique_labels,
        "labeled_issue_ratio": round(label_ratio, 3),
        "top_labels": top_labels,
        "categorization_score": round(categorization_score, 1),
    }


def analyze_issue_authors(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze issue author distribution.

    Args:
        issues: List of issues

    Returns:
        Dictionary of issue author metrics
    """
    if not issues:
        return {"unique_issue_authors": 0, "top_issue_authors": [], "external_issue_ratio": 0}

    # Count issue authors
    authors = Counter()
    external_issues = 0

    for issue in issues:
        author = issue.get("user", {}).get("login")
        if author:
            authors[author] += 1

        # Check if issue author is not a core contributor
        # (heuristic: author association not OWNER, MEMBER, or COLLABORATOR)
        is_external = issue.get("author_association") not in ["OWNER", "MEMBER", "COLLABORATOR"]
        if is_external:
            external_issues += 1

    top_authors = authors.most_common(5)
    external_ratio = external_issues / len(issues)

    return {
        "unique_issue_authors": len(authors),
        "top_issue_authors": top_authors,
        "external_issue_ratio": round(external_ratio, 3),
    }


def analyze_issue_closure(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze issue closure patterns.

    Args:
        issues: List of issues

    Returns:
        Dictionary of issue closure metrics
    """
    if not issues:
        return {"closure_rate": 0, "recently_closed_ratio": 0}

    # Count closed issues
    closed_issues = sum(1 for issue in issues if issue.get("state") == "closed")

    # Count recently closed issues (last 30 days)
    now = datetime.now()
    thirty_days_ago = now - timedelta(days=30)

    recently_closed = 0
    for issue in issues:
        if issue.get("state") == "closed" and "closed_at" in issue:
            closed_at = parse_date(issue["closed_at"])
            if closed_at >= thirty_days_ago:
                recently_closed += 1

    # Calculate closure rate
    closure_rate = closed_issues / len(issues)

    # Calculate recently closed ratio
    recently_closed_ratio = recently_closed / len(issues)

    return {
        "closure_rate": round(closure_rate, 3),
        "recently_closed": recently_closed,
        "recently_closed_ratio": round(recently_closed_ratio, 3),
        "issue_velocity_score": round(
            min(10, recently_closed / 10), 1
        ),  # Simple heuristic: 0-10 score
    }
