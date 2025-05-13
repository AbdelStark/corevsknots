// src/types/reportTypes.ts

// Basic structure for a user/author
export interface ReportUser {
  login: string;
  id?: number;
  html_url?: string;
  // Add other fields if seen in data, e.g., avatar_url
}

export interface CommitMessageQuality {
  quality_score?: number;
  avg_message_length?: number;
  descriptive_ratio?: number;
}

export interface ContributorMetrics {
  total_contributors?: number;
  active_contributors?: number;
  active_ratio?: number;
  bus_factor?: number;
  contributor_gini?: number;
  contributors_by_commits?: [string, number][]; // [login, count]
  top_contributors?: [string, number][];
  organization_count?: number;
  organization_diversity?: number;
  email_domains?: Record<string, number>;

  // Knots specific (original work)
  knots_original_commit_authors_count?: number;
  core_merge_commit_authors_count?: number;
  knots_contributors_only_merging_core?: number;
  knots_contributors_with_original_work?: number;
  knots_contributors_by_original_commits?: [string, number][];
  knots_top_original_contributors?: [string, number][];
  knots_original_contributor_gini?: number;
  knots_original_bus_factor?: number;
}

export interface CommitMetrics {
  total_commits_in_period?: number;
  original_commits_in_period?: number;
  commits_per_day?: number;
  commits_per_week?: number;
  commits_per_month?: number;
  commit_activity_days?: number;
  commit_activity_ratio?: number;
  commit_frequency?: string;
  avg_commit_size?: number;
  large_commit_ratio?: number;
  commit_message_quality?: CommitMessageQuality;
  unique_authors?: number;
  top_authors?: [string, number][]; // [login, count]
  merge_commit_count?: number;
  merge_commit_ratio?: number;
  commits_by_day?: Record<string, number>; // Day name to count
  commits_by_hour?: Record<string, number>; // Hour (string '0'- '23') to count
  direct_commit_count_git?: number;
  direct_to_original_commit_ratio?: number;
}

export interface PullRequestMetrics {
  total_prs?: number;
  open_prs?: number;
  closed_prs?: number;
  merged_prs?: number;
  open_ratio?: number;
  merged_ratio?: number;
  closed_unmerged_ratio?: number;
  avg_review_count?: number;
  reviewed_pr_ratio?: number;
  self_merged_ratio?: number;
  avg_time_to_merge?: number; // hours
  avg_time_to_close?: number; // hours
  pr_velocity_score?: number;
  avg_pr_size?: number; // lines changed
  large_pr_ratio?: number;
  unique_pr_authors?: number;
  top_pr_authors?: [string, number][]; // [login, count]
  external_pr_ratio?: number;
}

export interface CodeReviewMetrics {
  total_reviews?: number;
  total_review_comments?: number;
  reviews_per_pr?: number;
  comments_per_pr?: number;
  multi_reviewer_ratio?: number;
  substantive_review_ratio?: number;
  review_thoroughness_score?: number;
  unique_reviewers?: number;
  top_reviewers?: [string, number][]; // [login, count]
  reviewer_to_author_ratio?: number;
  avg_time_to_first_review?: number; // hours
  review_responsiveness_score?: number;
  self_merged_count?: number;
  self_merged_ratio?: number; // This one is also in PullRequestMetrics, ensure consistency or pick one source
  self_merged_prs_analyzed?: number;
}

export interface CiCdMetrics {
  has_ci?: boolean;
  total_workflow_runs?: number;
  successful_workflow_runs?: number;
  workflow_success_rate?: number;
  workflows_per_day?: number;
  unique_workflows?: number;
  ci_config_count?: number;
  ci_systems?: string[];
  has_github_actions?: boolean;
  has_travis?: boolean;
  has_circle_ci?: boolean;
  ci_system_count?: number;
  pr_ci_ratio?: number;
  pr_ci_required?: boolean;
  // ci_quality_score?: number | null; // If implemented later
}

export interface IssueMetrics {
  total_issues?: number;
  open_issues?: number;
  closed_issues?: number;
  closed_ratio?: number;
  avg_time_to_close_issue?: number; // hours
  responsiveness_score?: number;
  categorization_score?: number; // Placeholder if you add this
  stale_issue_count?: number;
  stale_issue_ratio?: number;
  bug_report_ratio?: number;
  feature_request_ratio?: number;
  top_issue_reporters?: [string, number][];
  issue_activity_ratio?: number;
}

export interface TestMetrics {
  has_tests?: boolean;
  test_files_count?: number;
  test_lines_count?: number; // If available from git_data
  test_coverage_documented?: number | null; // If found in docs/README
  testing_frameworks?: string[];
  test_to_code_ratio?: number; // Lines or file count based
  testing_practice_score?: number;
}

// Replaces the generic MetricCategory
export interface RepositoryMetrics {
  repository?: {
    name: string;
    analysis_period_months?: number;
    analysis_date?: string;
    github_stars?: number;
    github_forks?: number;
    github_watchers?: number;
    default_branch?: string;
    language?: string;
  };
  overall_health_score?: number;
  contributor?: ContributorMetrics;
  commit?: CommitMetrics;
  pull_request?: PullRequestMetrics;
  code_review?: CodeReviewMetrics;
  ci_cd?: CiCdMetrics;
  issue?: IssueMetrics;
  test?: TestMetrics;
  // Allow other top-level metric categories or metadata
  [key: string]: any;
}

// Comparison structure for specific metric differences
export interface MetricComparisonDetail {
  [key: string]: number | string | undefined | null;
  // e.g. total_contributors_difference?: number;
}

// Structure for the comparison data in the JSON file
export interface ComparisonData {
  repo1: {
    name: string;
    metrics: RepositoryMetrics;
  };
  repo2: {
    name: string;
    metrics: RepositoryMetrics;
  };
  comparison?: {
    overall?: MetricComparisonDetail;
    contributor?: MetricComparisonDetail;
    commit?: MetricComparisonDetail;
    pull_request?: MetricComparisonDetail;
    code_review?: MetricComparisonDetail;
    ci_cd?: MetricComparisonDetail;
    issue?: MetricComparisonDetail;
    test?: MetricComparisonDetail;
    [key: string]: any; // Allow other comparison categories
  };
  analysis_metadata: {
    date: string;
    period_months: number;
    is_fight_mode?: boolean;
  };
}
