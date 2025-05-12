# Repository Health Report: {{repo_name}}

## Introduction

This report provides a comprehensive analysis of the repository's health based on open-source development practices and software quality metrics. The analysis examines contributor activity, commit patterns, pull request workflows, code review processes, CI/CD usage, issue tracking, and test coverage signals.

### Analysis Metadata

| Metric          | Value                                  |
| --------------- | -------------------------------------- |
| Repository      | {{repo_name}}                          |
| Analysis Date   | {{analysis_date}}                      |
| Analysis Period | Last {{analysis_period_months}} months |

## Overall Health Score

**Overall Health Score**: {{overall_health_score}}/10 ({{health_rating}})

![Overall Health Score]({{overall_health_chart}})

![Health by Category]({{health_by_category_chart}})

## Contributor Base and Activity

The repository has **{{total_contributors}} total contributors**, with **{{active_contributors}} active contributors** in the last {{analysis_period_months}} months ({{active_ratio}} activity ratio).

The repository has a **bus factor of {{bus_factor}}**, meaning that's how many contributors would need to leave before the project would be in serious trouble.

{% if bus_factor >= 5 %}
🟢 **Good**: The repository has a healthy bus factor, reducing the risk of project disruption if key contributors leave.
{% elif bus_factor >= 2 %}
🟡 **Moderate**: The repository has some contributor redundancy but could improve its bus factor to reduce risk.
{% else %}
🔴 **Poor**: The repository has a dangerously low bus factor, creating significant risk if key contributors leave.
{% endif %}

![Top Contributors]({{top_contributors_chart}})

![Bus Factor]({{bus_factor_chart}})

## Commit Activity and Patterns

The repository shows **{{commit_frequency}}** commit patterns with **{{commits_per_day}} commits per day** (approximately {{commits_per_week}} per week).

**Commit Message Quality**: {{commit_message_quality}}/10

**Merge Commit Ratio**: {{merge_commit_ratio}} of commits are merge commits.

{% if commits_per_day >= 3 %}
🟢 **Good**: The repository shows high commit activity, indicating active development.
{% elif commits_per_day >= 1 %}
🟡 **Moderate**: The repository shows regular commit activity.
{% else %}
🔴 **Low**: The repository shows minimal commit activity, possibly indicating a less active project.
{% endif %}

![Commits by Day]({{commits_by_day_chart}})

![Commits by Hour]({{commits_by_hour_chart}})

![Commit Message Quality]({{commit_message_quality_chart}})

## Pull Request Practices

The repository has processed **{{total_prs}} pull requests** in the analysis period, with a **merge rate of {{merged_ratio}}**.

**Average Time to Merge**: {{time_to_merge}}

**PR Velocity Score**: {{pr_velocity_score}}/10

{% if merged_ratio >= 0.7 and pr_velocity_score >= 7 %}
🟢 **Good**: The repository has an efficient pull request process with high throughput and quick turnaround.
{% elif merged_ratio >= 0.5 and pr_velocity_score >= 4 %}
🟡 **Moderate**: The repository has a functional pull request process but could improve efficiency.
{% else %}
🔴 **Poor**: The repository has an inefficient pull request process with potential bottlenecks.
{% endif %}

![PR State Distribution]({{pr_state_distribution_chart}})

![PR Velocity]({{pr_velocity_chart}})

## Code Review Process

The repository averages **{{reviews_per_pr}} reviews per pull request** with **{{comments_per_pr}} comments per pull request**.

**Review Thoroughness Score**: {{review_thoroughness_score}}/10

**Self-Merged Ratio**: {{self_merged_ratio}} of merged PRs are merged by the author (without independent review).

{% if review_thoroughness_score >= 7 and self_merged_ratio <= 0.2 %}
🟢 **Good**: The repository has a thorough code review process with strong independent oversight.
{% elif review_thoroughness_score >= 4 and self_merged_ratio <= 0.5 %}
🟡 **Moderate**: The repository has a functional code review process but could improve thoroughness.
{% else %}
🔴 **Poor**: The repository has a weak code review process with limited independent oversight.
{% endif %}

![Review Thoroughness]({{review_thoroughness_chart}})

![Independent Review Rate]({{independent_review_chart}})

## Continuous Integration and Deployment

{% if has_ci %}
The repository uses continuous integration with a **workflow success rate of {{workflow_success_rate}}**.

**CI Systems Used**: {{ci_systems}}

{% if workflow_success_rate >= 0.9 %}
🟢 **Good**: The repository has a reliable CI/CD pipeline with high success rates.
{% elif workflow_success_rate >= 0.7 %}
🟡 **Moderate**: The repository has a functional CI/CD pipeline but could improve reliability.
{% else %}
🔴 **Poor**: The repository has an unreliable CI/CD pipeline with frequent failures.
{% endif %}

![CI Success Rate]({{ci_success_rate_chart}})
{% else %}
❌ **No Continuous Integration Found**: The repository does not appear to use CI/CD.
{% endif %}

## Issue Tracking and Management

The repository has **{{total_issues}} total issues** ({{open_issues}} open, {{closed_issues}} closed).

**Issue Responsiveness Score**: {{responsiveness_score}}/10

**Stale Issues**: {{stale_issues}} open issues have not been updated in over 30 days.

{% if responsiveness_score >= 7 and stale_issues <= open_issues * 0.1 %}
🟢 **Good**: The repository has a responsive issue management process with few stale issues.
{% elif responsiveness_score >= 4 and stale_issues <= open_issues * 0.3 %}
🟡 **Moderate**: The repository has a functional issue management process but could improve responsiveness.
{% else %}
🔴 **Poor**: The repository has a weak issue management process with many stale issues.
{% endif %}

![Issue State Distribution]({{issue_state_distribution_chart}})

![Issue Responsiveness]({{issue_responsiveness_chart}})

## Testing Practices

{% if has_tests %}
The repository has **{{test_files_count}} test files** with a testing practice score of {{testing_practice_score}}/10.

{% if testing_practice_score >= 7 %}
🟢 **Good**: The repository has a strong testing practice with comprehensive test coverage.
{% elif testing_practice_score >= 4 %}
🟡 **Moderate**: The repository has a functional testing practice but could improve coverage.
{% else %}
🔴 **Poor**: The repository has limited testing practices with room for improvement.
{% endif %}
{% else %}
❌ **No Tests Found**: The repository does not appear to have automated tests.
{% endif %}

## Conclusion and Recommendations

{% if overall_health_score >= 7 %}
Overall, this repository demonstrates **good health** with strong development practices. It follows many open-source and software development best practices, suggesting a mature and well-maintained project.
{% elif overall_health_score >= 4 %}
Overall, this repository demonstrates **moderate health** with reasonable development practices. While it follows some best practices, there are areas for improvement to enhance project quality and sustainability.
{% else %}
Overall, this repository demonstrates **poor health** with concerning development practices. Significant improvements are needed in several areas to enhance project quality and sustainability.
{% endif %}

### Specific Recommendations

{% for recommendation in recommendations %}

- {{recommendation}}
  {% endfor %}
