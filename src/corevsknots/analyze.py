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

CORE_REPO_IDENTIFIER = "bitcoin/bitcoin"
KNOTS_REPO_IDENTIFIER = "bitcoinknots/bitcoin"

def get_core_commit_shas_for_period(months: int, github_token: Optional[str], use_cache: bool) -> set[str]:
    """Helper to fetch commit SHAs for Bitcoin Core for a given period."""
    logger.info(f"Fetching Bitcoin Core commit SHAs for the last {months} months for fork comparison...")
    core_client = GitHubAPIClient(token=github_token, use_cache=use_cache)
    since_date = months_ago(months)
    since = format_date(since_date)
    core_commits_data = core_client.get_commits(CORE_REPO_IDENTIFIER, since=since)
    core_shas = {commit['sha'] for commit in core_commits_data if 'sha' in commit}
    logger.info(f"Fetched {len(core_shas)} unique Bitcoin Core commit SHAs for comparison period.")
    return core_shas

def analyze_repository(
    repo: str,
    months: int = 12,
    github_token: Optional[str] = None,
    local_path: Optional[str] = None,
    use_cache: bool = True,
    # New parameter to pass Core's commit SHAs if analyzing Knots
    core_commit_shas_for_knots: Optional[set[str]] = None
) -> Dict[str, Any]:
    """
    Analyze a GitHub repository.

    Args:
        repo: Repository name (e.g., 'bitcoin/bitcoin')
        months: Number of months to analyze
        github_token: GitHub personal access token
        local_path: Path to local repository clone
        use_cache: Whether to use cache for API responses
        core_commit_shas_for_knots: Set of commit SHAs for Bitcoin Core if analyzing Knots

    Returns:
        Dictionary of repository metrics
    """
    logger.info(f"Starting analysis for repository: {repo} (last {months} months)")

    # Initialize GitHub API client
    logger.info("Initializing GitHub API client...")
    github_client = GitHubAPIClient(token=github_token, use_cache=use_cache)

    # Fetch data from GitHub API
    since_date = months_ago(months)
    since = format_date(since_date)

    logger.info(f"Fetching GitHub data since: {since} for {repo}...")
    github_data = github_client.get_repository_metrics(repo, months)
    default_branch = github_data.get("repo_info", {}).get("default_branch")
    logger.info(f"[{repo}] Determined default branch from GitHub API: {default_branch}")
    logger.info(f"GitHub data fetching complete for {repo}.")

    # Initialize Git CLI client if local path is provided
    git_data = None
    if local_path:
        logger.info(f"Analyzing local repository at: {local_path} for {repo}...")
        try:
            git_client = GitCLI(repo_path=local_path, default_branch_hint=default_branch)
            git_data = git_client.get_repository_metrics(months)
            logger.info(f"Local git analysis complete for {repo} at {local_path}.")
        except Exception as e:
            logger.error(f"Failed to analyze local repository at {local_path} for {repo}: {e}")
    else:
        try:
            logger.info(f"Attempting temporary clone of repository {repo}...")
            repo_url = f"https://github.com/{repo}.git"
            git_client = GitCLI(clone_url=repo_url, default_branch_hint=default_branch)
            git_data = git_client.get_repository_metrics(months)
            logger.info(f"Temporary clone and local git analysis complete for {repo}.")
        except Exception as e:
            logger.error(f"Failed to clone and analyze repository {repo}: {e}")

    logger.info(f"Calculating all metrics for {repo}...")
    # Pass core_commit_shas_for_knots if this is the Knots repo
    metrics = calculate_all_metrics(
        github_data,
        git_data,
        repo_name_for_logging=repo,
        core_commit_shas=(core_commit_shas_for_knots if repo == KNOTS_REPO_IDENTIFIER else None),
        github_client_instance=github_client
    )
    logger.info(f"All metrics calculation complete for {repo}.")

    # Add repository metadata
    logger.debug(f"Adding repository metadata for {repo}...")
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
    logger.debug(f"Calculating overall health score for {repo}...")
    metrics["overall_health_score"] = calculate_overall_health_score(metrics, repo_name=repo)

    logger.info(f"Analysis complete for repository: {repo}")
    return metrics


def compare_repositories(
    repo1: str,
    repo2: str,
    months: int = 12,
    github_token: Optional[str] = None,
    local_path1: Optional[str] = None,
    local_path2: Optional[str] = None,
    use_cache: bool = True,
    is_fight_mode: bool = False
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
        is_fight_mode: Whether to apply special Core vs Knots comparison logic

    Returns:
        Dictionary containing metrics for both repositories
    """
    logger.info(f"Comparing repositories: {repo1} vs {repo2}{' (FIGHT MODE!)' if is_fight_mode else ''}")

    core_shas_for_knots_comparison: Optional[set[str]] = None
    if is_fight_mode or (repo1 == CORE_REPO_IDENTIFIER and repo2 == KNOTS_REPO_IDENTIFIER):
        core_shas_for_knots_comparison = get_core_commit_shas_for_period(months, github_token, use_cache)

    metrics1 = analyze_repository(repo1, months, github_token, local_path1, use_cache,
                                  core_commit_shas_for_knots=(core_shas_for_knots_comparison if repo1 == KNOTS_REPO_IDENTIFIER else None))
    metrics2 = analyze_repository(repo2, months, github_token, local_path2, use_cache,
                                  core_commit_shas_for_knots=(core_shas_for_knots_comparison if repo2 == KNOTS_REPO_IDENTIFIER else None))

    # Structure the comparison result
    comparison = {
        "repo1": {"name": repo1, "metrics": metrics1},
        "repo2": {"name": repo2, "metrics": metrics2},
        "comparison": compare_metrics(metrics1, metrics2, is_fight_mode, repo1_name=repo1, repo2_name=repo2),
        "analysis_metadata": {
            "date": datetime.now().isoformat(),
            "period_months": months,
            "is_fight_mode": is_fight_mode
        },
    }

    return comparison


def calculate_all_metrics(
    github_data: Dict[str, Any],
    git_data: Optional[Dict[str, Any]] = None,
    repo_name_for_logging: str = "unknown_repo",
    core_commit_shas: Optional[set[str]] = None,
    github_client_instance: Optional[GitHubAPIClient] = None
) -> Dict[str, Any]:
    """
    Calculate all repository metrics.

    Args:
        github_data: Repository data fetched from GitHub API
        git_data: Repository data fetched from Git CLI (optional)
        repo_name_for_logging: Name of the repository for logging purposes
        core_commit_shas: Set of commit SHAs for Bitcoin Core if analyzing Knots
        github_client_instance: GitHubAPIClient instance for passing to calculate_code_review_metrics

    Returns:
        Dictionary of all repository metrics
    """
    metrics = {}
    logger.info(f"[{repo_name_for_logging}] Starting calculation of all metrics.")

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
    logger.info(f"[{repo_name_for_logging}] Calculating contributor metrics...")
    try:
        metrics["contributor"] = calculate_contributor_metrics(github_data, git_data,
                                                              repo_name=repo_name_for_logging,
                                                              core_commit_shas=core_commit_shas)
        logger.info(f"[{repo_name_for_logging}] Contributor metrics calculated.")
    except Exception as e:
        logger.error(f"[{repo_name_for_logging}] Failed to calculate contributor metrics: {e}")
        metrics["contributor"] = {}

    # Calculate commit metrics
    logger.info(f"[{repo_name_for_logging}] Calculating commit metrics...")
    try:
        metrics["commit"] = calculate_commit_metrics(github_data, git_data,
                                                     repo_name=repo_name_for_logging,
                                                     core_commit_shas=core_commit_shas)
        logger.info(f"[{repo_name_for_logging}] Commit metrics calculated.")
    except Exception as e:
        logger.error(f"[{repo_name_for_logging}] Failed to calculate commit metrics: {e}")
        metrics["commit"] = {}

    # Calculate pull request metrics
    logger.info(f"[{repo_name_for_logging}] Calculating pull request metrics...")
    try:
        metrics["pull_request"] = calculate_pr_metrics(github_data)
        logger.info(f"[{repo_name_for_logging}] Pull request metrics calculated.")
    except Exception as e:
        logger.error(f"[{repo_name_for_logging}] Failed to calculate pull request metrics: {e}")
        metrics["pull_request"] = {}

    # Calculate code review metrics
    logger.info(f"[{repo_name_for_logging}] Calculating code review metrics...")
    try:
        metrics["code_review"] = calculate_code_review_metrics(
                                    github_data,
                                    repo_name=repo_name_for_logging,
                                    github_client=github_client_instance
                                )
        logger.info(f"[{repo_name_for_logging}] Code review metrics calculated.")
    except Exception as e:
        logger.error(f"[{repo_name_for_logging}] Failed to calculate code review metrics: {e}")
        metrics["code_review"] = {}

    # Calculate CI/CD metrics
    logger.info(f"[{repo_name_for_logging}] Calculating CI/CD metrics...")
    try:
        metrics["ci_cd"] = calculate_cicd_metrics(github_data, git_data)
        logger.info(f"[{repo_name_for_logging}] CI/CD metrics calculated.")
    except Exception as e:
        logger.error(f"[{repo_name_for_logging}] Failed to calculate CI/CD metrics: {e}")
        metrics["ci_cd"] = {}

    # Calculate issue metrics
    logger.info(f"[{repo_name_for_logging}] Calculating issue metrics...")
    try:
        metrics["issue"] = calculate_issue_metrics(github_data)
        logger.info(f"[{repo_name_for_logging}] Issue metrics calculated.")
    except Exception as e:
        logger.error(f"[{repo_name_for_logging}] Failed to calculate issue metrics: {e}")
        metrics["issue"] = {}

    # Calculate test metrics
    logger.info(f"[{repo_name_for_logging}] Calculating test metrics...")
    try:
        metrics["test"] = calculate_test_metrics(github_data, git_data)
        logger.info(f"[{repo_name_for_logging}] Test metrics calculated.")
    except Exception as e:
        logger.error(f"[{repo_name_for_logging}] Failed to calculate test metrics: {e}")
        metrics["test"] = {}

    logger.info(f"[{repo_name_for_logging}] Finished calculation of all metrics.")
    return metrics


def calculate_overall_health_score(metrics: Dict[str, Any], repo_name: Optional[str] = None) -> float:
    """Calculate an overall repository health score."""
    is_knots_fight_mode = repo_name == KNOTS_REPO_IDENTIFIER and metrics.get("analysis_metadata", {}).get("is_fight_mode", False)
    # Or, more simply, if knots_original_bus_factor exists, it implies we are in a fight and this is Knots
    is_knots_with_original_metrics = repo_name == KNOTS_REPO_IDENTIFIER and "knots_original_bus_factor" in metrics.get("contributor", {})

    weights = {
        "contributor": 0.3,
        "commit": 0.15,
        "pull_request": 0.15,
        "code_review": 0.25,
        "ci_cd": 0.05,
        "issue": 0.05,
        "test": 0.05,
    }

    scores = {}

    contributor_metrics = metrics.get("contributor", {})
    if contributor_metrics:
        bus_factor = contributor_metrics.get("knots_original_bus_factor") if is_knots_with_original_metrics else contributor_metrics.get("bus_factor", 1)
        contributor_count = contributor_metrics.get("total_contributors", 0)

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

    commit_metrics = metrics.get("commit", {})
    if commit_metrics:
        commit_frequency = commit_metrics.get("commit_frequency", "inactive")
        commit_message_quality = commit_metrics.get("commit_message_quality", {}).get("quality_score", 0)

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

    pr = metrics.get("pull_request", {})
    if pr:
        merged_ratio = pr.get("merged_ratio", 0)
        pr_velocity = pr.get("pr_velocity_score", 0)

        # Higher merged ratio and faster PR velocity are better
        scores["pull_request"] = merged_ratio * 10 * 0.5 + pr_velocity * 0.5
    else:
        scores["pull_request"] = 0

    review = metrics.get("code_review", {})
    if review:
        review_thoroughness = review.get("review_thoroughness_score", 0)
        self_merged_ratio = review.get("self_merged_ratio", 1)

        # Higher thoroughness and lower self-merge ratio are better
        scores["code_review"] = review_thoroughness * 0.7 + (1 - self_merged_ratio) * 10 * 0.3
    else:
        scores["code_review"] = 0

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

    issue = metrics.get("issue", {})
    if issue:
        responsiveness = issue.get("responsiveness_score", 0)
        categorization = issue.get("categorization_score", 0)

        # Higher responsiveness and better categorization are better
        scores["issue"] = responsiveness * 0.7 + categorization * 0.3
    else:
        scores["issue"] = 0

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


def compare_metrics(metrics1: Dict[str, Any], metrics2: Dict[str, Any], is_fight_mode: bool = False, repo1_name: Optional[str] = None, repo2_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Compare metrics between two repositories.

    Args:
        metrics1: Metrics for the first repository
        metrics2: Metrics for the second repository
        is_fight_mode: Whether to apply special Core vs Knots comparison logic
        repo1_name: Name of the first repository
        repo2_name: Name of the second repository

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

    # If it's a fight, potentially add specific Core vs Knots comparison logic here or in sub-functions
    if is_fight_mode and repo1_name == "bitcoin/bitcoin" and repo2_name == "bitcoinknots/bitcoin":
        logger.info("Applying special Core vs Knots comparison logic...")
        # Example: Adjust contributor comparison if we have more data
        # comparison["contributor"] = compare_contributor_metrics_fork_aware(
        #     metrics1.get("contributor", {}),
        #     metrics2.get("contributor", {}),
        #     github_data1=metrics1.get("_raw_github_data"), # Hypothetical raw data access
        #     github_data2=metrics2.get("_raw_github_data")
        # )
        pass # Placeholder for now

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
