// src/types/reportTypes.ts

// Basic structure for a user/author
export interface ReportUser {
  login: string;
  id?: number;
  // Add other fields if seen in data, e.g., avatar_url, html_url
}

// Metrics for a specific category (e.g., contributor, commit, pull_request)
export interface MetricCategory {
  // General metrics
  total_contributors?: number;
  active_contributors?: number;
  bus_factor?: number;
  contributor_gini?: number;
  organization_count?: number;
  organization_diversity?: number;

  commits_per_day?: number;
  commit_frequency?: string;
  commit_message_quality?: { quality_score?: number };
  merge_commit_ratio?: number;
  avg_commit_size?: number;

  total_prs?: number;
  merged_ratio?: number;
  avg_time_to_merge?: number;
  pr_velocity_score?: number;

  reviews_per_pr?: number;
  comments_per_pr?: number;
  review_thoroughness_score?: number;
  self_merged_ratio?: number;

  has_ci?: boolean;
  workflow_success_rate?: number;

  total_issues?: number;
  responsiveness_score?: number;
  categorization_score?: number; // Example, adapt if different
  stale_issue_ratio?: number;

  has_tests?: boolean;
  testing_practice_score?: number;

  // Knots specific (original work)
  knots_original_bus_factor?: number;
  knots_original_contributor_gini?: number;
  knots_contributors_with_original_work?: number;
  knots_contributors_only_merging_core?: number;
  core_merge_commit_authors_count?: number;

  // Add other specific metric fields as needed based on the JSON structure
  [key: string]: any; // Allow other properties
}

// Structure for a single repository's full metrics set
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
  contributor?: MetricCategory;
  commit?: MetricCategory;
  pull_request?: MetricCategory;
  code_review?: MetricCategory;
  ci_cd?: MetricCategory;
  issue?: MetricCategory;
  test?: MetricCategory;
  // Allow other top-level metric categories or metadata
  [key: string]: any;
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
    // Example comparison fields - expand as needed
    overall?: { health_score_difference?: number };
    contributor?: {
      total_contributors_difference?: number;
      bus_factor_difference?: number;
    };
    commit?: {
      commits_per_day_difference?: number;
      quality_score_difference?: number;
    };
    // Add other comparison categories and fields
    [key: string]: any;
  };
  analysis_metadata: {
    date: string;
    period_months: number;
    is_fight_mode?: boolean;
  };
}
