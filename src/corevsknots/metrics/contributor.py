"""
Contributor analysis metrics.

This module calculates metrics related to repository contributor diversity,
activity, and distribution.
"""

import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

from ..utils.logger import get_logger

logger = get_logger(__name__)

CORE_REPO_IDENTIFIER = "bitcoin/bitcoin" # Define for checking
KNOTS_REPO_IDENTIFIER = "bitcoinknots/bitcoin"

def is_core_merge_commit(commit_message: str) -> bool:
    """Check if a commit message suggests a merge from Bitcoin Core."""
    core_merge_patterns = [
        "Merge bitcoin/bitcoin#",
        "Merge remote-tracking branch 'upstream/master'", # Common for forks
        "Merge remote-tracking branch 'upstream/main'",
        "Merge pull request #\\d+ from bitcoin/bitcoin",
        "Sync with bitcoin/bitcoin",
        # Add more patterns if observed
    ]
    for pattern in core_merge_patterns:
        if pattern.lower() in commit_message.lower():
            return True
    # Heuristic: if message is exactly "Merge branch 'X' of https://github.com/bitcoin/bitcoin into Y"
    if re.match(r"Merge branch '.*' of https://github.com/bitcoin/bitcoin into ", commit_message, re.IGNORECASE):
        return True
    return False

def calculate_contributor_metrics(
    github_data: Dict[str, Any], git_data: Optional[Dict[str, Any]] = None,
    repo_name: Optional[str] = None # Added to provide context
) -> Dict[str, Any]:
    """
    Calculate contributor-related metrics from GitHub API data and Git CLI data.

    Args:
        github_data: Repository data fetched from GitHub API
        git_data: Repository data fetched from Git CLI (optional)
        repo_name: Name of the repository (optional)

    Returns:
        Dictionary of contributor metrics
    """
    metrics = {}
    is_knots_repo = repo_name == KNOTS_REPO_IDENTIFIER
    if is_knots_repo:
        logger.info(f"[{repo_name}] Applying Knots-specific contributor logic.")

    # Extract contributors from GitHub data
    github_contributors = github_data.get("contributors", [])

    # Basic contributor count
    metrics["total_contributors"] = len(github_contributors)

    # If no contributors, return empty metrics
    if metrics["total_contributors"] == 0:
        logger.warning(f"[{repo_name or 'unknown'}] No contributors found in GitHub data")
        return metrics

    # Default contributor lists (based on GitHub API contributions endpoint - good for overall view)
    contributors_by_gh_api_contributions = [
        (contributor.get("login", "unknown"), contributor.get("contributions", 0))
        for contributor in github_contributors
    ]
    contributors_by_gh_api_contributions.sort(key=lambda x: x[1], reverse=True)
    metrics["contributors_by_commits"] = contributors_by_gh_api_contributions # This remains the GH API view
    metrics["top_contributors"] = contributors_by_gh_api_contributions[:10]

    # Initialize active/original author sets
    all_commit_authors = set()
    knots_original_commit_authors = set() # Authors who made at least one original commit to Knots
    core_merge_commit_authors = set()   # Authors who made at least one Core merge commit to Knots
    # For Knots: count original commits per author
    knots_author_original_commit_counts = Counter()

    commits_data = github_data.get("commits", [])
    if commits_data:
        for commit in commits_data:
            author_login = None
            if commit.get("author") and commit["author"].get("login"):
                author_login = commit["author"]["login"]
            elif commit.get("commit", {}).get("author", {}).get("name"):
                author_login = commit["commit"]["author"]["name"]

            if author_login:
                all_commit_authors.add(author_login)
                if is_knots_repo and "commit" in commit and "message" in commit["commit"]:
                    commit_message = commit["commit"]["message"]
                    if is_core_merge_commit(commit_message):
                        core_merge_commit_authors.add(author_login)
                    else:
                        knots_original_commit_authors.add(author_login)
                        knots_author_original_commit_counts[author_login] += 1
                elif not is_knots_repo: # For Core (or any non-Knots repo), all non-merge like commits are original
                    # This could be further refined if Core also merges from other sources
                    # but for Core vs Knots, this distinction is most important for Knots.
                    if not is_core_merge_commit(commit.get("commit", {}).get("message", "")): # crude check for core
                        knots_original_commit_authors.add(author_login) # reuse for general active authors
                        knots_author_original_commit_counts[author_login] +=1

        metrics["active_contributors"] = len(all_commit_authors)
        metrics["active_ratio"] = metrics["active_contributors"] / metrics["total_contributors"] if metrics["total_contributors"] > 0 else 0

        if is_knots_repo:
            metrics["knots_original_commit_authors_count"] = len(knots_original_commit_authors)
            metrics["core_merge_commit_authors_count"] = len(core_merge_commit_authors)
            only_merging_authors = core_merge_commit_authors - knots_original_commit_authors
            metrics["knots_contributors_only_merging_core"] = len(only_merging_authors)
            metrics["knots_contributors_with_original_work"] = len(knots_original_commit_authors)

            # Recalculate contributor lists for Knots based on original commits
            knots_contributors_by_original_commits_list = sorted(
                knots_author_original_commit_counts.items(),
                key=lambda item: item[1],
                reverse=True
            )
            metrics["knots_contributors_by_original_commits"] = knots_contributors_by_original_commits_list
            metrics["knots_top_original_contributors"] = knots_contributors_by_original_commits_list[:10]
            if knots_contributors_by_original_commits_list:
                original_commits_counts = [c[1] for c in knots_contributors_by_original_commits_list]
                metrics["knots_original_contributor_gini"] = calculate_gini_coefficient(original_commits_counts)
                metrics["knots_original_bus_factor"] = calculate_bus_factor(knots_contributors_by_original_commits_list)
            else:
                metrics["knots_original_contributor_gini"] = 0 # or 1.0 if preferred for no data
                metrics["knots_original_bus_factor"] = 0
            logger.info(f"[{repo_name}] Knots original work: Gini={metrics.get('knots_original_contributor_gini')}, BusFactor={metrics.get('knots_original_bus_factor')}")
    else:
        metrics["active_contributors"] = 0
        metrics["active_ratio"] = 0
        if is_knots_repo:
            metrics["knots_original_commit_authors_count"] = 0
            metrics["core_merge_commit_authors_count"] = 0
            metrics["knots_contributors_only_merging_core"] = 0
            metrics["knots_contributors_with_original_work"] = 0

    # Default Gini and Bus Factor (uses GH API contributions for non-Knots or as a fallback)
    if not (is_knots_repo and "knots_original_bus_factor" in metrics): # if not already set by knots specific logic
        if len(contributors_by_gh_api_contributions) > 1:
            commits_counts_gh_api = [c[1] for c in contributors_by_gh_api_contributions]
            metrics["contributor_gini"] = calculate_gini_coefficient(commits_counts_gh_api)
        else:
            metrics["contributor_gini"] = 1.0
        metrics["bus_factor"] = calculate_bus_factor(contributors_by_gh_api_contributions)

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
