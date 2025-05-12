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
    repo_name: Optional[str] = None,
    core_commit_shas: Optional[set[str]] = None # New param
) -> Dict[str, Any]:
    """
    Calculate contributor-related metrics from GitHub API data and Git CLI data.

    Args:
        github_data: Repository data fetched from GitHub API
        git_data: Repository data fetched from Git CLI (optional)
        repo_name: Name of the repository (optional)
        core_commit_shas: Set of SHA-1 hashes of Core merge commits (optional)

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

    # Initialize active/original author sets and counts
    all_commit_authors_in_period = set()
    knots_original_commit_authors = set()
    core_merge_commit_authors = set()
    knots_author_original_commit_counts = Counter()
    knots_author_core_merge_commit_counts = Counter()
    # For Core, or non-Knots repos, treat all commits (not matching merge patterns) as "original" for consistency in this logic block
    non_knots_author_commit_counts = Counter()
    knots_original_author_emails = set() # New: to store emails of original Knots commit authors

    commits_data = github_data.get("commits", [])
    if commits_data:
        for commit in commits_data:
            author_login = None
            if commit.get("author") and commit["author"].get("login"):
                author_login = commit["author"]["login"]
            elif commit.get("commit", {}).get("author", {}).get("name"):
                author_login = commit["commit"]["author"]["name"]

            if author_login:
                all_commit_authors_in_period.add(author_login)
                commit_sha = commit.get('sha')
                commit_message = commit.get("commit", {}).get("message", "")
                # Get author email from the commit object itself (more reliable for git history)
                git_commit_author_email = commit.get("commit", {}).get("author", {}).get("email")

                if is_knots_repo:
                    is_merged_from_core = (core_commit_shas is not None and commit_sha in core_commit_shas) or \
                                          is_core_merge_commit(commit_message)
                    if is_merged_from_core:
                        core_merge_commit_authors.add(author_login)
                        knots_author_core_merge_commit_counts[author_login] += 1
                    else:
                        knots_original_commit_authors.add(author_login)
                        knots_author_original_commit_counts[author_login] += 1
                        if git_commit_author_email: # Collect email for original commit
                            knots_original_author_emails.add(git_commit_author_email)
                else: # For Core or other repos, count all non-heuristic-merge commits towards this count
                    if not is_core_merge_commit(commit_message): # Basic check to exclude obvious upstream merges for Core itself
                        non_knots_author_commit_counts[author_login] += 1

        metrics["active_contributors"] = len(all_commit_authors_in_period)
        metrics["active_ratio"] = metrics["active_contributors"] / metrics["total_contributors"] if metrics["total_contributors"] > 0 else 0

        if is_knots_repo:
            metrics["knots_original_commit_authors_count"] = len(knots_original_commit_authors)
            metrics["core_merge_commit_authors_count"] = len(core_merge_commit_authors)
            knots_authors_only_merging = core_merge_commit_authors - knots_original_commit_authors
            metrics["knots_contributors_only_merging_core"] = len(knots_authors_only_merging)
            metrics["knots_contributors_with_original_work"] = len(knots_original_commit_authors)

            knots_contrib_by_original = sorted(knots_author_original_commit_counts.items(), key=lambda item: item[1], reverse=True)
            metrics["knots_contributors_by_original_commits"] = knots_contrib_by_original
            metrics["knots_top_original_contributors"] = knots_contrib_by_original[:10]
            if knots_contrib_by_original:
                original_counts = [c[1] for c in knots_contrib_by_original]
                metrics["knots_original_contributor_gini"] = calculate_gini_coefficient(original_counts)
                metrics["knots_original_bus_factor"] = calculate_bus_factor(knots_contrib_by_original)
            else:
                metrics["knots_original_contributor_gini"] = 0.0
                metrics["knots_original_bus_factor"] = 0
            logger.info(f"[{repo_name}] Knots original work (based on {len(commits_data)} recent commits): Gini={metrics.get('knots_original_contributor_gini')}, BusFactor={metrics.get('knots_original_bus_factor')}")
        else: # For Core or other repos, use non_knots_author_commit_counts for a comparable Gini/BusFactor
            core_like_contrib_by_commits = sorted(non_knots_author_commit_counts.items(), key=lambda item: item[1], reverse=True)
            if core_like_contrib_by_commits:
                core_like_counts = [c[1] for c in core_like_contrib_by_commits]
                metrics["contributor_gini"] = calculate_gini_coefficient(core_like_counts)
                metrics["bus_factor"] = calculate_bus_factor(core_like_contrib_by_commits)
            else:
                metrics["contributor_gini"] = 0.0
                metrics["bus_factor"] = 0
    else:
        metrics["active_contributors"] = 0
        metrics["active_ratio"] = 0
        if is_knots_repo:
            metrics["knots_original_commit_authors_count"] = 0
            metrics["core_merge_commit_authors_count"] = 0
            metrics["knots_contributors_only_merging_core"] = 0
            metrics["knots_contributors_with_original_work"] = 0

    # General Gini/Bus Factor from GH API /contributors as overall view, remove if Knots version is preferred as primary
    # For clarity, let's ensure general bus_factor & gini are always present from GH API for all repos for now.
    if len(contributors_by_gh_api_contributions) > 1:
        commits_counts_gh_api = [c[1] for c in contributors_by_gh_api_contributions]
        # Only set general gini if not already set by non-Knots path above
        if not (not is_knots_repo and "contributor_gini" in metrics):
            metrics["contributor_gini"] = calculate_gini_coefficient(commits_counts_gh_api)
    elif not (not is_knots_repo and "contributor_gini" in metrics):
        metrics["contributor_gini"] = 1.0

    if not (not is_knots_repo and "bus_factor" in metrics):
        metrics["bus_factor"] = calculate_bus_factor(contributors_by_gh_api_contributions)

    # Organizational Diversity
    if is_knots_repo:
        if knots_original_author_emails:
            # Create a mock contributors dict for count_email_domains just for these emails
            knots_original_contributors_for_domain_count = {email: {} for email in knots_original_author_emails}
            metrics["email_domains"] = count_email_domains(knots_original_contributors_for_domain_count)
            metrics["organization_count"] = len(metrics["email_domains"])
            metrics["organization_diversity"] = calculate_diversity_score(list(metrics["email_domains"].values())) # Pass list of counts
            logger.info(f"[{repo_name}] Knots original work org diversity: Count={metrics['organization_count']}, Diversity={metrics['organization_diversity']:.3f}")
        else:
            metrics["email_domains"] = {}
            metrics["organization_count"] = 0
            metrics["organization_diversity"] = 0.0
    elif git_data and "contributors" in git_data: # For Core or general repos with git_data
        git_contributors = git_data["contributors"]
        metrics["email_domains"] = count_email_domains(git_contributors)
        metrics["organization_count"] = len(metrics["email_domains"])
        metrics["organization_diversity"] = calculate_diversity_score(list(metrics["email_domains"].values()))
    else: # Fallback if no relevant data
        metrics["email_domains"] = {}
        metrics["organization_count"] = 0
        metrics["organization_diversity"] = 0.0

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
