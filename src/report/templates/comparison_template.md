# Repository Health Comparison: {{repo1_name}} vs {{repo2_name}}

## Introduction

This report provides a comparative analysis of two repositories in terms of open-source development practices and software quality metrics. The analysis examines contributor activity, commit patterns, pull request workflows, code review processes, CI/CD usage, issue tracking, and test coverage signals.

### Analysis Metadata

| Metric          | Value                                  |
| --------------- | -------------------------------------- |
| Analysis Date   | {{analysis_date}}                      |
| Analysis Period | Last {{analysis_period_months}} months |
| Repository 1    | {{repo1_name}}                         |
| Repository 2    | {{repo2_name}}                         |

## Overall Health Comparison

**{{repo1_name}}**: {{health_score1}}/10

**{{repo2_name}}**: {{health_score2}}/10

{{comparison_text}}

![Overall Health Comparison]({{overall_health_comparison_chart}})

![Category Comparison]({{category_comparison_chart}})

## Contributor Base Comparison

**{{repo1_name}}** has **{{total_contributors1}} contributors** with a bus factor of **{{bus_factor1}}**.

**{{repo2_name}}** has **{{total_contributors2}} contributors** with a bus factor of **{{bus_factor2}}**.

{% if contributor_difference > 0 %}
**{{repo1_name}}** has **{{contributor_difference}} more contributors** than {{repo2_name}}.
{% elif contributor_difference < 0 %}
**{{repo2_name}}** has **{{contributor_difference_abs}} more contributors** than {{repo1_name}}.
{% else %}
Both repositories have the same number of contributors.
{% endif %}

{% if bus_factor_difference > 0 %}
**{{repo1_name}}** has a **higher bus factor** by {{bus_factor_difference}} points, indicating better resilience to contributor departure.
{% elif bus_factor_difference < 0 %}
**{{repo2_name}}** has a **higher bus factor** by {{bus_factor_difference_abs}} points, indicating better resilience to contributor departure.
{% else %}
Both repositories have the same bus factor.
{% endif %}

![Contributor Count Comparison]({{contributor_count_comparison_chart}})

![Bus Factor Comparison]({{bus_factor_comparison_chart}})

## Commit Activity Comparison

**{{repo1_name}}** has **{{commits_per_day1}} commits per day** with a message quality score of **{{message_quality1}}/10**.

**{{repo2_name}}** has **{{commits_per_day2}} commits per day** with a message quality score of **{{message_quality2}}/10**.

{% if commits_difference > 0 %}
**{{repo1_name}}** has **{{commits_difference}} more commits per day** than {{repo2_name}}.
{% elif commits_difference < 0 %}
**{{repo2_name}}** has **{{commits_difference_abs}} more commits per day** than {{repo1_name}}.
{% else %}
Both repositories have the same commit frequency.
{% endif %}

{% if quality_difference > 0 %}
**{{repo1_name}}** has **higher commit message quality** by {{quality_difference}} points.
{% elif quality_difference < 0 %}
**{{repo2_name}}** has **higher commit message quality** by {{quality_difference_abs}} points.
{% else %}
Both repositories have the same commit message quality.
{% endif %}

![Commit Frequency Comparison]({{commit_frequency_comparison_chart}})

![Commit Quality Comparison]({{commit_quality_comparison_chart}})

## Pull Request Process Comparison

**{{repo1_name}}** has a PR merge rate of **{{merged_ratio1}}** with a velocity score of **{{velocity_score1}}/10**.

**{{repo2_name}}** has a PR merge rate of **{{merged_ratio2}}** with a velocity score of **{{velocity_score2}}/10**.

{% if merged_difference > 0 %}
**{{repo1_name}}** has a **higher PR merge rate** by {{merged_difference}}.
{% elif merged_difference < 0 %}
**{{repo2_name}}** has a **higher PR merge rate** by {{merged_difference_abs}}.
{% else %}
Both repositories have the same PR merge rate.
{% endif %}

{% if velocity_difference > 0 %}
**{{repo1_name}}** has a **higher PR velocity score** by {{velocity_difference}} points, indicating faster PR processing.
{% elif velocity_difference < 0 %}
**{{repo2_name}}** has a **higher PR velocity score** by {{velocity_difference_abs}} points, indicating faster PR processing.
{% else %}
Both repositories have the same PR velocity score.
{% endif %}

![PR Velocity Comparison]({{pr_velocity_comparison_chart}})

![PR Merged Ratio Comparison]({{pr_merged_ratio_comparison_chart}})

## Code Review Process Comparison

**{{repo1_name}}** has a review thoroughness score of **{{thoroughness_score1}}/10** with a self-merged ratio of **{{self_merged_ratio1}}**.

**{{repo2_name}}** has a review thoroughness score of **{{thoroughness_score2}}/10** with a self-merged ratio of **{{self_merged_ratio2}}**.

{% if thoroughness_difference > 0 %}
**{{repo1_name}}** has a **higher review thoroughness score** by {{thoroughness_difference}} points, indicating more thorough code reviews.
{% elif thoroughness_difference < 0 %}
**{{repo2_name}}** has a **higher review thoroughness score** by {{thoroughness_difference_abs}} points, indicating more thorough code reviews.
{% else %}
Both repositories have the same review thoroughness score.
{% endif %}

{% if self_merged_difference < 0 %}
**{{repo1_name}}** has a **lower self-merged ratio** by {{self_merged_difference_abs}}, indicating better independent review practices.
{% elif self_merged_difference > 0 %}
**{{repo2_name}}** has a **lower self-merged ratio** by {{self_merged_difference}}, indicating better independent review practices.
{% else %}
Both repositories have the same self-merged ratio.
{% endif %}

![Review Thoroughness Comparison]({{review_thoroughness_comparison_chart}})

![Independent Review Comparison]({{independent_review_comparison_chart}})

## Summary of Key Metrics

| Metric | {{repo1_name}} | {{repo2_name}} | Difference |
| ------ |{{repo1_dashes}}|{{repo2_dashes}}|------------|
| Overall Health Score | {{health_score1}}/10 | {{health_score2}}/10 | {{health_difference}} |
| Total Contributors | {{total_contributors1}} | {{total_contributors2}} | {{contributor_difference}} |
| Bus Factor | {{bus_factor1}} | {{bus_factor2}} | {{bus_factor_difference}} |
| Commits per Day | {{commits_per_day1}} | {{commits_per_day2}} | {{commits_difference}} |
| Commit Message Quality | {{message_quality1}}/10 | {{message_quality2}}/10 | {{quality_difference}} |
| PR Merge Rate | {{merged_ratio1}} | {{merged_ratio2}} | {{merged_difference}} |
| PR Velocity Score | {{velocity_score1}}/10 | {{velocity_score2}}/10 | {{velocity_difference}} |
| Review Thoroughness | {{thoroughness_score1}}/10 | {{thoroughness_score2}}/10 | {{thoroughness_difference}} |
| Self-Merged Ratio | {{self_merged_ratio1}} | {{self_merged_ratio2}} | {{self_merged_difference}} |

## Conclusion and Recommendations

{% if health_difference > 2 %}
**{{repo1_name}}** demonstrates **significantly better repository health** compared to {{repo2_name}}. It excels in several key areas including:
{% elif health_difference > 0 %}
**{{repo1_name}}** demonstrates **moderately better repository health** compared to {{repo2_name}}. It performs better in several areas including:
{% elif health_difference < -2 %}
**{{repo2_name}}** demonstrates **significantly better repository health** compared to {{repo1_name}}. It excels in several key areas including:
{% elif health_difference < 0 %}
**{{repo2_name}}** demonstrates **moderately better repository health** compared to {{repo1_name}}. It performs better in several areas including:
{% else %}
Both repositories demonstrate **similar overall health**, though they have different strengths and weaknesses:
{% endif %}

{% for advantage in advantages %}

- {{advantage}}
  {% endfor %}

### Specific Recommendations

{% for recommendation in recommendations %}

- {{recommendation}}
  {% endfor %}
