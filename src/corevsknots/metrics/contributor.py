"""
Contributor analysis metrics.

This module calculates metrics related to repository contributor diversity,
activity, and distribution.
"""

from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from ..utils.logger import get_logger

logger = get_logger(__name__)


def calculate_contributor_metrics(
    github_data: Dict[str, Any], git_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate contributor-related metrics from GitHub API data and Git CLI data.

    Args:
        github_data: Repository data fetched from GitHub API
        git_data: Repository data fetched from Git CLI (optional)

    Returns:
        Dictionary of contributor metrics
    """
    metrics = {}

    # Extract contributors from GitHub data
    github_contributors = github_data.get("contributors", [])

    # Basic contributor count
    metrics["total_contributors"] = len(github_contributors)

    # If no contributors, return empty metrics
    if metrics["total_contributors"] == 0:
        logger.warning("No contributors found in GitHub data")
        return metrics

    # Contributor distribution (by number of commits)
    contributors_by_commits = [
        (contributor.get("login", "unknown"), contributor.get("contributions", 0))
        for contributor in github_contributors
    ]
    contributors_by_commits.sort(key=lambda x: x[1], reverse=True)

    metrics["contributors_by_commits"] = contributors_by_commits

    # Top contributors
    metrics["top_contributors"] = contributors_by_commits[:10]

    # Calculate the Gini coefficient for contributor distribution
    # Higher value indicates higher inequality (e.g., one developer dominates)
    if len(contributors_by_commits) > 1:
        commits = [c[1] for c in contributors_by_commits]
        metrics["contributor_gini"] = calculate_gini_coefficient(commits)
    else:
        metrics["contributor_gini"] = 1.0  # Maximum inequality if only one contributor

    # Bus factor calculation
    # (Number of contributors needed to cover 80% of all contributions)
    metrics["bus_factor"] = calculate_bus_factor(contributors_by_commits)

    # Recent activity (from commits)
    commits = github_data.get("commits", [])
    if commits:
        # Extract unique contributors from recent commits
        commit_authors = set()
        for commit in commits:
            if commit.get("author") and commit["author"].get("login"):
                commit_authors.add(commit["author"]["login"])
            elif commit.get("commit", {}).get("author", {}).get("name"):
                commit_authors.add(commit["commit"]["author"]["name"])

        metrics["active_contributors"] = len(commit_authors)
        metrics["active_ratio"] = metrics["active_contributors"] / metrics["total_contributors"]
    else:
        metrics["active_contributors"] = 0
        metrics["active_ratio"] = 0

    # Additional metrics from Git CLI data if available
    if git_data and "contributors" in git_data:
        git_contributors = git_data["contributors"]

        # Count unique contributor emails
        metrics["email_domains"] = count_email_domains(git_contributors)

        # Organizational diversity (based on email domains)
        metrics["organization_count"] = len(metrics["email_domains"])

        # Calculate organization diversity score (Shannon entropy)
        metrics["organization_diversity"] = calculate_diversity_score(
            metrics["email_domains"].values()
        )

    return metrics


def calculate_gini_coefficient(values: List[int]) -> float:
    """
    Calculate the Gini coefficient for a distribution of values.

    The Gini coefficient measures inequality in a distribution.
    - 0 means perfect equality (all contributors have same number of commits)
    - 1 means perfect inequality (one contributor has all commits)

    Args:
        values: List of values (e.g., commit counts per contributor)

    Returns:
        Gini coefficient
    """
    if not values or sum(values) == 0:
        return 0

    values = sorted(values)
    cumsum = 0
    total = sum(values)
    gini = 0

    for i, value in enumerate(values):
        cumsum += value
        gini += (i + 1) * value

    gini = 2 * gini / (len(values) * total) - 1 - (1 / len(values))
    return max(0, gini)  # Ensure non-negative


def calculate_bus_factor(contributors_by_commits: List[Tuple[str, int]]) -> int:
    """
    Calculate the "bus factor" of a project.

    The bus factor is the minimum number of contributors that would need to be
    hit by a bus (or leave the project) before the project would be in serious trouble.

    Here we define it as the minimum number of contributors needed to cover
    80% of all contributions.

    Args:
        contributors_by_commits: List of (contributor, commit_count) tuples

    Returns:
        Bus factor
    """
    if not contributors_by_commits:
        return 0

    total_commits = sum(commits for _, commits in contributors_by_commits)
    if total_commits == 0:
        return 0

    threshold = 0.8 * total_commits
    cumulative = 0
    bus_factor = 0

    for _, commits in contributors_by_commits:
        cumulative += commits
        bus_factor += 1
        if cumulative >= threshold:
            break

    return bus_factor


def count_email_domains(contributors: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    """
    Count the number of contributors from different email domains.

    Args:
        contributors: Dictionary mapping email to contributor information

    Returns:
        Dictionary mapping domain to count
    """
    domains = Counter()

    for email, _ in contributors.items():
        # Extract domain from email
        try:
            domain = email.split("@")[-1]
            domains[domain] += 1
        except (IndexError, AttributeError):
            # Skip invalid emails
            continue

    return dict(domains)


def calculate_diversity_score(values: List[int]) -> float:
    """
    Calculate the Shannon entropy (diversity score) for a distribution.

    Higher values indicate more diversity (e.g., contributors from many organizations).

    Args:
        values: List of values (e.g., number of contributors per organization)

    Returns:
        Shannon entropy
    """
    import math

    if not values or sum(values) == 0:
        return 0

    total = sum(values)
    probabilities = [value / total for value in values]

    entropy = -sum(p * math.log(p) for p in probabilities if p > 0)
    max_entropy = math.log(len(values)) if len(values) > 0 else 0

    # Normalize to [0, 1]
    if max_entropy > 0:
        return entropy / max_entropy
    else:
        return 0
