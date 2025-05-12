"""
CI/CD workflows analysis metrics.

This module calculates metrics related to Continuous Integration and
Continuous Deployment workflows and practices.
"""

import re
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)


def calculate_cicd_metrics(
    github_data: Dict[str, Any], git_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Calculate CI/CD related metrics from GitHub API data and Git CLI data.

    Args:
        github_data: Repository data fetched from GitHub API
        git_data: Repository data fetched from Git CLI (optional)

    Returns:
        Dictionary of CI/CD metrics
    """
    metrics = {}

    # Extract workflow runs
    workflow_runs = github_data.get("workflow_runs", [])

    # Basic metrics
    metrics["has_ci"] = bool(workflow_runs) or has_ci_configs(git_data)

    # If no CI/CD detected, return limited metrics
    if not metrics["has_ci"]:
        logger.warning("No CI/CD detected in the repository")
        return metrics

    # Workflow metrics
    metrics.update(analyze_workflow_runs(workflow_runs))

    # CI configuration metrics
    metrics.update(analyze_ci_configs(git_data))

    # PR-CI integration metrics
    metrics.update(analyze_pr_ci_integration(github_data, workflow_runs))

    return metrics


def has_ci_configs(git_data: Optional[Dict[str, Any]] = None) -> bool:
    """
    Check if repository has CI configuration files.

    Args:
        git_data: Repository data fetched from Git CLI

    Returns:
        True if CI configuration files are detected, False otherwise
    """
    if not git_data:
        return False

    ci_config_files = git_data.get("ci_config_files", [])
    return len(ci_config_files) > 0


def analyze_workflow_runs(workflow_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze GitHub Actions workflow runs.

    Args:
        workflow_runs: List of workflow runs

    Returns:
        Dictionary of workflow run metrics
    """
    if not workflow_runs:
        return {"total_workflow_runs": 0, "workflow_success_rate": 0, "workflows_per_day": 0}

    # Count runs and successes
    total_runs = len(workflow_runs)
    successful_runs = sum(1 for run in workflow_runs if run.get("conclusion") == "success")

    # Calculate success rate
    success_rate = successful_runs / total_runs if total_runs > 0 else 0

    # Calculate average workflows per day
    # (This is a rough approximation as we don't have the full timeline)
    if total_runs >= 2:
        first_run = min(workflow_runs, key=lambda r: r.get("created_at", ""))
        last_run = max(workflow_runs, key=lambda r: r.get("created_at", ""))

        if "created_at" in first_run and "created_at" in last_run:
            from ..utils.time_utils import parse_date

            first_date = parse_date(first_run["created_at"])
            last_date = parse_date(last_run["created_at"])

            days_diff = (last_date - first_date).days + 1  # Add 1 to include both days
            workflows_per_day = total_runs / days_diff if days_diff > 0 else total_runs
        else:
            workflows_per_day = 0
    else:
        workflows_per_day = total_runs  # If only 1 run, assume 1 per day

    # Count unique workflow names
    workflow_names = set(run.get("name", "") for run in workflow_runs)
    unique_workflows = len(workflow_names)

    return {
        "total_workflow_runs": total_runs,
        "successful_workflow_runs": successful_runs,
        "workflow_success_rate": round(success_rate, 3),
        "workflows_per_day": round(workflows_per_day, 2),
        "unique_workflows": unique_workflows,
    }


def analyze_ci_configs(git_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze CI/CD configuration files.

    Args:
        git_data: Repository data fetched from Git CLI

    Returns:
        Dictionary of CI/CD configuration metrics
    """
    if not git_data or "ci_config_files" not in git_data:
        return {
            "ci_config_count": 0,
            "ci_systems": [],
            "has_github_actions": False,
            "has_travis": False,
            "has_circle_ci": False,
        }

    ci_config_files = git_data.get("ci_config_files", [])

    # Identify CI systems
    ci_systems = set()
    has_github_actions = any(f.startswith(".github/workflows/") for f in ci_config_files)
    has_travis = any(f == ".travis.yml" for f in ci_config_files)
    has_circle_ci = any(f == ".circleci/config.yml" for f in ci_config_files)
    has_gitlab_ci = any(f == ".gitlab-ci.yml" for f in ci_config_files)
    has_jenkins = any(f == "Jenkinsfile" for f in ci_config_files)
    has_azure = any(f == "azure-pipelines.yml" for f in ci_config_files)

    if has_github_actions:
        ci_systems.add("GitHub Actions")
    if has_travis:
        ci_systems.add("Travis CI")
    if has_circle_ci:
        ci_systems.add("CircleCI")
    if has_gitlab_ci:
        ci_systems.add("GitLab CI")
    if has_jenkins:
        ci_systems.add("Jenkins")
    if has_azure:
        ci_systems.add("Azure Pipelines")

    return {
        "ci_config_count": len(ci_config_files),
        "ci_systems": list(ci_systems),
        "has_github_actions": has_github_actions,
        "has_travis": has_travis,
        "has_circle_ci": has_circle_ci,
        "ci_system_count": len(ci_systems),
    }


def analyze_pr_ci_integration(
    github_data: Dict[str, Any], workflow_runs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyze integration between pull requests and CI.

    Args:
        github_data: Repository data fetched from GitHub API
        workflow_runs: List of workflow runs

    Returns:
        Dictionary of PR-CI integration metrics
    """
    pull_requests = github_data.get("pull_requests", [])

    if not pull_requests or not workflow_runs:
        return {"pr_ci_ratio": 0, "pr_ci_required": False}

    # Count PRs with associated CI runs (approximate)
    pr_with_ci = 0

    # Check if repository has CI status checks for PRs (implied if workflow_runs exist)
    pr_ci_required = bool(workflow_runs)

    # Try to match PRs with workflow runs
    pr_workflow_mapping = {}

    for run in workflow_runs:
        # Check if run is associated with a PR
        if run.get("event") == "pull_request":
            # Extract PR number from head branch (e.g., 'refs/pull/123/merge')
            head_branch = run.get("head_branch", "")
            pr_match = re.search(r"refs/pull/(\d+)", head_branch)

            if pr_match:
                pr_number = int(pr_match.group(1))
                pr_workflow_mapping[pr_number] = pr_workflow_mapping.get(pr_number, 0) + 1

    # Count PRs with associated workflow runs
    for pr in pull_requests:
        pr_number = pr.get("number")
        if pr_number in pr_workflow_mapping:
            pr_with_ci += 1

    # Calculate metrics
    pr_ci_ratio = pr_with_ci / len(pull_requests) if pull_requests else 0

    return {"pr_ci_ratio": round(pr_ci_ratio, 3), "pr_ci_required": pr_ci_required}


def analyze_ci_script_quality(git_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze the quality and coverage of CI scripts.

    Note: This would require analyzing the content of CI configuration files,
    which is beyond the scope of the current implementation.

    Args:
        git_data: Repository data fetched from Git CLI

    Returns:
        Dictionary of CI script quality metrics
    """
    # Placeholder for future implementation
    return {"ci_quality_score": None}
