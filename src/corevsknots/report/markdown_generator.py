"""
Markdown report generator.

This module generates markdown reports from repository metrics.
"""

import os
import re
from datetime import datetime
from typing import Any, Dict, List

from ..utils.logger import get_logger
from .chart_generator import generate_charts, generate_comparison_charts

# Define for fork-aware logic in reporting
KNOTS_REPO_IDENTIFIER = "bitcoinknots/bitcoin"
CORE_REPO_IDENTIFIER = "bitcoin/bitcoin"

logger = get_logger(__name__)


def generate_report(
    metrics: Dict[str, Any],
    output_dir: str,
    output_name: str,
    output_format: str = "markdown",
    template: str = "single",
) -> str:
    """
    Generate a report from repository metrics.

    Args:
        metrics: Repository metrics or comparison results
        output_dir: Output directory
        output_name: Output file name (without extension)
        output_format: Output format (markdown, html, json)
        template: Report template to use (single, comparison)

    Returns:
        Path to the generated report
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Always generate the JSON data file for later use, if not the primary format
    json_report_path = os.path.join(output_dir, f"{output_name}.json")
    try:
        import json
        with open(json_report_path, "w") as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Generated accompanying JSON data report: {json_report_path}")
    except Exception as e:
        logger.error(f"Failed to generate accompanying JSON data report: {e}")

    # Generate charts
    if template == "comparison":
        charts = generate_comparison_charts(metrics, output_dir)
    else:
        charts = generate_charts(metrics, output_dir)

    # Generate report based on format
    if output_format == "markdown":
        report_path = generate_markdown_report(metrics, charts, output_dir, output_name, template)
    elif output_format == "html":
        report_path = generate_html_report(metrics, charts, output_dir, output_name, template)
    elif output_format == "json":
        # If JSON is the primary format, we've already created it.
        # The function expects to return the path to the primary requested report.
        report_path = json_report_path
    else:
        raise ValueError(f"Unsupported output format: {output_format}")

    return report_path


def generate_markdown_report(
    metrics: Dict[str, Any],
    charts: Dict[str, str],
    output_dir: str,
    output_name: str,
    template: str = "single",
) -> str:
    """
    Generate a markdown report from repository metrics.

    Args:
        metrics: Repository metrics or comparison results
        charts: Generated charts
        output_dir: Output directory
        output_name: Output file name (without extension)
        template: Report template to use (single, comparison)

    Returns:
        Path to the generated report
    """
    # Determine template based on input data and template parameter
    if template == "comparison":
        report_content = generate_comparison_report_content(metrics, charts)
    else:
        report_content = generate_single_report_content(metrics, charts)

    # Write report to file
    report_path = os.path.join(output_dir, f"{output_name}.md")
    with open(report_path, "w") as f:
        f.write(report_content)

    logger.info(f"Generated markdown report: {report_path}")

    return report_path


def generate_html_report(
    metrics: Dict[str, Any],
    charts: Dict[str, str],
    output_dir: str,
    output_name: str,
    template: str = "single",
) -> str:
    """
    Generate an HTML report from repository metrics.

    Args:
        metrics: Repository metrics or comparison results
        charts: Generated charts
        output_dir: Output directory
        output_name: Output file name (without extension)
        template: Report template to use (single, comparison)

    Returns:
        Path to the generated report
    """
    # For now, just convert markdown to HTML
    # In a real implementation, we would use a proper HTML template

    if template == "comparison":
        markdown_content = generate_comparison_report_content(metrics, charts)
    else:
        markdown_content = generate_single_report_content(metrics, charts)

    # Very simple markdown to HTML conversion
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Repository Health Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }}
            h1, h2, h3, h4 {{ color: #2c3e50; }}
            h1 {{ border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            h2 {{ border-bottom: 1px solid #eee; padding-bottom: 5px; }}
            img {{ max-width: 100%; height: auto; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ text-align: left; padding: 12px; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f8f8f8; }}
            code {{ background-color: #f0f0f0; padding: 2px 4px; border-radius: 4px; }}
            pre {{ background-color: #f0f0f0; padding: 10px; border-radius: 4px; overflow-x: auto; }}
            .good {{ color: #4CAF50; }}
            .warning {{ color: #FFC107; }}
            .poor {{ color: #F44336; }}
        </style>
    </head>
    <body>
        {markdown_to_html(markdown_content)}
    </body>
    </html>
    """

    # Write report to file
    report_path = os.path.join(output_dir, f"{output_name}.html")
    with open(report_path, "w") as f:
        f.write(html_content)

    logger.info(f"Generated HTML report: {report_path}")

    return report_path


def generate_json_report(metrics: Dict[str, Any], output_dir: str, output_name: str) -> str:
    """
    Generate a JSON report from repository metrics.

    Args:
        metrics: Repository metrics or comparison results
        output_dir: Output directory
        output_name: Output file name (without extension)

    Returns:
        Path to the generated report
    """
    import json

    # Write report to file
    report_path = os.path.join(output_dir, f"{output_name}.json")
    with open(report_path, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"Generated JSON report: {report_path}")

    return report_path


def generate_single_report_content(metrics: Dict[str, Any], charts: Dict[str, str]) -> str:
    """
    Generate content for a single repository report.

    Args:
        metrics: Repository metrics
        charts: Generated charts

    Returns:
        Report content as markdown
    """
    # Extract repository name
    repo_name = metrics.get("repository", {}).get("name", "Unknown Repository")

    # Generate report sections
    sections = []

    # Title and introduction
    sections.append(f"# Repository Health Report: {repo_name}\n")
    sections.append("## Introduction\n")
    sections.append(
        "This report provides a comprehensive analysis of the repository's health "
        "based on open-source development practices and software quality metrics. "
        "The analysis examines contributor activity, commit patterns, pull request workflows, "
        "code review processes, CI/CD usage, issue tracking, and test coverage signals.\n"
    )

    # Analysis metadata
    sections.append("### Analysis Metadata\n")
    sections.append("| Metric | Value |\n|--------|-------|\n")
    sections.append(f"| Repository | {repo_name} |\n")

    analysis_date = metrics.get("repository", {}).get("analysis_date", datetime.now().isoformat())
    try:
        analysis_date = datetime.fromisoformat(analysis_date).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        pass

    sections.append(f"| Analysis Date | {analysis_date} |\n")
    sections.append(
        f"| Analysis Period | Last {metrics.get('repository', {}).get('analysis_period_months', 12)} months |\n"
    )

    # Overall health score
    if "overall_health_score" in metrics:
        sections.append("\n## Overall Health Score\n")

        health_score = metrics["overall_health_score"]
        if health_score >= 7:
            health_rating = "Good"
        elif health_score >= 4:
            health_rating = "Moderate"
        else:
            health_rating = "Poor"

        sections.append(f"**Overall Health Score**: {health_score}/10 ({health_rating})\n")

        if "overall_health_score" in charts:
            chart_path = os.path.relpath(
                charts["overall_health_score"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![Overall Health Score]({chart_path})\n")

        if "health_by_category" in charts:
            chart_path = os.path.relpath(
                charts["health_by_category"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![Health by Category]({chart_path})\n")

    # Contributor metrics
    if "contributor" in metrics:
        sections.append("\n## Contributor Base and Activity\n")
        contributor_metrics = metrics["contributor"]
        is_knots_repo_with_original = repo_name == KNOTS_REPO_IDENTIFIER and "knots_original_bus_factor" in contributor_metrics

        total_contributors_api = contributor_metrics.get("total_contributors", 0)
        active_contributors_api = contributor_metrics.get("active_contributors", 0)
        active_ratio_api = contributor_metrics.get("active_ratio", 0.0)

        sections.append(
            f"The repository has **{total_contributors_api} total contributors (GitHub API view)**, "
            f"with **{active_contributors_api} active contributors** in the analyzed period (based on any commit activity, {active_ratio_api:.1%} activity ratio overall).\n"
        )

        bus_factor_for_assessment = contributor_metrics.get("bus_factor", 0) # Default to general
        gini_for_display = contributor_metrics.get("contributor_gini", 0.0)
        bus_factor_context = "(General, from GH API contributions)"

        if is_knots_repo_with_original:
            sections.append("\n### Bitcoin Knots Specific Contributor Analysis (based on recent commit activity)\n")
            sections.append(f"- Authors with original Knots commits: {contributor_metrics.get('knots_contributors_with_original_work', 'N/A')}\n")
            sections.append(f"- Authors primarily merging Core changes (and no original work): {contributor_metrics.get('knots_contributors_only_merging_core', 'N/A')}\n")

            bus_factor_for_assessment = contributor_metrics.get('knots_original_bus_factor', bus_factor_for_assessment)
            gini_for_display = contributor_metrics.get('knots_original_contributor_gini', gini_for_display)
            bus_factor_context = "(Knots Original Work)"
            sections.append(f"- **Bus Factor {bus_factor_context}**: {bus_factor_for_assessment}\n")
            sections.append(f"- **Gini Coefficient {bus_factor_context}**: {gini_for_display:.3f}\n")

            sections.append("\n#### Top Original Knots Contributors (by original commits):\n")
            if "knots_top_original_contributors" in contributor_metrics and contributor_metrics["knots_top_original_contributors"]:
                for author, count in contributor_metrics["knots_top_original_contributors"]:
                    sections.append(f"  - {author}: {count} original commits\n")
            else:
                sections.append("  - No original Knots commit authors identified in the analyzed period.\n")
        else: # For Core or other general repos
            sections.append(f"- **Bus Factor {bus_factor_context}**: {bus_factor_for_assessment}\n")
            sections.append(f"- **Gini Coefficient {bus_factor_context}**: {gini_for_display:.3f}\n")
            sections.append("\n#### Top Contributors (by GH API contributions):\n")
            if "top_contributors" in contributor_metrics and contributor_metrics["top_contributors"]:
                 for author, count in contributor_metrics["top_contributors"]:
                    sections.append(f"  - {author}: {count} contributions\n")
            else:
                sections.append("  - No contributor data from GitHub API.\n")

        sections.append(
            f"\nThe repository has a calculated bus factor of {bus_factor_for_assessment} {bus_factor_context}. "
            f"This estimates how many key contributors would need to leave before the project might face significant disruption based on the analyzed contribution patterns.\n"
        )
        if bus_factor_for_assessment >= 5:
            sections.append(
                "🟢 **Good**: The repository appears to have a healthy contributor spread, reducing risk.\n"
            )
        elif bus_factor_for_assessment >= 2:
            sections.append(
                "🟡 **Moderate**: There is some contributor redundancy, but risk could be further reduced by broadening expertise.\n"
            )
        else:
            sections.append(
                "🔴 **Poor**: The repository may have a high dependency on a very small number of contributors, posing a significant risk.\n"
            )
        # Charts are already adapted to show Knots original if repo_name is passed to generate_contributor_charts
        if "top_contributors" in charts:
            chart_path = os.path.relpath(
                charts["top_contributors"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![Top Contributors {bus_factor_context}]({chart_path})\n")

        if "bus_factor" in charts:
            chart_path = os.path.relpath(
                charts["bus_factor"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![Bus Factor {bus_factor_context}]({chart_path})\n")

        knots_org_count = knots_contrib_metrics.get("organization_count", "N/A")
        knots_org_diversity = knots_contrib_metrics.get("organization_diversity", 0.0)
        core_org_count = core_contrib_metrics.get("organization_count", "N/A") # From git_data
        core_org_diversity = core_contrib_metrics.get("organization_diversity", 0.0) # From git_data

        sections.append(f"- **Organizational Diversity (Knots Original Commit Authors)**: {knots_org_count} domains, Diversity Score: {knots_org_diversity:.3f}\n")
        sections.append(f"- **Organizational Diversity (Core All Commit Authors via git log)**: {core_org_count} domains, Diversity Score: {core_org_diversity:.3f}\n")

    # Commit metrics
    if "commit" in metrics:
        sections.append("\n## Commit Activity and Patterns\n")

        commit_metrics = metrics["commit"]
        commits_per_day = commit_metrics.get("commits_per_day", 0)
        commits_per_week = commit_metrics.get("commits_per_week", 0)
        commit_frequency = commit_metrics.get("commit_frequency", "inactive")
        message_quality = commit_metrics.get("commit_message_quality", {}).get("quality_score", 0)
        merge_ratio = commit_metrics.get("merge_commit_ratio", 0)

        # Format commit frequency for readability
        if commit_frequency == "very_active":
            frequency_str = "very active"
        elif commit_frequency == "active":
            frequency_str = "active"
        elif commit_frequency == "moderate":
            frequency_str = "moderately active"
        elif commit_frequency == "low":
            frequency_str = "low activity"
        else:
            frequency_str = "inactive"

        sections.append(
            f"The repository shows **{frequency_str}** commit patterns with "
            f"**{commits_per_day:.1f} commits per day** (approximately {commits_per_week:.1f} per week).\n"
        )

        sections.append(f"**Commit Message Quality**: {message_quality}/10\n")

        sections.append(
            f"**Merge Commit Ratio**: {merge_ratio:.1%} of commits are merge commits.\n"
        )

        # Commit frequency assessment
        if commits_per_day >= 3:
            sections.append(
                "🟢 **Good**: The repository shows high commit activity, indicating active development.\n"
            )
        elif commits_per_day >= 1:
            sections.append("🟡 **Moderate**: The repository shows regular commit activity.\n")
        else:
            sections.append(
                "🔴 **Low**: The repository shows minimal commit activity, possibly indicating a less active project.\n"
            )

        # Commit pattern charts
        if "commits_by_day" in charts:
            chart_path = os.path.relpath(
                charts["commits_by_day"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![Commits by Day]({chart_path})\n")

        if "commits_by_hour" in charts:
            chart_path = os.path.relpath(
                charts["commits_by_hour"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![Commits by Hour]({chart_path})\n")

        if "commit_message_quality" in charts:
            chart_path = os.path.relpath(
                charts["commit_message_quality"],
                os.path.dirname(os.path.join(os.getcwd(), "dummy")),
            )
            sections.append(f"![Commit Message Quality]({chart_path})\n")

    # Pull request metrics
    if "pull_request" in metrics:
        sections.append("\n## Pull Request Practices\n")

        pr_metrics = metrics["pull_request"]
        total_prs = pr_metrics.get("total_prs", 0)
        merged_ratio = pr_metrics.get("merged_ratio", 0)
        avg_time_to_merge = pr_metrics.get("avg_time_to_merge", 0)
        velocity_score = pr_metrics.get("pr_velocity_score", 0)

        sections.append(
            f"The repository has processed **{total_prs} pull requests** in the analysis period, "
            f"with a **merge rate of {merged_ratio:.1%}**.\n"
        )

        # Format time to merge for readability
        if avg_time_to_merge < 24:
            time_str = f"{avg_time_to_merge:.1f} hours"
        elif avg_time_to_merge < 168:  # 7 days
            time_str = f"{avg_time_to_merge / 24:.1f} days"
        else:
            time_str = f"{avg_time_to_merge / 168:.1f} weeks"

        sections.append(f"**Average Time to Merge**: {time_str}\n")
        sections.append(f"**PR Velocity Score**: {velocity_score}/10\n")

        # PR process assessment
        if merged_ratio >= 0.7 and velocity_score >= 7:
            sections.append(
                "🟢 **Good**: The repository has an efficient pull request process with high throughput and quick turnaround.\n"
            )
        elif merged_ratio >= 0.5 and velocity_score >= 4:
            sections.append(
                "🟡 **Moderate**: The repository has a functional pull request process but could improve efficiency.\n"
            )
        else:
            sections.append(
                "🔴 **Poor**: The repository has an inefficient pull request process with potential bottlenecks.\n"
            )

        # PR charts
        if "pr_state_distribution" in charts:
            chart_path = os.path.relpath(
                charts["pr_state_distribution"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![PR State Distribution]({chart_path})\n")

        if "pr_velocity" in charts:
            chart_path = os.path.relpath(
                charts["pr_velocity"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![PR Velocity]({chart_path})\n")

    # Code review metrics
    if "code_review" in metrics:
        sections.append("\n## Code Review Process\n")

        review_metrics = metrics["code_review"]
        reviews_per_pr = review_metrics.get("reviews_per_pr", 0)
        comments_per_pr = review_metrics.get("comments_per_pr", 0)
        thoroughness_score = review_metrics.get("review_thoroughness_score", 0)
        self_merged_ratio = review_metrics.get("self_merged_ratio", 0)

        sections.append(
            f"The repository averages **{reviews_per_pr:.1f} reviews per pull request** "
            f"with **{comments_per_pr:.1f} comments per pull request**.\n"
        )

        sections.append(f"**Review Thoroughness Score**: {thoroughness_score}/10\n")
        sections.append(
            f"**Self-Merged Ratio**: {self_merged_ratio:.1%} of merged PRs are merged by the author (without independent review).\n"
        )

        # Code review assessment
        if thoroughness_score >= 7 and self_merged_ratio <= 0.2:
            sections.append(
                "🟢 **Good**: The repository has a thorough code review process with strong independent oversight.\n"
            )
        elif thoroughness_score >= 4 and self_merged_ratio <= 0.5:
            sections.append(
                "🟡 **Moderate**: The repository has a functional code review process but could improve thoroughness.\n"
            )
        else:
            sections.append(
                "🔴 **Poor**: The repository has a weak code review process with limited independent oversight.\n"
            )

        # Review charts
        if "review_thoroughness" in charts:
            chart_path = os.path.relpath(
                charts["review_thoroughness"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![Review Thoroughness]({chart_path})\n")

        if "independent_review_rate" in charts:
            chart_path = os.path.relpath(
                charts["independent_review_rate"],
                os.path.dirname(os.path.join(os.getcwd(), "dummy")),
            )
            sections.append(f"![Independent Review Rate]({chart_path})\n")

    # CI/CD metrics
    if "ci_cd" in metrics:
        sections.append("\n## Continuous Integration and Deployment\n")

        cicd_metrics = metrics["ci_cd"]
        has_ci = cicd_metrics.get("has_ci", False)
        workflow_success_rate = cicd_metrics.get("workflow_success_rate", 0)
        ci_systems = cicd_metrics.get("ci_systems", [])

        if has_ci:
            sections.append(
                f"The repository uses continuous integration with a **workflow success rate of {workflow_success_rate:.1%}**.\n"
            )

            if ci_systems:
                sections.append(f"**CI Systems Used**: {', '.join(ci_systems)}\n")

            # CI/CD assessment
            if workflow_success_rate >= 0.9:
                sections.append(
                    "🟢 **Good**: The repository has a reliable CI/CD pipeline with high success rates.\n"
                )
            elif workflow_success_rate >= 0.7:
                sections.append(
                    "🟡 **Moderate**: The repository has a functional CI/CD pipeline but could improve reliability.\n"
                )
            else:
                sections.append(
                    "🔴 **Poor**: The repository has an unreliable CI/CD pipeline with frequent failures.\n"
                )

            # CI charts
            if "ci_success_rate" in charts:
                chart_path = os.path.relpath(
                    charts["ci_success_rate"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
                )
                sections.append(f"![CI Success Rate]({chart_path})\n")
        else:
            sections.append(
                "❌ **No Continuous Integration Found**: The repository does not appear to use CI/CD.\n"
            )

    # Issue metrics
    if "issue" in metrics:
        sections.append("\n## Issue Tracking and Management\n")

        issue_metrics = metrics["issue"]
        total_issues = issue_metrics.get("total_issues", 0)
        open_issues = issue_metrics.get("open_issues", 0)
        closed_issues = issue_metrics.get("closed_issues", 0)
        responsiveness_score = issue_metrics.get("responsiveness_score", 0)
        stale_issues = issue_metrics.get("stale_issues", 0)

        sections.append(
            f"The repository has **{total_issues} total issues** "
            f"({open_issues} open, {closed_issues} closed).\n"
        )

        sections.append(f"**Issue Responsiveness Score**: {responsiveness_score}/10\n")
        sections.append(
            f"**Stale Issues**: {stale_issues} open issues have not been updated in over 30 days.\n"
        )

        # Issue management assessment
        if responsiveness_score >= 7 and stale_issues <= open_issues * 0.1:
            sections.append(
                "🟢 **Good**: The repository has a responsive issue management process with few stale issues.\n"
            )
        elif responsiveness_score >= 4 and stale_issues <= open_issues * 0.3:
            sections.append(
                "🟡 **Moderate**: The repository has a functional issue management process but could improve responsiveness.\n"
            )
        else:
            sections.append(
                "🔴 **Poor**: The repository has a weak issue management process with many stale issues.\n"
            )

        # Issue charts
        if "issue_state_distribution" in charts:
            chart_path = os.path.relpath(
                charts["issue_state_distribution"],
                os.path.dirname(os.path.join(os.getcwd(), "dummy")),
            )
            sections.append(f"![Issue State Distribution]({chart_path})\n")

        if "issue_responsiveness" in charts:
            chart_path = os.path.relpath(
                charts["issue_responsiveness"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
            )
            sections.append(f"![Issue Responsiveness]({chart_path})\n")

    # Test metrics
    if "test" in metrics:
        sections.append("\n## Testing Practices\n")

        test_metrics = metrics["test"]
        has_tests = test_metrics.get("has_tests", False)
        test_files_count = test_metrics.get("test_files_count", 0)
        testing_practice_score = test_metrics.get("testing_practice_score", 0)

        if has_tests:
            sections.append(
                f"The repository has **{test_files_count} test files** with a testing practice score of {testing_practice_score}/10.\n"
            )

            # Testing assessment
            if testing_practice_score >= 7:
                sections.append(
                    "🟢 **Good**: The repository has a strong testing practice with comprehensive test coverage.\n"
                )
            elif testing_practice_score >= 4:
                sections.append(
                    "🟡 **Moderate**: The repository has a functional testing practice but could improve coverage.\n"
                )
            else:
                sections.append(
                    "🔴 **Poor**: The repository has limited testing practices with room for improvement.\n"
                )
        else:
            sections.append(
                "❌ **No Tests Found**: The repository does not appear to have automated tests.\n"
            )

    # Conclusion and recommendations
    sections.append("\n## Conclusion and Recommendations\n")

    # Overall assessment based on health score
    overall_health = metrics.get("overall_health_score", 0)
    if overall_health >= 7:
        sections.append(
            "Overall, this repository demonstrates **good health** with strong development practices. "
            "It follows many open-source and software development best practices, suggesting a mature and well-maintained project.\n"
        )
    elif overall_health >= 4:
        sections.append(
            "Overall, this repository demonstrates **moderate health** with reasonable development practices. "
            "While it follows some best practices, there are areas for improvement to enhance project quality and sustainability.\n"
        )
    else:
        sections.append(
            "Overall, this repository demonstrates **poor health** with concerning development practices. "
            "Significant improvements are needed in several areas to enhance project quality and sustainability.\n"
        )

    # Generate specific recommendations based on metrics
    sections.append("### Specific Recommendations\n")
    recommendations = []

    # Contributor recommendations
    bus_factor = metrics.get("contributor", {}).get("bus_factor", 0)
    if bus_factor < 3:
        recommendations.append(
            "🔍 **Increase Bus Factor**: Encourage more contributors to become familiar with different parts of the codebase to reduce dependency on key individuals."
        )

    # Commit recommendations
    commit_quality = (
        metrics.get("commit", {}).get("commit_message_quality", {}).get("quality_score", 0)
    )
    if commit_quality < 7:
        recommendations.append(
            "🔍 **Improve Commit Messages**: Enhance commit message quality with more descriptive and consistent formatting."
        )

    # PR recommendations
    pr_velocity = metrics.get("pull_request", {}).get("pr_velocity_score", 0)
    if pr_velocity < 7:
        recommendations.append(
            "🔍 **Enhance PR Velocity**: Streamline the pull request process to reduce time to merge and increase throughput."
        )

    # Code review recommendations
    self_merged = metrics.get("code_review", {}).get("self_merged_ratio", 0)
    if self_merged > 0.3:
        recommendations.append(
            "🔍 **Strengthen Code Review**: Implement stricter code review policies to ensure independent review before merging."
        )

    # CI/CD recommendations
    has_ci = metrics.get("ci_cd", {}).get("has_ci", False)
    if not has_ci:
        recommendations.append(
            "🔍 **Add CI/CD**: Implement continuous integration to automate testing and quality checks."
        )
    elif metrics.get("ci_cd", {}).get("workflow_success_rate", 0) < 0.8:
        recommendations.append(
            "🔍 **Improve CI Reliability**: Address frequent CI failures to enhance pipeline reliability."
        )

    # Issue recommendations
    responsiveness = metrics.get("issue", {}).get("responsiveness_score", 0)
    if responsiveness < 7:
        recommendations.append(
            "🔍 **Improve Issue Responsiveness**: Develop a more responsive approach to issue triage and resolution."
        )

    # Test recommendations
    has_tests = metrics.get("test", {}).get("has_tests", False)
    if not has_tests:
        recommendations.append(
            "🔍 **Add Tests**: Implement automated tests to ensure code quality and prevent regressions."
        )
    elif metrics.get("test", {}).get("testing_practice_score", 0) < 7:
        recommendations.append(
            "🔍 **Enhance Test Coverage**: Expand test coverage to include more code paths and edge cases."
        )

    # Add recommendations to report
    if recommendations:
        sections.append("\n".join(recommendations))
    else:
        sections.append(
            "No specific recommendations identified. The repository follows good practices in all analyzed areas."
        )

    # Join all sections
    return "\n".join(sections)


def generate_comparison_report_content(metrics: Dict[str, Any], charts: Dict[str, str]) -> str:
    """
    Generate content for a comparison report.

    Args:
        metrics: Comparison metrics
        charts: Generated charts

    Returns:
        Report content as markdown
    """
    # Extract repository names
    repo1_name = metrics["repo1"]["name"]
    repo2_name = metrics["repo2"]["name"]

    # Generate report sections
    sections = []

    # Title and introduction
    sections.append(f"# Repository Health Comparison: {repo1_name} vs {repo2_name}\n")
    sections.append("## Introduction\n")
    sections.append(
        "This report provides a comparative analysis of two repositories in terms of "
        "open-source development practices and software quality metrics. The analysis "
        "examines contributor activity, commit patterns, pull request workflows, "
        "code review processes, CI/CD usage, issue tracking, and test coverage signals.\n"
    )

    # Analysis metadata
    sections.append("### Analysis Metadata\n")
    sections.append("| Metric | Value |\n|--------|-------|\n")

    analysis_date = metrics["analysis_metadata"]["date"]
    try:
        analysis_date = datetime.fromisoformat(analysis_date).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        pass

    sections.append(f"| Analysis Date | {analysis_date} |\n")
    sections.append(
        f"| Analysis Period | Last {metrics['analysis_metadata']['period_months']} months |\n"
    )
    sections.append(f"| Repository 1 | {repo1_name} |\n")
    sections.append(f"| Repository 2 | {repo2_name} |\n")

    # Overall health comparison
    sections.append("\n## Overall Health Comparison\n")

    health_score1 = metrics["repo1"]["metrics"].get("overall_health_score", 0)
    health_score2 = metrics["repo2"]["metrics"].get("overall_health_score", 0)

    health_difference = health_score1 - health_score2
    if health_difference > 0:
        comparison_text = f"{repo1_name} has a higher overall health score by **{abs(health_difference):.1f} points**."
    elif health_difference < 0:
        comparison_text = f"{repo2_name} has a higher overall health score by **{abs(health_difference):.1f} points**."
    else:
        comparison_text = "Both repositories have the same overall health score."

    sections.append(f"**{repo1_name}**: {health_score1}/10\n")
    sections.append(f"**{repo2_name}**: {health_score2}/10\n")
    sections.append(f"{comparison_text}\n")

    # Overall health comparison chart
    if "overall_health_comparison" in charts:
        chart_path = os.path.relpath(
            charts["overall_health_comparison"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
        )
        sections.append(f"![Overall Health Comparison]({chart_path})\n")

    # Category comparison chart
    if "category_comparison" in charts:
        chart_path = os.path.relpath(
            charts["category_comparison"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
        )
        sections.append(f"![Category Comparison]({chart_path})\n")

    # Contributor comparison
    sections.append("\n## Contributor Base Comparison\n")

    contributor_metrics1 = metrics["repo1"]["metrics"].get("contributor", {})
    contributor_metrics2 = metrics["repo2"]["metrics"].get("contributor", {})

    total_contributors1 = contributor_metrics1.get("total_contributors", 0)
    total_contributors2 = contributor_metrics2.get("total_contributors", 0)

    bus_factor1 = contributor_metrics1.get("bus_factor", 0)
    bus_factor2 = contributor_metrics2.get("bus_factor", 0)

    sections.append(
        f"**{repo1_name}** has **{total_contributors1} contributors** with a bus factor of **{bus_factor1}**.\n"
    )
    sections.append(
        f"**{repo2_name}** has **{total_contributors2} contributors** with a bus factor of **{bus_factor2}**.\n"
    )

    contributor_difference = total_contributors1 - total_contributors2
    if contributor_difference > 0:
        sections.append(
            f"**{repo1_name}** has **{abs(contributor_difference)} more contributors** than {repo2_name}.\n"
        )
    elif contributor_difference < 0:
        sections.append(
            f"**{repo2_name}** has **{abs(contributor_difference)} more contributors** than {repo1_name}.\n"
        )
    else:
        sections.append("Both repositories have the same number of contributors.\n")

    bus_factor_difference = bus_factor1 - bus_factor2
    if bus_factor_difference > 0:
        sections.append(
            f"**{repo1_name}** has a **higher bus factor** by {abs(bus_factor_difference)} points, indicating better resilience to contributor departure.\n"
        )
    elif bus_factor_difference < 0:
        sections.append(
            f"**{repo2_name}** has a **higher bus factor** by {abs(bus_factor_difference)} points, indicating better resilience to contributor departure.\n"
        )
    else:
        sections.append("Both repositories have the same bus factor.\n")

    if metrics.get("analysis_metadata", {}).get("is_fight_mode"):
        core_contrib_metrics = metrics["repo1"]["metrics"].get("contributor", {})
        knots_contrib_metrics = metrics["repo2"]["metrics"].get("contributor", {})

        sections.append("\n### Core vs. Knots Fork-Specific Contributor Insights (based on recent commit activity)\n")
        core_active = core_contrib_metrics.get("active_contributors", "N/A")
        knots_original_active = knots_contrib_metrics.get("knots_contributors_with_original_work", "N/A")
        knots_only_merging = knots_contrib_metrics.get("knots_contributors_only_merging_core", "N/A")
        knots_total_involved_in_merges = knots_contrib_metrics.get("core_merge_commit_authors_count", "N/A")

        sections.append(f"- **{repo1_name} (Core)**: {core_active} active contributors (based on recent commits).\n")
        sections.append(f"- **{repo2_name} (Knots)**: {knots_original_active} contributors with original work to Knots.\n")
        sections.append(f"  - Additionally, {knots_only_merging} contributors to Knots appeared to *only* merge changes from Core (no other original Knots commits detected in recent activity).\n")
        sections.append(f"  - Total authors involved in Core merges on Knots: {knots_total_involved_in_merges}.\n")

        if "knots_original_bus_factor" in knots_contrib_metrics:
            sections.append(f"- **Bus Factor (Knots Original Work)**: {knots_contrib_metrics['knots_original_bus_factor']} (Core general bus factor: {core_contrib_metrics.get('bus_factor', 'N/A')})\n")
        if "knots_original_contributor_gini" in knots_contrib_metrics:
            sections.append(f"- **Gini Coefficient (Knots Original Work)**: {knots_contrib_metrics['knots_original_contributor_gini']:.3f} (Core General Gini: {core_contrib_metrics.get('contributor_gini', 0.0):.3f})\n")

        knots_org_count = knots_contrib_metrics.get("organization_count", "N/A")
        knots_org_diversity = knots_contrib_metrics.get("organization_diversity", 0.0)
        core_org_count = core_contrib_metrics.get("organization_count", "N/A") # This is from Core's git_data
        core_org_diversity = core_contrib_metrics.get("organization_diversity", 0.0)

        sections.append(f"- **Organizational Diversity (Knots Original Commit Authors)**: {knots_org_count} domains, Diversity Score: {knots_org_diversity:.3f}\n")
        sections.append(f"- **Organizational Diversity (Core All Commit Authors via git log)**: {core_org_count} domains, Diversity Score: {core_org_diversity:.3f}\n")

    # Contributor comparison charts
    if "contributor_count_comparison" in charts:
        chart_path = os.path.relpath(
            charts["contributor_count_comparison"],
            os.path.dirname(os.path.join(os.getcwd(), "dummy")),
        )
        sections.append(f"![Contributor Count Comparison]({chart_path})\n")

    if "bus_factor_comparison" in charts:
        chart_path = os.path.relpath(
            charts["bus_factor_comparison"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
        )
        sections.append(f"![Bus Factor Comparison]({chart_path})\n")

    # Commit comparison
    sections.append("\n## Commit Activity Comparison\n")

    commit_metrics1 = metrics["repo1"]["metrics"].get("commit", {})
    commit_metrics2 = metrics["repo2"]["metrics"].get("commit", {})

    commits_per_day1 = commit_metrics1.get("commits_per_day", 0)
    commits_per_day2 = commit_metrics2.get("commits_per_day", 0)

    message_quality1 = commit_metrics1.get("commit_message_quality", {}).get("quality_score", 0)
    message_quality2 = commit_metrics2.get("commit_message_quality", {}).get("quality_score", 0)

    sections.append(
        f"**{repo1_name}** has **{commits_per_day1:.1f} commits per day** with a message quality score of **{message_quality1}/10**.\n"
    )
    sections.append(
        f"**{repo2_name}** has **{commits_per_day2:.1f} commits per day** with a message quality score of **{message_quality2}/10**.\n"
    )

    commits_difference = commits_per_day1 - commits_per_day2
    if commits_difference > 0:
        sections.append(
            f"**{repo1_name}** has **{abs(commits_difference):.1f} more commits per day** than {repo2_name}.\n"
        )
    elif commits_difference < 0:
        sections.append(
            f"**{repo2_name}** has **{abs(commits_difference):.1f} more commits per day** than {repo1_name}.\n"
        )
    else:
        sections.append("Both repositories have the same commit frequency.\n")

    quality_difference = message_quality1 - message_quality2
    if quality_difference > 0:
        sections.append(
            f"**{repo1_name}** has **higher commit message quality** by {abs(quality_difference):.1f} points.\n"
        )
    elif quality_difference < 0:
        sections.append(
            f"**{repo2_name}** has **higher commit message quality** by {abs(quality_difference):.1f} points.\n"
        )
    else:
        sections.append("Both repositories have the same commit message quality.\n")

    # Commit comparison charts
    if "commit_frequency_comparison" in charts:
        chart_path = os.path.relpath(
            charts["commit_frequency_comparison"],
            os.path.dirname(os.path.join(os.getcwd(), "dummy")),
        )
        sections.append(f"![Commit Frequency Comparison]({chart_path})\n")

    if "commit_quality_comparison" in charts:
        chart_path = os.path.relpath(
            charts["commit_quality_comparison"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
        )
        sections.append(f"![Commit Quality Comparison]({chart_path})\n")

    # Pull request comparison
    sections.append("\n## Pull Request Process Comparison\n")

    pr_metrics1 = metrics["repo1"]["metrics"].get("pull_request", {})
    pr_metrics2 = metrics["repo2"]["metrics"].get("pull_request", {})

    merged_ratio1 = pr_metrics1.get("merged_ratio", 0)
    merged_ratio2 = pr_metrics2.get("merged_ratio", 0)

    velocity_score1 = pr_metrics1.get("pr_velocity_score", 0)
    velocity_score2 = pr_metrics2.get("pr_velocity_score", 0)

    sections.append(
        f"**{repo1_name}** has a PR merge rate of **{merged_ratio1:.1%}** with a velocity score of **{velocity_score1}/10**.\n"
    )
    sections.append(
        f"**{repo2_name}** has a PR merge rate of **{merged_ratio2:.1%}** with a velocity score of **{velocity_score2}/10**.\n"
    )

    merged_difference = merged_ratio1 - merged_ratio2
    if merged_difference > 0:
        sections.append(
            f"**{repo1_name}** has a **higher PR merge rate** by {abs(merged_difference):.1%}.\n"
        )
    elif merged_difference < 0:
        sections.append(
            f"**{repo2_name}** has a **higher PR merge rate** by {abs(merged_difference):.1%}.\n"
        )
    else:
        sections.append("Both repositories have the same PR merge rate.\n")

    velocity_difference = velocity_score1 - velocity_score2
    if velocity_difference > 0:
        sections.append(
            f"**{repo1_name}** has a **higher PR velocity score** by {abs(velocity_difference):.1f} points, indicating faster PR processing.\n"
        )
    elif velocity_difference < 0:
        sections.append(
            f"**{repo2_name}** has a **higher PR velocity score** by {abs(velocity_difference):.1f} points, indicating faster PR processing.\n"
        )
    else:
        sections.append("Both repositories have the same PR velocity score.\n")

    # PR comparison charts
    if "pr_velocity_comparison" in charts:
        chart_path = os.path.relpath(
            charts["pr_velocity_comparison"], os.path.dirname(os.path.join(os.getcwd(), "dummy"))
        )
        sections.append(f"![PR Velocity Comparison]({chart_path})\n")

    if "pr_merged_ratio_comparison" in charts:
        chart_path = os.path.relpath(
            charts["pr_merged_ratio_comparison"],
            os.path.dirname(os.path.join(os.getcwd(), "dummy")),
        )
        sections.append(f"![PR Merged Ratio Comparison]({chart_path})\n")

    # Code review comparison
    sections.append("\n## Code Review Process Comparison\n")

    review_metrics1 = metrics["repo1"]["metrics"].get("code_review", {})
    review_metrics2 = metrics["repo2"]["metrics"].get("code_review", {})

    thoroughness_score1 = review_metrics1.get("review_thoroughness_score", 0)
    thoroughness_score2 = review_metrics2.get("review_thoroughness_score", 0)

    self_merged_ratio1 = review_metrics1.get("self_merged_ratio", 0)
    self_merged_ratio2 = review_metrics2.get("self_merged_ratio", 0)

    sections.append(
        f"**{repo1_name}** has a review thoroughness score of **{thoroughness_score1:.1f}/10** with a self-merged ratio of **{self_merged_ratio1:.1%}**.\n"
    )
    sections.append(
        f"**{repo2_name}** has a review thoroughness score of **{thoroughness_score2:.1f}/10** with a self-merged ratio of **{self_merged_ratio2:.1%}**.\n"
    )

    thoroughness_difference = thoroughness_score1 - thoroughness_score2
    if thoroughness_difference > 0:
        sections.append(
            f"**{repo1_name}** has a **higher review thoroughness score** by {abs(thoroughness_difference):.1f} points, indicating more thorough code reviews.\n"
        )
    elif thoroughness_difference < 0:
        sections.append(
            f"**{repo2_name}** has a **higher review thoroughness score** by {abs(thoroughness_difference):.1f} points, indicating more thorough code reviews.\n"
        )
    else:
        sections.append("Both repositories have the same review thoroughness score.\n")

    self_merged_difference = self_merged_ratio1 - self_merged_ratio2
    if self_merged_difference < 0:  # Lower is better for self-merged ratio
        sections.append(
            f"**{repo1_name}** has a **lower self-merged ratio** by {abs(self_merged_difference):.1%}, indicating better independent review practices.\n"
        )
    elif self_merged_difference > 0:
        sections.append(
            f"**{repo2_name}** has a **lower self-merged ratio** by {abs(self_merged_difference):.1%}, indicating better independent review practices.\n"
        )
    else:
        sections.append("Both repositories have the same self-merged ratio.\n")

    # Code review comparison charts
    if "review_thoroughness_comparison" in charts:
        chart_path = os.path.relpath(
            charts["review_thoroughness_comparison"],
            os.path.dirname(os.path.join(os.getcwd(), "dummy")),
        )
        sections.append(f"![Review Thoroughness Comparison]({chart_path})\n")

    if "independent_review_comparison" in charts:
        chart_path = os.path.relpath(
            charts["independent_review_comparison"],
            os.path.dirname(os.path.join(os.getcwd(), "dummy")),
        )
        sections.append(f"![Independent Review Comparison]({chart_path})\n")

    # Summary table of key metrics
    sections.append("\n## Summary of Key Metrics\n")

    # Add note about metrics interpretation
    sections.append("*Note: For all metrics in this table, a positive difference indicates better performance for the first repository, except for self-merged ratio where lower values are better.*\n\n")

    sections.append(f"| Metric | {repo1_name} | {repo2_name} | Difference |\n")
    sections.append(f"|--------|{'-' * len(repo1_name)}|{'-' * len(repo2_name)}|----------|\n")

    # Overall health
    sections.append(
        f"| Overall Health Score | {health_score1:.1f}/10 | {health_score2:.1f}/10 | {health_difference:+.1f} |\n"
    )

    # Contributor metrics - adjusted for fight mode
    is_fight = metrics.get("analysis_metadata", {}).get("is_fight_mode")
    c1_metrics = metrics["repo1"]["metrics"].get("contributor", {})
    c2_metrics = metrics["repo2"]["metrics"].get("contributor", {})

    total_contrib1 = c1_metrics.get("total_contributors", 0)
    bus_factor1_val = c1_metrics.get("bus_factor", 0) # General bus factor for Core

    if is_fight and repo2_name == KNOTS_REPO_IDENTIFIER: # KNOTS_REPO_IDENTIFIER needs to be available here
        total_contrib2 = c2_metrics.get("knots_contributors_with_original_work", 0)
        bus_factor2_val = c2_metrics.get("knots_original_bus_factor", 0)
        sections.append(f"| Total Contributors (Original for Knots) | {total_contrib1} | {total_contrib2} | {total_contrib1 - total_contrib2:+d} |\n")
        sections.append(f"| Bus Factor (Original for Knots) | {bus_factor1_val} | {bus_factor2_val} | {bus_factor1_val - bus_factor2_val:+d} |\n")
    else:
        total_contrib2 = c2_metrics.get("total_contributors", 0)
        bus_factor2_val = c2_metrics.get("bus_factor", 0)
        sections.append(f"| Total Contributors | {total_contrib1} | {total_contrib2} | {total_contrib1 - total_contrib2:+d} |\n")
        sections.append(f"| Bus Factor | {bus_factor1_val} | {bus_factor2_val} | {bus_factor1_val - bus_factor2_val:+d} |\n")

    # Commit metrics - commits_per_day for Knots should already be original due to earlier processing
    commit_metrics1 = metrics["repo1"]["metrics"].get("commit", {})
    commit_metrics2 = metrics["repo2"]["metrics"].get("commit", {})
    cpd1 = commit_metrics1.get("commits_per_day", 0)
    # In fight mode, commits_per_day for Knots is based on its original commits due to filtering in calculate_commit_metrics
    cpd2 = commit_metrics2.get("commits_per_day", 0)
    commit_msg_q1 = commit_metrics1.get("commit_message_quality", {}).get("quality_score", 0)
    commit_msg_q2 = commit_metrics2.get("commit_message_quality", {}).get("quality_score", 0)

    sections.append(
        f"| Commits per Day (Original for Knots if fight) | {cpd1:.1f} | {cpd2:.1f} | {cpd1 - cpd2:+.1f} |\n"
    )
    sections.append(
        f"| Commit Message Quality | {commit_msg_q1:.1f}/10 | {commit_msg_q2:.1f}/10 | {commit_msg_q1 - commit_msg_q2:+.1f} |\n"
    )

    # PR metrics
    sections.append(
        f"| PR Merge Rate | {merged_ratio1:.1%} | {merged_ratio2:.1%} | {merged_difference:+.1%} |\n"
    )
    sections.append(
        f"| PR Velocity Score | {velocity_score1:.1f}/10 | {velocity_score2:.1f}/10 | {velocity_difference:+.1f} |\n"
    )

    # Review metrics
    sections.append(
        f"| Review Thoroughness | {thoroughness_score1:.1f}/10 | {thoroughness_score2:.1f}/10 | {thoroughness_difference:+.1f} |\n"
    )
    sections.append(
        f"| Self-Merged Ratio | {self_merged_ratio1:.1%} | {self_merged_ratio2:.1%} | {-self_merged_difference:+.1%} |\n"
    )

    # Conclusion and recommendations
    sections.append("\n## Conclusion and Recommendations\n")

    # Overall comparison conclusion
    if health_difference > 2:
        sections.append(
            f"**{repo1_name}** demonstrates **significantly better repository health** compared to {repo2_name}. "
            f"It excels in several key areas including:"
        )
    elif health_difference > 0:
        sections.append(
            f"**{repo1_name}** demonstrates **moderately better repository health** compared to {repo2_name}. "
            f"It performs better in several areas including:"
        )
    elif health_difference < -2:
        sections.append(
            f"**{repo2_name}** demonstrates **significantly better repository health** compared to {repo1_name}. "
            f"It excels in several key areas including:"
        )
    elif health_difference < 0:
        sections.append(
            f"**{repo2_name}** demonstrates **moderately better repository health** compared to {repo1_name}. "
            f"It performs better in several areas including:"
        )
    else:
        sections.append(
            "Both repositories demonstrate **similar overall health**, though they have different strengths and weaknesses:"
        )

    # List key advantages for the better repository
    advantages = []

    if health_difference >= 0:  # repo1 is better or equal
        if bus_factor_difference > 0:
            advantages.append(f"Higher bus factor (better contributor redundancy)")
        if commits_difference > 0:
            advantages.append(f"More active development (higher commit frequency)")
        if quality_difference > 0:
            advantages.append(f"Better commit quality")
        if velocity_difference > 0:
            advantages.append(f"Faster pull request processing")
        if thoroughness_difference > 0:
            advantages.append(f"More thorough code review")
        if self_merged_difference < 0:  # Lower is better for self-merged
            advantages.append(f"Better independent review practices (lower self-merged ratio)")
    else:  # repo2 is better
        if bus_factor_difference < 0:
            advantages.append(f"Higher bus factor (better contributor redundancy)")
        if commits_difference < 0:
            advantages.append(f"More active development (higher commit frequency)")
        if quality_difference < 0:
            advantages.append(f"Better commit quality")
        if velocity_difference < 0:
            advantages.append(f"Faster pull request processing")
        if thoroughness_difference < 0:
            advantages.append(f"More thorough code review")
        if self_merged_difference > 0:  # Lower is better for self-merged
            advantages.append(f"Better independent review practices (lower self-merged ratio)")

    if advantages:
        sections.append("\n- " + "\n- ".join(advantages) + "\n")

    # Generate specific recommendations for improvement
    sections.append("\n### Specific Recommendations\n")

    if health_difference >= 0:  # repo2 needs more improvements
        recommendations = generate_comparative_recommendations(
            repo2_name, metrics["repo2"]["metrics"], repo1_name, metrics["repo1"]["metrics"]
        )
    else:  # repo1 needs more improvements
        recommendations = generate_comparative_recommendations(
            repo1_name, metrics["repo1"]["metrics"], repo2_name, metrics["repo2"]["metrics"]
        )

    if recommendations:
        sections.append("\n".join(recommendations))
    else:
        sections.append("No specific recommendations identified.")

    # Join all sections
    return "\n".join(sections)


def generate_comparative_recommendations(
    target_repo: str,
    target_metrics: Dict[str, Any],
    reference_repo: str,
    reference_metrics: Dict[str, Any],
) -> List[str]:
    """
    Generate recommendations for a repository based on comparison with another repository.

    Args:
        target_repo: Name of the repository to generate recommendations for
        target_metrics: Metrics for the target repository
        reference_repo: Name of the reference repository (better performing one)
        reference_metrics: Metrics for the reference repository

    Returns:
        List of recommendations
    """
    recommendations = []

    # Contributor recommendations
    bus_factor_diff = reference_metrics.get("contributor", {}).get(
        "bus_factor", 0
    ) - target_metrics.get("contributor", {}).get("bus_factor", 0)
    if bus_factor_diff >= 2:
        recommendations.append(
            f"🔍 **Increase Bus Factor for {target_repo}**: Consider strategies to distribute knowledge and contributions more evenly, as {reference_repo} has a significantly higher bus factor."
        )

    # Commit recommendations
    commit_quality_diff = reference_metrics.get("commit", {}).get("commit_message_quality", {}).get(
        "quality_score", 0
    ) - target_metrics.get("commit", {}).get("commit_message_quality", {}).get("quality_score", 0)
    if commit_quality_diff >= 2:
        recommendations.append(
            f"🔍 **Improve Commit Messages for {target_repo}**: Enhance commit message quality with more descriptive and consistent formatting, following practices similar to {reference_repo}."
        )

    # PR recommendations
    pr_velocity_diff = reference_metrics.get("pull_request", {}).get(
        "pr_velocity_score", 0
    ) - target_metrics.get("pull_request", {}).get("pr_velocity_score", 0)
    if pr_velocity_diff >= 2:
        recommendations.append(
            f"🔍 **Enhance PR Velocity for {target_repo}**: Streamline the pull request process to reduce time to merge and increase throughput, as {reference_repo} demonstrates significantly faster PR processing."
        )

    # Code review recommendations
    self_merged_diff = target_metrics.get("code_review", {}).get(
        "self_merged_ratio", 0
    ) - reference_metrics.get("code_review", {}).get("self_merged_ratio", 0)
    if self_merged_diff >= 0.2:  # 20% difference in self-merged ratio
        recommendations.append(
            f"🔍 **Strengthen Code Review for {target_repo}**: Implement stricter code review policies to ensure independent review before merging, as {reference_repo} has a significantly lower self-merged ratio."
        )

    thoroughness_diff = reference_metrics.get("code_review", {}).get(
        "review_thoroughness_score", 0
    ) - target_metrics.get("code_review", {}).get("review_thoroughness_score", 0)
    if thoroughness_diff >= 2:
        recommendations.append(
            f"🔍 **Improve Review Thoroughness for {target_repo}**: Enhance code review practices to ensure more comprehensive and detailed reviews, following practices similar to {reference_repo}."
        )

    # CI/CD recommendations
    has_ci_ref = reference_metrics.get("ci_cd", {}).get("has_ci", False)
    has_ci_target = target_metrics.get("ci_cd", {}).get("has_ci", False)
    if has_ci_ref and not has_ci_target:
        recommendations.append(
            f"🔍 **Add CI/CD for {target_repo}**: Implement continuous integration similar to {reference_repo} to automate testing and quality checks."
        )

    # Issue recommendations
    responsiveness_diff = reference_metrics.get("issue", {}).get(
        "responsiveness_score", 0
    ) - target_metrics.get("issue", {}).get("responsiveness_score", 0)
    if responsiveness_diff >= 2:
        recommendations.append(
            f"🔍 **Improve Issue Responsiveness for {target_repo}**: Develop a more responsive approach to issue triage and resolution, following practices similar to {reference_repo}."
        )

    # Test recommendations
    has_tests_ref = reference_metrics.get("test", {}).get("has_tests", False)
    has_tests_target = target_metrics.get("test", {}).get("has_tests", False)
    if has_tests_ref and not has_tests_target:
        recommendations.append(
            f"🔍 **Add Tests for {target_repo}**: Implement automated tests similar to {reference_repo} to ensure code quality and prevent regressions."
        )

    return recommendations


def markdown_to_html(markdown_content: str) -> str:
    """
    Convert markdown to HTML (very simple conversion).

    Args:
        markdown_content: Markdown content

    Returns:
        HTML content
    """
    # This is a very basic markdown to HTML converter
    # In a real implementation, we would use a proper markdown parser

    # Convert top-level Markdown headers
    html = re.sub(r"^# (.*?)", r"<h1>\1</h1>", markdown_content, flags=re.MULTILINE)
    html = re.sub(r"^## (.*?)", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^### (.*?)", r"<h3>\1</h3>", html, flags=re.MULTILINE)

    # Convert bold text
    html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html)

    # Convert italic text
    html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html)

    # Convert lists
    html = re.sub(r"^- (.*?)", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"(<li>.*?</li>\n)+", r"<ul>\n\g<0></ul>", html, flags=re.DOTALL)

    # Convert tables (very basic)
    html = re.sub(r"\|(.*?)\|", r"<tr>\1</tr>", html)
    html = re.sub(
        r"<tr>(.*?)</tr>",
        lambda m: "<tr>"
        + "".join(f"<td>{cell.strip()}</td>" for cell in m.group(1).split("|"))
        + "</tr>",
        html,
    )
    html = re.sub(r"(<tr>.*?</tr>\n)+", r"<table>\n\g<0></table>", html, flags=re.DOTALL)

    # Convert images
    html = re.sub(r"!\[(.*?)\]\((.*?)\)", r'<img src="\2" alt="\1">', html)

    # Convert code
    html = re.sub(r"`(.*?)`", r"<code>\1</code>", html)

    # Convert paragraphs
    html = re.sub(r"(?<!\n)\n(?!\n)((?!<h|<ul|<table|<li|<img).)", r"<br>\1", html)
    html = re.sub(r"\n\n((?!<h|<ul|<table).)", r"<p>\1", html)

    return html
