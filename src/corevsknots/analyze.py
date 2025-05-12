"""
Main analysis coordinator.

This module coordinates the analysis of repositories, fetching data
and calculating metrics.
"""

from datetime import datetime
from typing import Any, Dict, Optional

# from .fetch import fetch_data, fetch_comparison_data # Removed F401
from .fetch.git_cli import GitCLI
from .fetch.github_api import GitHubAPIClient
from .metrics.ci_cd import calculate_cicd_metrics
from .metrics.code_review import calculate_code_review_metrics
from .metrics.commits import calculate_commit_metrics
from .metrics.contributor import calculate_contributor_metrics
from .metrics.issues import calculate_issue_metrics
from .metrics.pull_requests import calculate_pr_metrics
from .metrics.tests import calculate_test_metrics

# from .report import generate_report # Removed F401
from .utils.logger import get_logger
from .utils.time_utils import format_date, months_ago

logger = get_logger(__name__)


def analyze_repository(
    repo: str,
    months: int = 12,
    github_token: Optional[str] = None,
    local_path: Optional[str] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Analyze a GitHub repository.

    Args:
        repo: Repository name (e.g., 'bitcoin/bitcoin')
        months: Number of months to analyze
        github_token: GitHub personal access token
        local_path: Path to local repository clone
        use_cache: Whether to use cache for API responses

    Returns:
        Dictionary of repository metrics
    """
    logger.info(f"Analyzing repository: {repo} for the past {months} months")

    # Initialize GitHub API client
    github_client = GitHubAPIClient(token=github_token, use_cache=use_cache)

    # Fetch data from GitHub API
    since_date = months_ago(months)
    since = format_date(since_date)

    logger.info(f"Fetching GitHub data since: {since}")
    github_data = github_client.get_repository_metrics(repo, months)

    # Initialize Git CLI client if local path is provided
    git_data = None
    if local_path:
        logger.info(f"Analyzing local repository at: {local_path}")
        try:
            git_client = GitCLI(repo_path=local_path)
            git_data = git_client.get_repository_metrics(months)
        except Exception as e:
            logger.error(f"Failed to analyze local repository: {e}")
    else:
        # Try to clone the repository temporarily
        try:
            logger.info(f"Creating temporary clone of repository")
            repo_url = f"https://github.com/{repo}.git"
            git_client = GitCLI(clone_url=repo_url)
            git_data = git_client.get_repository_metrics(months)
        except Exception as e:
            logger.error(f"Failed to clone repository: {e}")

    # Calculate metrics
    metrics = calculate_all_metrics(github_data, git_data)

    # Add repository metadata
    metrics["repository"] = {
        "name": repo,
        "analysis_period_months": months,
        "analysis_date": datetime.now().isoformat(),
        "github_stars": github_data.get("repo_info", {}).get("stargazers_count"),
        "github_forks": github_data.get("repo_info", {}).get("forks_count"),
        "github_watchers": github_data.get("repo_info", {}).get("subscribers_count"),
        "default_branch": github_data.get("repo_info", {}).get("default_branch"),
        "language": github_data.get("repo_info", {}).get("language"),
    }

    # Calculate overall health score
    metrics["overall_health_score"] = calculate_overall_health_score(metrics)

    logger.info(f"Using cached metrics for {repo}")
    return metrics

    logger.info("Cache miss or invalid, fetching fresh data...")


def compare_repositories(
    repo1: str,
    repo2: str,
    months: int = 12,
    github_token: Optional[str] = None,
    local_path1: Optional[str] = None,
    local_path2: Optional[str] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """
    Compare two GitHub repositories.

    Args:
        repo1: First repository name (e.g., 'bitcoin/bitcoin')
        repo2: Second repository name (e.g., 'bitcoinknots/bitcoin')
        months: Number of months to analyze
        github_token: GitHub personal access token
        local_path1: Path to first local repository clone
        local_path2: Path to second local repository clone
        use_cache: Whether to use cache for API responses

    Returns:
        Dictionary containing metrics for both repositories
    """
    logger.info(f"Comparing repositories: {repo1} vs {repo2}")

    # Analyze both repositories
    metrics1 = analyze_repository(repo1, months, github_token, local_path1, use_cache)
    metrics2 = analyze_repository(repo2, months, github_token, local_path2, use_cache)

    # Structure the comparison result
    comparison = {
        "repo1": {"name": repo1, "metrics": metrics1},
        "repo2": {"name": repo2, "metrics": metrics2},
        "comparison": compare_metrics(metrics1, metrics2),
        "analysis_metadata": {"date": datetime.now().isoformat(), "period_months": months},
    }

    return comparison


def calculate_all_metrics(
    github_data: Dict[str, Any], git_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate all repository metrics.

    Args:
        github_data: Repository data fetched from GitHub API
        git_data: Repository data fetched from Git CLI (optional)

    Returns:
        Dictionary of all repository metrics
    """
    metrics = {}

    # Basic repository info
    if "repo_info" in github_data:
        metrics["repository_info"] = {
            "name": github_data["repo_info"].get("full_name"),
            "description": github_data["repo_info"].get("description"),
            "created_at": github_data["repo_info"].get("created_at"),
            "updated_at": github_data["repo_info"].get("updated_at"),
            "pushed_at": github_data["repo_info"].get("pushed_at"),
            "stars": github_data["repo_info"].get("stargazers_count"),
            "forks": github_data["repo_info"].get("forks_count"),
            "watchers": github_data["repo_info"].get("subscribers_count"),
            "open_issues": github_data["repo_info"].get("open_issues_count"),
            "language": github_data["repo_info"].get("language"),
            "license": (
                github_data["repo_info"].get("license", {}).get("name")
                if github_data["repo_info"].get("license")
                else None
            ),
        }

    # Calculate contributor metrics
    logger.info("Calculating contributor metrics")
    try:
        metrics["contributor"] = calculate_contributor_metrics(github_data, git_data)
    except Exception as e:
        logger.error(f"Failed to calculate contributor metrics: {e}")
        metrics["contributor"] = {}

    # Calculate commit metrics
    logger.info("Calculating commit metrics")
    try:
        metrics["commit"] = calculate_commit_metrics(github_data, git_data)
    except Exception as e:
        logger.error(f"Failed to calculate commit metrics: {e}")
        metrics["commit"] = {}

    # Calculate pull request metrics
    logger.info("Calculating pull request metrics")
    try:
        metrics["pull_request"] = calculate_pr_metrics(github_data)
    except Exception as e:
        logger.error(f"Failed to calculate pull request metrics: {e}")
        metrics["pull_request"] = {}

    # Calculate code review metrics
    logger.info("Calculating code review metrics")
    try:
        metrics["code_review"] = calculate_code_review_metrics(github_data)
    except Exception as e:
        logger.error(f"Failed to calculate code review metrics: {e}")
        metrics["code_review"] = {}

    # Calculate CI/CD metrics
    logger.info("Calculating CI/CD metrics")
    try:
        metrics["ci_cd"] = calculate_cicd_metrics(github_data, git_data)
    except Exception as e:
        logger.error(f"Failed to calculate CI/CD metrics: {e}")
        metrics["ci_cd"] = {}

    # Calculate issue metrics
    logger.info("Calculating issue metrics")
    try:
        metrics["issue"] = calculate_issue_metrics(github_data)
    except Exception as e:
        logger.error(f"Failed to calculate issue metrics: {e}")
        metrics["issue"] = {}

    # Calculate test metrics
    logger.info("Calculating test metrics")
    try:
        metrics["test"] = calculate_test_metrics(github_data, git_data)
    except Exception as e:
        logger.error(f"Failed to calculate test metrics: {e}")
        metrics["test"] = {}

    return metrics


def calculate_overall_health_score(metrics: Dict[str, Any]) -> float:
    """
    Calculate an overall repository health score.

    Args:
        metrics: Repository metrics

    Returns:
        Overall health score (0-10)
    """
    # Define weights for each category
    weights = {
        "contributor": 0.15,
        "commit": 0.15,
        "pull_request": 0.15,
        "code_review": 0.2,
        "ci_cd": 0.15,
        "issue": 0.1,
        "test": 0.1,
    }

    # Extract scores from each category
    scores = {}

    # Contributor score
    contributor = metrics.get("contributor", {})
    if contributor:
        bus_factor = contributor.get("bus_factor", 1)
        contributor_count = contributor.get("total_contributors", 0)

        # Higher bus factor and more contributors are better
        if bus_factor >= 10:
            scores["contributor"] = 10
        elif bus_factor >= 5:
            scores["contributor"] = 8
        elif bus_factor >= 3:
            scores["contributor"] = 6
        elif bus_factor == 2:
            scores["contributor"] = 4
        else:
            scores["contributor"] = 2

        # Adjust based on total contributors
        if contributor_count >= 100:
            scores["contributor"] = min(10, scores["contributor"] + 2)
        elif contributor_count >= 50:
            scores["contributor"] = min(10, scores["contributor"] + 1)
        elif contributor_count <= 3:
            scores["contributor"] = max(0, scores["contributor"] - 2)
    else:
        scores["contributor"] = 0

    # Commit score
    commit = metrics.get("commit", {})
    if commit:
        commit_frequency = commit.get("commit_frequency", "inactive")
        commit_message_quality = commit.get("commit_message_quality", {}).get("quality_score", 0)

        # Score based on commit frequency
        if commit_frequency == "very_active":
            scores["commit"] = 10
        elif commit_frequency == "active":
            scores["commit"] = 8
        elif commit_frequency == "moderate":
            scores["commit"] = 6
        elif commit_frequency == "low":
            scores["commit"] = 4
        else:
            scores["commit"] = 2

        # Adjust based on commit message quality
        scores["commit"] = scores["commit"] * 0.7 + commit_message_quality * 0.3
    else:
        scores["commit"] = 0

    # Pull request score
    pr = metrics.get("pull_request", {})
    if pr:
        merged_ratio = pr.get("merged_ratio", 0)
        pr_velocity = pr.get("pr_velocity_score", 0)

        # Higher merged ratio and faster PR velocity are better
        scores["pull_request"] = merged_ratio * 10 * 0.5 + pr_velocity * 0.5
    else:
        scores["pull_request"] = 0

    # Code review score
    review = metrics.get("code_review", {})
    if review:
        review_thoroughness = review.get("review_thoroughness_score", 0)
        self_merged_ratio = review.get("self_merged_ratio", 1)

        # Higher thoroughness and lower self-merge ratio are better
        scores["code_review"] = review_thoroughness * 0.7 + (1 - self_merged_ratio) * 10 * 0.3
    else:
        scores["code_review"] = 0

    # CI/CD score
    ci_cd = metrics.get("ci_cd", {})
    if ci_cd:
        has_ci = ci_cd.get("has_ci", False)
        success_rate = ci_cd.get("workflow_success_rate", 0)

        # Having CI and high success rate are better
        if has_ci:
            scores["ci_cd"] = 5 + success_rate * 5
        else:
            scores["ci_cd"] = 0
    else:
        scores["ci_cd"] = 0

    # Issue score
    issue = metrics.get("issue", {})
    if issue:
        responsiveness = issue.get("responsiveness_score", 0)
        categorization = issue.get("categorization_score", 0)

        # Higher responsiveness and better categorization are better
        scores["issue"] = responsiveness * 0.7 + categorization * 0.3
    else:
        scores["issue"] = 0

    # Test score
    test = metrics.get("test", {})
    if test:
        has_tests = test.get("has_tests", False)
        practice_score = test.get("testing_practice_score", 0)

        # Having tests and good practices are better
        if has_tests:
            scores["test"] = practice_score
        else:
            scores["test"] = 0
    else:
        scores["test"] = 0

    # Calculate weighted average score
    total_weight = sum(weights.values())
    overall_score = (
        sum(scores.get(category, 0) * weight for category, weight in weights.items()) / total_weight
    )

    return round(overall_score, 1)


def compare_metrics(metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare metrics between two repositories.

    Args:
        metrics1: Metrics for the first repository
        metrics2: Metrics for the second repository

    Returns:
        Dictionary of metric comparisons
    """
    comparison = {}

    # Compare contributor metrics
    comparison["contributor"] = compare_contributor_metrics(
        metrics1.get("contributor", {}), metrics2.get("contributor", {})
    )

    # Compare commit metrics
    comparison["commit"] = compare_commit_metrics(
        metrics1.get("commit", {}), metrics2.get("commit", {})
    )

    # Compare pull request metrics
    comparison["pull_request"] = compare_pr_metrics(
        metrics1.get("pull_request", {}), metrics2.get("pull_request", {})
    )

    # Compare code review metrics
    comparison["code_review"] = compare_code_review_metrics(
        metrics1.get("code_review", {}), metrics2.get("code_review", {})
    )

    # Compare CI/CD metrics
    comparison["ci_cd"] = compare_cicd_metrics(metrics1.get("ci_cd", {}), metrics2.get("ci_cd", {}))

    # Compare issue metrics
    comparison["issue"] = compare_issue_metrics(
        metrics1.get("issue", {}), metrics2.get("issue", {})
    )

    # Compare test metrics
    comparison["test"] = compare_test_metrics(metrics1.get("test", {}), metrics2.get("test", {}))

    # Compare overall health score
    comparison["overall"] = {
        "health_score_difference": metrics1.get("overall_health_score", 0)
        - metrics2.get("overall_health_score", 0)
    }

    return comparison


def compare_contributor_metrics(
    metrics1: Dict[str, Any], metrics2: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare contributor metrics between two repositories.

    Args:
        metrics1: Contributor metrics for the first repository
        metrics2: Contributor metrics for the second repository

    Returns:
        Dictionary of contributor metric comparisons
    """
    return {
        "total_contributors_difference": metrics1.get("total_contributors", 0)
        - metrics2.get("total_contributors", 0),
        "active_contributors_difference": metrics1.get("active_contributors", 0)
        - metrics2.get("active_contributors", 0),
        "bus_factor_difference": metrics1.get("bus_factor", 0) - metrics2.get("bus_factor", 0),
        "contributor_gini_difference": metrics1.get("contributor_gini", 0)
        - metrics2.get("contributor_gini", 0),
    }


def compare_commit_metrics(metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare commit metrics between two repositories.

    Args:
        metrics1: Commit metrics for the first repository
        metrics2: Commit metrics for the second repository

    Returns:
        Dictionary of commit metric comparisons
    """
    return {
        "commits_per_day_difference": metrics1.get("commits_per_day", 0)
        - metrics2.get("commits_per_day", 0),
        "avg_commit_size_difference": metrics1.get("avg_commit_size", 0)
        - metrics2.get("avg_commit_size", 0),
        "quality_score_difference": (
            metrics1.get("commit_message_quality", {}).get("quality_score", 0)
            - metrics2.get("commit_message_quality", {}).get("quality_score", 0)
        ),
        "merge_commit_ratio_difference": (
            metrics1.get("merge_commit_ratio", 0) - metrics2.get("merge_commit_ratio", 0)
        ),
    }


def compare_pr_metrics(metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare pull request metrics between two repositories.

    Args:
        metrics1: Pull request metrics for the first repository
        metrics2: Pull request metrics for the second repository

    Returns:
        Dictionary of pull request metric comparisons
    """
    return {
        "total_prs_difference": metrics1.get("total_prs", 0) - metrics2.get("total_prs", 0),
        "merged_ratio_difference": metrics1.get("merged_ratio", 0)
        - metrics2.get("merged_ratio", 0),
        "avg_time_to_merge_difference": metrics1.get("avg_time_to_merge", 0)
        - metrics2.get("avg_time_to_merge", 0),
        "velocity_score_difference": metrics1.get("pr_velocity_score", 0)
        - metrics2.get("pr_velocity_score", 0),
    }


def compare_code_review_metrics(
    metrics1: Dict[str, Any], metrics2: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare code review metrics between two repositories.

    Args:
        metrics1: Code review metrics for the first repository
        metrics2: Code review metrics for the second repository

    Returns:
        Dictionary of code review metric comparisons
    """
    return {
        "reviews_per_pr_difference": metrics1.get("reviews_per_pr", 0)
        - metrics2.get("reviews_per_pr", 0),
        "comments_per_pr_difference": metrics1.get("comments_per_pr", 0)
        - metrics2.get("comments_per_pr", 0),
        "self_merged_ratio_difference": metrics1.get("self_merged_ratio", 0)
        - metrics2.get("self_merged_ratio", 0),
        "thoroughness_score_difference": metrics1.get("review_thoroughness_score", 0)
        - metrics2.get("review_thoroughness_score", 0),
    }


def compare_cicd_metrics(metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare CI/CD metrics between two repositories.

    Args:
        metrics1: CI/CD metrics for the first repository
        metrics2: CI/CD metrics for the second repository

    Returns:
        Dictionary of CI/CD metric comparisons
    """
    has_ci1 = metrics1.get("has_ci", False)
    has_ci2 = metrics2.get("has_ci", False)

    return {
        "has_ci_difference": (
            1 if has_ci1 and not has_ci2 else (-1 if has_ci2 and not has_ci1 else 0)
        ),
        "workflow_success_rate_difference": metrics1.get("workflow_success_rate", 0)
        - metrics2.get("workflow_success_rate", 0),
        "ci_system_count_difference": metrics1.get("ci_system_count", 0)
        - metrics2.get("ci_system_count", 0),
    }


def compare_issue_metrics(metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare issue metrics between two repositories.

    Args:
        metrics1: Issue metrics for the first repository
        metrics2: Issue metrics for the second repository

    Returns:
        Dictionary of issue metric comparisons
    """
    return {
        "total_issues_difference": metrics1.get("total_issues", 0)
        - metrics2.get("total_issues", 0),
        "responsiveness_score_difference": metrics1.get("responsiveness_score", 0)
        - metrics2.get("responsiveness_score", 0),
        "categorization_score_difference": metrics1.get("categorization_score", 0)
        - metrics2.get("categorization_score", 0),
        "stale_issue_ratio_difference": metrics1.get("stale_issue_ratio", 0)
        - metrics2.get("stale_issue_ratio", 0),
    }


def compare_test_metrics(metrics1: Dict[str, Any], metrics2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare test metrics between two repositories.

    Args:
        metrics1: Test metrics for the first repository
        metrics2: Test metrics for the second repository

    Returns:
        Dictionary of test metric comparisons
    """
    has_tests1 = metrics1.get("has_tests", False)
    has_tests2 = metrics2.get("has_tests", False)

    return {
        "has_tests_difference": (
            1 if has_tests1 and not has_tests2 else (-1 if has_tests2 and not has_tests1 else 0)
        ),
        "test_files_count_difference": metrics1.get("test_files_count", 0)
        - metrics2.get("test_files_count", 0),
        "testing_practice_score_difference": metrics1.get("testing_practice_score", 0)
        - metrics2.get("testing_practice_score", 0),
    }
