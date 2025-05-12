"""
Chart generator for repository metrics.

This module generates charts and visualizations for repository metrics.
"""

import os
from typing import Any, Dict

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from ..utils.logger import get_logger

logger = get_logger(__name__)


def generate_charts(metrics: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generate charts for repository metrics.

    Args:
        metrics: Repository metrics
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    # Create output directory if it doesn't exist
    charts_dir = os.path.join(output_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    charts = {}

    # Generate contributor charts
    if "contributor" in metrics:
        contributor_charts = generate_contributor_charts(metrics["contributor"], charts_dir)
        charts.update(contributor_charts)

    # Generate commit charts
    if "commit" in metrics:
        commit_charts = generate_commit_charts(metrics["commit"], charts_dir)
        charts.update(commit_charts)

    # Generate pull request charts
    if "pull_request" in metrics:
        pr_charts = generate_pr_charts(metrics["pull_request"], charts_dir)
        charts.update(pr_charts)

    # Generate code review charts
    if "code_review" in metrics:
        review_charts = generate_review_charts(metrics["code_review"], charts_dir)
        charts.update(review_charts)

    # Generate CI/CD charts
    if "ci_cd" in metrics:
        cicd_charts = generate_cicd_charts(metrics["ci_cd"], charts_dir)
        charts.update(cicd_charts)

    # Generate issue charts
    if "issue" in metrics:
        issue_charts = generate_issue_charts(metrics["issue"], charts_dir)
        charts.update(issue_charts)

    # Generate overall health chart
    if "overall_health_score" in metrics:
        health_chart = generate_health_chart(metrics, charts_dir)
        charts.update(health_chart)

    return charts


def generate_comparison_charts(comparison: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generate charts comparing two repositories.

    Args:
        comparison: Repository comparison data
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    # Create output directory if it doesn't exist
    charts_dir = os.path.join(output_dir, "charts")
    os.makedirs(charts_dir, exist_ok=True)

    charts = {}

    # Extract repository names
    repo1_name = comparison["repo1"]["name"]
    repo2_name = comparison["repo2"]["name"]

    # Generate contributor comparison chart
    charts.update(
        generate_contributor_comparison_chart(
            comparison["repo1"]["metrics"].get("contributor", {}),
            comparison["repo2"]["metrics"].get("contributor", {}),
            repo1_name,
            repo2_name,
            charts_dir,
        )
    )

    # Generate commit comparison chart
    charts.update(
        generate_commit_comparison_chart(
            comparison["repo1"]["metrics"].get("commit", {}),
            comparison["repo2"]["metrics"].get("commit", {}),
            repo1_name,
            repo2_name,
            charts_dir,
        )
    )

    # Generate pull request comparison chart
    charts.update(
        generate_pr_comparison_chart(
            comparison["repo1"]["metrics"].get("pull_request", {}),
            comparison["repo2"]["metrics"].get("pull_request", {}),
            repo1_name,
            repo2_name,
            charts_dir,
        )
    )

    # Generate code review comparison chart
    charts.update(
        generate_review_comparison_chart(
            comparison["repo1"]["metrics"].get("code_review", {}),
            comparison["repo2"]["metrics"].get("code_review", {}),
            repo1_name,
            repo2_name,
            charts_dir,
        )
    )

    # Generate overall health comparison chart
    charts.update(
        generate_health_comparison_chart(
            comparison["repo1"]["metrics"].get("overall_health_score", 0),
            comparison["repo2"]["metrics"].get("overall_health_score", 0),
            repo1_name,
            repo2_name,
            charts_dir,
        )
    )

    # Generate category comparison chart
    charts.update(
        generate_category_comparison_chart(
            comparison["repo1"]["metrics"],
            comparison["repo2"]["metrics"],
            repo1_name,
            repo2_name,
            charts_dir,
        )
    )

    return charts


def generate_contributor_charts(metrics: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generate charts for contributor metrics.

    Args:
        metrics: Contributor metrics
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # Top contributors chart
    if "contributors_by_commits" in metrics and metrics["contributors_by_commits"]:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            top_contributors = metrics["contributors_by_commits"][:10]
            names = [contributor[0] for contributor in top_contributors]
            commits = [contributor[1] for contributor in top_contributors]

            ax.barh(names, commits, color="skyblue")
            ax.set_xlabel("Number of Commits")
            ax.set_ylabel("Contributor")
            ax.set_title("Top 10 Contributors by Commits")

            # Add count labels
            for i, v in enumerate(commits):
                ax.text(v + 5, i, str(v), va="center")

            plt.tight_layout()

            # Save chart
            chart_path = os.path.join(output_dir, "top_contributors.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["top_contributors"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate top contributors chart: {e}")

    # Bus factor chart
    if "bus_factor" in metrics:
        try:
            fig, ax = plt.subplots(figsize=(8, 6))

            bus_factor = metrics["bus_factor"]
            total_contributors = metrics["total_contributors"]

            # Create gauge chart
            bus_factor_ratio = (
                min(1.0, bus_factor / total_contributors) if total_contributors > 0 else 0
            )

            # Create a colormap
            cmap = plt.cm.RdYlGn
            # colors = cmap(np.linspace(0, 1, 100)) # F841: Unused

            # Create gauge chart
            # gauge = plt.pie( # F841: Unused
            plt.pie(
                [bus_factor_ratio, 1 - bus_factor_ratio],
                colors=[cmap(int(bus_factor_ratio * 100)), "whitesmoke"],
                startangle=90,
                counterclock=False,
                wedgeprops={"width": 0.3, "edgecolor": "white"},
            )

            plt.annotate(
                f"Bus Factor: {bus_factor}", xy=(0, 0), ha="center", va="center", fontsize=16
            )

            plt.annotate(
                f"Out of {total_contributors} contributors",
                xy=(0, -0.2),
                ha="center",
                va="center",
                fontsize=12,
            )

            plt.title("Bus Factor", fontsize=14)

            # Save chart
            chart_path = os.path.join(output_dir, "bus_factor.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["bus_factor"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate bus factor chart: {e}")

    return charts


def generate_commit_charts(metrics: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generate charts for commit metrics.

    Args:
        metrics: Commit metrics
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # Commit activity by day of week
    if "commits_by_day" in metrics and metrics["commits_by_day"]:
        try:
            fig, ax = plt.subplots(figsize=(10, 6))

            days = list(metrics["commits_by_day"].keys())
            commits = list(metrics["commits_by_day"].values())

            ax.bar(days, commits, color="lightgreen")
            ax.set_xlabel("Day of Week")
            ax.set_ylabel("Number of Commits")
            ax.set_title("Commit Activity by Day of Week")

            plt.tight_layout()

            # Save chart
            chart_path = os.path.join(output_dir, "commits_by_day.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["commits_by_day"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate commits by day chart: {e}")

    # Commit activity by hour
    if "commits_by_hour" in metrics and metrics["commits_by_hour"]:
        try:
            fig, ax = plt.subplots(figsize=(12, 6))

            hours = [int(hour) for hour in metrics["commits_by_hour"].keys()]
            commits = list(metrics["commits_by_hour"].values())

            # Sort by hour
            hour_commits = sorted(zip(hours, commits))
            hours, commits = zip(*hour_commits) if hour_commits else ([], [])

            ax.bar(hours, commits, color="lightblue")
            ax.set_xlabel("Hour of Day (UTC)")
            ax.set_ylabel("Number of Commits")
            ax.set_title("Commit Activity by Hour of Day")
            ax.set_xticks(range(0, 24, 2))

            plt.tight_layout()

            # Save chart
            chart_path = os.path.join(output_dir, "commits_by_hour.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["commits_by_hour"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate commits by hour chart: {e}")

    # Commit message quality
    if "commit_message_quality" in metrics:
        try:
            quality_metrics = metrics["commit_message_quality"]

            fig, ax = plt.subplots(figsize=(8, 6))

            quality_score = quality_metrics.get("quality_score", 0)

            # Create gauge chart
            # gauge = plt.pie( # F841: Unused
            plt.pie(
                [quality_score / 10, 1 - quality_score / 10],
                colors=[
                    (
                        "#4CAF50"
                        if quality_score >= 7
                        else "#FFC107" if quality_score >= 4 else "#F44336"
                    ),
                    "whitesmoke",
                ],
                startangle=90,
                counterclock=False,
                wedgeprops={"width": 0.3, "edgecolor": "white"},
            )

            plt.annotate(f"{quality_score}/10", xy=(0, 0), ha="center", va="center", fontsize=20)

            plt.title("Commit Message Quality Score", fontsize=14)

            # Save chart
            chart_path = os.path.join(output_dir, "commit_message_quality.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["commit_message_quality"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate commit message quality chart: {e}")

    return charts


def generate_pr_charts(metrics: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generate charts for pull request metrics.

    Args:
        metrics: Pull request metrics
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # PR state distribution
    try:
        fig, ax = plt.subplots(figsize=(8, 8))

        open_prs = metrics.get("open_prs", 0)
        merged_prs = metrics.get("merged_prs", 0)
        closed_unmerged = metrics.get("closed_prs", 0) - merged_prs

        # Create pie chart
        labels = ["Open", "Merged", "Closed (Unmerged)"]
        sizes = [open_prs, merged_prs, closed_unmerged]
        colors = ["#FFC107", "#4CAF50", "#F44336"]

        # Only include non-zero segments
        non_zero_labels = []
        non_zero_sizes = []
        non_zero_colors = []

        for label, size, color in zip(labels, sizes, colors):
            if size > 0:
                non_zero_labels.append(label)
                non_zero_sizes.append(size)
                non_zero_colors.append(color)

        if non_zero_sizes:
            wedges, texts, autotexts = ax.pie(
                non_zero_sizes,
                labels=non_zero_labels,
                colors=non_zero_colors,
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"edgecolor": "white"},
            )

            # Make text more readable
            for text in texts:
                text.set_fontsize(12)
            for autotext in autotexts:
                autotext.set_fontsize(12)
                autotext.set_color("white")

            ax.set_title("Pull Request State Distribution", fontsize=14)

            # Save chart
            chart_path = os.path.join(output_dir, "pr_state_distribution.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["pr_state_distribution"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate PR state distribution chart: {e}")

    # PR velocity
    if "avg_time_to_merge" in metrics:
        try:
            fig, ax = plt.subplots(figsize=(8, 6))

            avg_time = metrics["avg_time_to_merge"]
            velocity_score = metrics.get("pr_velocity_score", 0)

            # Create gauge chart for PR velocity
            # gauge = plt.pie( # F841: Unused
            plt.pie(
                [velocity_score / 10, 1 - velocity_score / 10],
                colors=[
                    (
                        "#4CAF50"
                        if velocity_score >= 7
                        else "#FFC107" if velocity_score >= 4 else "#F44336"
                    ),
                    "whitesmoke",
                ],
                startangle=90,
                counterclock=False,
                wedgeprops={"width": 0.3, "edgecolor": "white"},
            )

            # Convert hours to a human-readable format
            if avg_time < 24:
                time_str = f"{avg_time:.1f} hours"
            elif avg_time < 168:  # 7 days
                time_str = f"{avg_time / 24:.1f} days"
            else:
                time_str = f"{avg_time / 168:.1f} weeks"

            plt.annotate(f"{velocity_score}/10", xy=(0, 0.1), ha="center", va="center", fontsize=20)

            plt.annotate(f"Avg: {time_str}", xy=(0, -0.1), ha="center", va="center", fontsize=12)

            plt.title("Pull Request Velocity", fontsize=14)

            # Save chart
            chart_path = os.path.join(output_dir, "pr_velocity.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["pr_velocity"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate PR velocity chart: {e}")

    return charts


def generate_review_charts(metrics: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generate charts for code review metrics.

    Args:
        metrics: Code review metrics
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # Review thoroughness
    if "review_thoroughness_score" in metrics:
        try:
            fig, ax = plt.subplots(figsize=(8, 6))

            thoroughness_score = metrics["review_thoroughness_score"]

            # Create gauge chart
            # gauge = plt.pie( # F841: Unused
            plt.pie(
                [thoroughness_score / 10, 1 - thoroughness_score / 10],
                colors=[
                    (
                        "#4CAF50"
                        if thoroughness_score >= 7
                        else "#FFC107" if thoroughness_score >= 4 else "#F44336"
                    ),
                    "whitesmoke",
                ],
                startangle=90,
                counterclock=False,
                wedgeprops={"width": 0.3, "edgecolor": "white"},
            )

            plt.annotate(
                f"{thoroughness_score}/10", xy=(0, 0), ha="center", va="center", fontsize=20
            )

            plt.title("Code Review Thoroughness", fontsize=14)

            # Save chart
            chart_path = os.path.join(output_dir, "review_thoroughness.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["review_thoroughness"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate review thoroughness chart: {e}")

    # Self-merge ratio
    if "self_merged_ratio" in metrics:
        try:
            fig, ax = plt.subplots(figsize=(8, 6))

            self_merged_ratio = metrics["self_merged_ratio"]
            independent_review_ratio = 1 - self_merged_ratio

            # Create gauge chart
            colors = [
                (
                    "#4CAF50"
                    if independent_review_ratio > 0.8
                    else "#FFC107" if independent_review_ratio > 0.5 else "#F44336"
                ),
                "whitesmoke",
            ]

            # gauge = plt.pie( # F841: Unused
            plt.pie(
                [independent_review_ratio, self_merged_ratio],
                colors=colors,
                startangle=90,
                counterclock=False,
                wedgeprops={"width": 0.3, "edgecolor": "white"},
            )

            plt.annotate(
                f"{independent_review_ratio:.1%}",
                xy=(0, 0.1),
                ha="center",
                va="center",
                fontsize=20,
            )

            plt.annotate(
                "PRs with independent review", xy=(0, -0.1), ha="center", va="center", fontsize=12
            )

            plt.title("Independent Code Review Rate", fontsize=14)

            # Save chart
            chart_path = os.path.join(output_dir, "independent_review_rate.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["independent_review_rate"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate independent review rate chart: {e}")

    return charts


def generate_cicd_charts(metrics: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generate charts for CI/CD metrics.

    Args:
        metrics: CI/CD metrics
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # CI success rate
    if "workflow_success_rate" in metrics:
        try:
            fig, ax = plt.subplots(figsize=(8, 6))

            success_rate = metrics["workflow_success_rate"]

            # Create gauge chart
            # gauge = plt.pie( # F841: Unused
            plt.pie(
                [success_rate, 1 - success_rate],
                colors=[
                    (
                        "#4CAF50"
                        if success_rate > 0.8
                        else "#FFC107" if success_rate > 0.6 else "#F44336"
                    ),
                    "whitesmoke",
                ],
                startangle=90,
                counterclock=False,
                wedgeprops={"width": 0.3, "edgecolor": "white"},
            )

            plt.annotate(f"{success_rate:.1%}", xy=(0, 0), ha="center", va="center", fontsize=20)

            plt.title("CI Workflow Success Rate", fontsize=14)

            # Save chart
            chart_path = os.path.join(output_dir, "ci_success_rate.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["ci_success_rate"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate CI success rate chart: {e}")

    return charts


def generate_issue_charts(metrics: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generate charts for issue metrics.

    Args:
        metrics: Issue metrics
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # Issue state distribution
    try:
        fig, ax = plt.subplots(figsize=(8, 8))

        open_issues = metrics.get("open_issues", 0)
        closed_issues = metrics.get("closed_issues", 0)

        # Create pie chart
        labels = ["Open", "Closed"]
        sizes = [open_issues, closed_issues]
        colors = ["#FFC107", "#4CAF50"]

        # Only include non-zero segments
        non_zero_labels = []
        non_zero_sizes = []
        non_zero_colors = []

        for label, size, color in zip(labels, sizes, colors):
            if size > 0:
                non_zero_labels.append(label)
                non_zero_sizes.append(size)
                non_zero_colors.append(color)

        if non_zero_sizes:
            wedges, texts, autotexts = ax.pie(
                non_zero_sizes,
                labels=non_zero_labels,
                colors=non_zero_colors,
                autopct="%1.1f%%",
                startangle=90,
                wedgeprops={"edgecolor": "white"},
            )

            # Make text more readable
            for text in texts:
                text.set_fontsize(12)
            for autotext in autotexts:
                autotext.set_fontsize(12)
                autotext.set_color("white")

            ax.set_title("Issue State Distribution", fontsize=14)

            # Save chart
            chart_path = os.path.join(output_dir, "issue_state_distribution.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["issue_state_distribution"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate issue state distribution chart: {e}")

    # Issue responsiveness
    if "responsiveness_score" in metrics:
        try:
            fig, ax = plt.subplots(figsize=(8, 6))

            responsiveness_score = metrics["responsiveness_score"]

            # Create gauge chart
            # gauge = plt.pie( # F841: Unused
            plt.pie(
                [responsiveness_score / 10, 1 - responsiveness_score / 10],
                colors=[
                    (
                        "#4CAF50"
                        if responsiveness_score >= 7
                        else "#FFC107" if responsiveness_score >= 4 else "#F44336"
                    ),
                    "whitesmoke",
                ],
                startangle=90,
                counterclock=False,
                wedgeprops={"width": 0.3, "edgecolor": "white"},
            )

            plt.annotate(
                f"{responsiveness_score}/10", xy=(0, 0), ha="center", va="center", fontsize=20
            )

            plt.title("Issue Responsiveness Score", fontsize=14)

            # Save chart
            chart_path = os.path.join(output_dir, "issue_responsiveness.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["issue_responsiveness"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate issue responsiveness chart: {e}")

    return charts


def generate_health_chart(metrics: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """
    Generate chart for overall repository health.

    Args:
        metrics: Repository metrics
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # Overall health score
    if "overall_health_score" in metrics:
        try:
            fig, ax = plt.subplots(figsize=(8, 8))

            health_score = metrics["overall_health_score"]

            # Create gauge chart
            # gauge = plt.pie( # F841: Unused
            plt.pie(
                [health_score / 10, 1 - health_score / 10],
                colors=[
                    (
                        "#4CAF50"
                        if health_score >= 7
                        else "#FFC107" if health_score >= 4 else "#F44336"
                    ),
                    "whitesmoke",
                ],
                startangle=90,
                counterclock=False,
                wedgeprops={"width": 0.3, "edgecolor": "white"},
            )

            plt.annotate(
                f"{health_score}/10",
                xy=(0, 0),
                ha="center",
                va="center",
                fontsize=24,
                fontweight="bold",
            )

            plt.title("Overall Repository Health Score", fontsize=16)

            # Save chart
            chart_path = os.path.join(output_dir, "overall_health_score.png")
            fig.savefig(chart_path)
            plt.close(fig)

            charts["overall_health_score"] = chart_path
        except Exception as e:
            logger.error(f"Failed to generate overall health score chart: {e}")

    # Category scores
    try:
        fig, ax = plt.subplots(figsize=(10, 8))

        categories = [
            "Contributor Diversity",
            "Commit Quality",
            "Pull Request Process",
            "Code Review",
            "CI/CD Integration",
            "Issue Management",
            "Testing Practices",
        ]

        scores = [
            metrics.get("contributor", {}).get("bus_factor", 0) / 10 * 10,  # Scale to 0-10
            metrics.get("commit", {}).get("commit_message_quality", {}).get("quality_score", 0),
            metrics.get("pull_request", {}).get("pr_velocity_score", 0),
            metrics.get("code_review", {}).get("review_thoroughness_score", 0),
            10 if metrics.get("ci_cd", {}).get("has_ci", False) else 0,  # Binary for has_ci
            metrics.get("issue", {}).get("responsiveness_score", 0),
            metrics.get("test", {}).get("testing_practice_score", 0),
        ]

        # Number of categories
        N = len(categories)

        # Create angles for radar chart
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
        scores.append(scores[0])  # Close the loop
        angles.append(angles[0])  # Close the loop

        # Plot data
        ax.plot(angles, scores, "o-", linewidth=2, color="#3F51B5")
        ax.fill(angles, scores, alpha=0.25, color="#3F51B5")

        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)

        # Set y-axis limits
        ax.set_ylim(0, 10)
        ax.set_yticks(np.arange(0, 11, 2))

        # Add grid
        ax.grid(True)

        # Set title
        plt.title("Repository Health by Category", fontsize=16)

        # Save chart
        chart_path = os.path.join(output_dir, "health_by_category.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["health_by_category"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate health by category chart: {e}")

    return charts


def generate_contributor_comparison_chart(
    metrics1: Dict[str, Any],
    metrics2: Dict[str, Any],
    repo1_name: str,
    repo2_name: str,
    output_dir: str,
) -> Dict[str, str]:
    """
    Generate charts comparing contributor metrics between two repositories.

    Args:
        metrics1: Contributor metrics for the first repository
        metrics2: Contributor metrics for the second repository
        repo1_name: Name of the first repository
        repo2_name: Name of the second repository
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # Bus factor comparison
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        bus_factor1 = metrics1.get("bus_factor", 0)
        bus_factor2 = metrics2.get("bus_factor", 0)

        repos = [repo1_name, repo2_name]
        bus_factors = [bus_factor1, bus_factor2]

        colors = ["#3F51B5", "#E91E63"]

        ax.bar(repos, bus_factors, color=colors)
        ax.set_ylabel("Bus Factor")
        ax.set_title("Bus Factor Comparison")

        # Add count labels
        for i, v in enumerate(bus_factors):
            ax.text(i, v + 0.1, str(v), ha="center")

        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, "bus_factor_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["bus_factor_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate bus factor comparison chart: {e}")

    # Contributor count comparison
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        total_contributors1 = metrics1.get("total_contributors", 0)
        total_contributors2 = metrics2.get("total_contributors", 0)

        active_contributors1 = metrics1.get("active_contributors", 0)
        active_contributors2 = metrics2.get("active_contributors", 0)

        repos = [repo1_name, repo2_name]
        total = [total_contributors1, total_contributors2]
        active = [active_contributors1, active_contributors2]

        x = np.arange(len(repos))
        width = 0.35

        ax.bar(x - width / 2, total, width, label="Total Contributors", color="#3F51B5")
        ax.bar(x + width / 2, active, width, label="Active Contributors", color="#03A9F4")

        ax.set_ylabel("Number of Contributors")
        ax.set_title("Contributor Count Comparison")
        ax.set_xticks(x)
        ax.set_xticklabels(repos)
        ax.legend()

        # Add count labels
        for i, v in enumerate(total):
            ax.text(i - width / 2, v + 1, str(v), ha="center")
        for i, v in enumerate(active):
            ax.text(i + width / 2, v + 1, str(v), ha="center")

        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, "contributor_count_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["contributor_count_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate contributor count comparison chart: {e}")

    return charts


def generate_commit_comparison_chart(
    metrics1: Dict[str, Any],
    metrics2: Dict[str, Any],
    repo1_name: str,
    repo2_name: str,
    output_dir: str,
) -> Dict[str, str]:
    """
    Generate charts comparing commit metrics between two repositories.

    Args:
        metrics1: Commit metrics for the first repository
        metrics2: Commit metrics for the second repository
        repo1_name: Name of the first repository
        repo2_name: Name of the second repository
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # Commit frequency comparison
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        commits_per_day1 = metrics1.get("commits_per_day", 0)
        commits_per_day2 = metrics2.get("commits_per_day", 0)

        repos = [repo1_name, repo2_name]
        commits_per_day = [commits_per_day1, commits_per_day2]

        colors = ["#3F51B5", "#E91E63"]

        ax.bar(repos, commits_per_day, color=colors)
        ax.set_ylabel("Commits per Day")
        ax.set_title("Commit Frequency Comparison")

        # Add count labels
        for i, v in enumerate(commits_per_day):
            ax.text(i, v + 0.1, f"{v:.1f}", ha="center")

        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, "commit_frequency_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["commit_frequency_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate commit frequency comparison chart: {e}")

    # Commit message quality comparison
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        quality_score1 = metrics1.get("commit_message_quality", {}).get("quality_score", 0)
        quality_score2 = metrics2.get("commit_message_quality", {}).get("quality_score", 0)

        repos = [repo1_name, repo2_name]
        quality_scores = [quality_score1, quality_score2]

        colors = [
            "#4CAF50" if score >= 7 else "#FFC107" if score >= 4 else "#F44336"
            for score in quality_scores
        ]

        ax.bar(repos, quality_scores, color=colors)
        ax.set_ylabel("Quality Score (0-10)")
        ax.set_title("Commit Message Quality Comparison")
        ax.set_ylim(0, 10)

        # Add score labels
        for i, v in enumerate(quality_scores):
            ax.text(i, v + 0.2, f"{v:.1f}", ha="center")

        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, "commit_quality_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["commit_quality_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate commit quality comparison chart: {e}")

    return charts


def generate_pr_comparison_chart(
    metrics1: Dict[str, Any],
    metrics2: Dict[str, Any],
    repo1_name: str,
    repo2_name: str,
    output_dir: str,
) -> Dict[str, str]:
    """
    Generate charts comparing pull request metrics between two repositories.

    Args:
        metrics1: Pull request metrics for the first repository
        metrics2: Pull request metrics for the second repository
        repo1_name: Name of the first repository
        repo2_name: Name of the second repository
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # PR velocity comparison
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        velocity_score1 = metrics1.get("pr_velocity_score", 0)
        velocity_score2 = metrics2.get("pr_velocity_score", 0)

        repos = [repo1_name, repo2_name]
        velocity_scores = [velocity_score1, velocity_score2]

        colors = [
            "#4CAF50" if score >= 7 else "#FFC107" if score >= 4 else "#F44336"
            for score in velocity_scores
        ]

        ax.bar(repos, velocity_scores, color=colors)
        ax.set_ylabel("Velocity Score (0-10)")
        ax.set_title("Pull Request Velocity Comparison")
        ax.set_ylim(0, 10)

        # Add score labels
        for i, v in enumerate(velocity_scores):
            ax.text(i, v + 0.2, f"{v:.1f}", ha="center")

        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, "pr_velocity_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["pr_velocity_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate PR velocity comparison chart: {e}")

    # PR merged ratio comparison
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        merged_ratio1 = metrics1.get("merged_ratio", 0)
        merged_ratio2 = metrics2.get("merged_ratio", 0)

        repos = [repo1_name, repo2_name]
        merged_ratios = [merged_ratio1, merged_ratio2]

        colors = [
            "#4CAF50" if ratio >= 0.7 else "#FFC107" if ratio >= 0.4 else "#F44336"
            for ratio in merged_ratios
        ]

        ax.bar(repos, merged_ratios, color=colors)
        ax.set_ylabel("Merged Ratio")
        ax.set_title("Pull Request Merged Ratio Comparison")
        ax.set_ylim(0, 1)

        # Add percentage labels
        for i, v in enumerate(merged_ratios):
            ax.text(i, v + 0.02, f"{v:.1%}", ha="center")

        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, "pr_merged_ratio_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["pr_merged_ratio_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate PR merged ratio comparison chart: {e}")

    return charts


def generate_review_comparison_chart(
    metrics1: Dict[str, Any],
    metrics2: Dict[str, Any],
    repo1_name: str,
    repo2_name: str,
    output_dir: str,
) -> Dict[str, str]:
    """
    Generate charts comparing code review metrics between two repositories.

    Args:
        metrics1: Code review metrics for the first repository
        metrics2: Code review metrics for the second repository
        repo1_name: Name of the first repository
        repo2_name: Name of the second repository
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    # Review thoroughness comparison
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        thoroughness_score1 = metrics1.get("review_thoroughness_score", 0)
        thoroughness_score2 = metrics2.get("review_thoroughness_score", 0)

        repos = [repo1_name, repo2_name]
        thoroughness_scores = [thoroughness_score1, thoroughness_score2]

        colors = [
            "#4CAF50" if score >= 7 else "#FFC107" if score >= 4 else "#F44336"
            for score in thoroughness_scores
        ]

        ax.bar(repos, thoroughness_scores, color=colors)
        ax.set_ylabel("Thoroughness Score (0-10)")
        ax.set_title("Code Review Thoroughness Comparison")
        ax.set_ylim(0, 10)

        # Add score labels
        for i, v in enumerate(thoroughness_scores):
            ax.text(i, v + 0.2, f"{v:.1f}", ha="center")

        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, "review_thoroughness_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["review_thoroughness_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate review thoroughness comparison chart: {e}")

    # Self-merge comparison
    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        self_merged_ratio1 = metrics1.get("self_merged_ratio", 0)
        self_merged_ratio2 = metrics2.get("self_merged_ratio", 0)

        independent_review_ratio1 = 1 - self_merged_ratio1
        independent_review_ratio2 = 1 - self_merged_ratio2

        repos = [repo1_name, repo2_name]
        independent_review_ratios = [independent_review_ratio1, independent_review_ratio2]

        colors = [
            "#4CAF50" if ratio >= 0.8 else "#FFC107" if ratio >= 0.5 else "#F44336"
            for ratio in independent_review_ratios
        ]

        ax.bar(repos, independent_review_ratios, color=colors)
        ax.set_ylabel("Independent Review Ratio")
        ax.set_title("Independent Code Review Ratio Comparison")
        ax.set_ylim(0, 1)

        # Add percentage labels
        for i, v in enumerate(independent_review_ratios):
            ax.text(i, v + 0.02, f"{v:.1%}", ha="center")

        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, "independent_review_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["independent_review_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate independent review comparison chart: {e}")

    return charts


def generate_health_comparison_chart(
    health_score1: float, health_score2: float, repo1_name: str, repo2_name: str, output_dir: str
) -> Dict[str, str]:
    """
    Generate chart comparing overall health between two repositories.

    Args:
        health_score1: Overall health score for the first repository
        health_score2: Overall health score for the second repository
        repo1_name: Name of the first repository
        repo2_name: Name of the second repository
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    try:
        fig, ax = plt.subplots(figsize=(10, 6))

        repos = [repo1_name, repo2_name]
        health_scores = [health_score1, health_score2]

        colors = [
            "#4CAF50" if score >= 7 else "#FFC107" if score >= 4 else "#F44336"
            for score in health_scores
        ]

        ax.bar(repos, health_scores, color=colors)
        ax.set_ylabel("Health Score (0-10)")
        ax.set_title("Overall Repository Health Comparison")
        ax.set_ylim(0, 10)

        # Add score labels
        for i, v in enumerate(health_scores):
            ax.text(i, v + 0.2, f"{v:.1f}", ha="center")

        plt.tight_layout()

        # Save chart
        chart_path = os.path.join(output_dir, "overall_health_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["overall_health_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate overall health comparison chart: {e}")

    return charts


def generate_category_comparison_chart(
    metrics1: Dict[str, Any],
    metrics2: Dict[str, Any],
    repo1_name: str,
    repo2_name: str,
    output_dir: str,
) -> Dict[str, str]:
    """
    Generate radar chart comparing category scores between two repositories.

    Args:
        metrics1: Metrics for the first repository
        metrics2: Metrics for the second repository
        repo1_name: Name of the first repository
        repo2_name: Name of the second repository
        output_dir: Output directory for charts

    Returns:
        Dictionary mapping chart names to file paths
    """
    charts = {}

    try:
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

        categories = [
            "Contributor\nDiversity",
            "Commit\nQuality",
            "Pull Request\nProcess",
            "Code\nReview",
            "CI/CD\nIntegration",
            "Issue\nManagement",
            "Testing\nPractices",
        ]

        scores1 = [
            metrics1.get("contributor", {}).get("bus_factor", 0) / 10 * 10,  # Scale to 0-10
            metrics1.get("commit", {}).get("commit_message_quality", {}).get("quality_score", 0),
            metrics1.get("pull_request", {}).get("pr_velocity_score", 0),
            metrics1.get("code_review", {}).get("review_thoroughness_score", 0),
            10 if metrics1.get("ci_cd", {}).get("has_ci", False) else 0,  # Binary for has_ci
            metrics1.get("issue", {}).get("responsiveness_score", 0),
            metrics1.get("test", {}).get("testing_practice_score", 0),
        ]

        scores2 = [
            metrics2.get("contributor", {}).get("bus_factor", 0) / 10 * 10,  # Scale to 0-10
            metrics2.get("commit", {}).get("commit_message_quality", {}).get("quality_score", 0),
            metrics2.get("pull_request", {}).get("pr_velocity_score", 0),
            metrics2.get("code_review", {}).get("review_thoroughness_score", 0),
            10 if metrics2.get("ci_cd", {}).get("has_ci", False) else 0,  # Binary for has_ci
            metrics2.get("issue", {}).get("responsiveness_score", 0),
            metrics2.get("test", {}).get("testing_practice_score", 0),
        ]

        # Number of categories
        N = len(categories)

        # Create angles for radar chart
        angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()

        # Close the loop
        scores1.append(scores1[0])
        scores2.append(scores2[0])
        angles.append(angles[0])

        # Plot data
        ax.plot(angles, scores1, "o-", linewidth=2, label=repo1_name, color="#3F51B5")
        ax.fill(angles, scores1, alpha=0.25, color="#3F51B5")

        ax.plot(angles, scores2, "o-", linewidth=2, label=repo2_name, color="#E91E63")
        ax.fill(angles, scores2, alpha=0.25, color="#E91E63")

        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)

        # Set y-axis limits
        ax.set_ylim(0, 10)
        ax.set_yticks(np.arange(0, 11, 2))

        # Add legend
        ax.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))

        # Add grid
        ax.grid(True)

        # Set title
        plt.title("Repository Health by Category", fontsize=16)

        # Save chart
        chart_path = os.path.join(output_dir, "category_comparison.png")
        fig.savefig(chart_path)
        plt.close(fig)

        charts["category_comparison"] = chart_path
    except Exception as e:
        logger.error(f"Failed to generate category comparison chart: {e}")

    return charts
