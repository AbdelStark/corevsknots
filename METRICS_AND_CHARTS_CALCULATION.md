# Metrics and Charts Calculation Documentation

This document details how various metrics and charts are computed within the Bitcoin Repository Health Analysis Tool.

## 1. Data Sources

The primary data sources for the analysis are:

- **GitHub API**: Used to fetch most of the repository metadata, including:
  - Repository information (stars, forks, default branch, etc.)
  - Commit history (SHA, author, committer, message, timestamps)
  - Pull Requests (details, states, user, timestamps, merge details)
  - Issues (details, states, user, timestamps, comments)
  - Contributors (list of users who contributed to the repository)
  - CI/CD workflow runs (status, conclusions, timings) - via commit statuses and check runs.
  - Release information (not currently heavily used but available).
- **Git CLI (or local Git repository analysis)**: Used to gather information that might be more accurate or detailed when analyzing a local clone, such as:
  - Precise commit counts and author details (especially email for organizational diversity).
  - File changes and commit sizes (if `git log --numstat` or similar is used).
  - Test file identification (by searching for common test patterns in filenames).
  - CI/CD configuration file detection (e.g., `.github/workflows`, `Jenkinsfile`).

The tool can operate solely on GitHub API data but benefits from having a local clone (either provided or cloned temporarily) for more in-depth Git-based metrics. For the Rust data loader, the goal is to pre-populate a local database with all this information.

## 2. Metric Calculation

Metrics are grouped into several categories. Each category's calculation is detailed below.

### 2.1. Contributor Metrics (`contributor.py`)

These metrics focus on the diversity, activity, and distribution of work among contributors.

- **`total_contributors`**: Total number of unique contributors listed by the GitHub API (`/contributors` endpoint).
- **`contributors_by_commits`**: A list of contributors sorted by their total contribution count (from GitHub API).
- **`top_contributors`**: The top 10 contributors from `contributors_by_commits`.
- **`active_contributors`**: Number of unique authors who made at least one commit within the analysis period (derived from GitHub API commit data).
  - An author is identified by `commit.author.login` or, if not available, `commit.commit.author.name`.
- **`active_ratio`**: `active_contributors` / `total_contributors`.
- **Gini Coefficient (`contributor_gini`)**: Measures the inequality of commit distribution among contributors. Calculated using the `calculate_gini_coefficient` function, which takes a list of commit counts per contributor.
  - A Gini coefficient of 0 means perfect equality (all contributors made the same number of commits).
  - A Gini coefficient of 1 means perfect inequality (one contributor made all the commits).
  - For non-Knots repositories, this is calculated based on commit counts per author for commits that are NOT identified as upstream merge commits (using `is_core_merge_commit` heuristic).
  - For all repositories, a general Gini is also calculated based on the overall `/contributors` API endpoint data if the specific Gini isn't already set.
- **Bus Factor (`bus_factor`)**: Estimates the minimum number of contributors whose departure would critically impact the project. Calculated using `calculate_bus_factor`.
  - It's defined as the minimum number of contributors whose cumulative contributions account for 80% of all contributions in the analyzed period.
  - Contribution counts are from the same source as the Gini coefficient (original commits for non-Knots, general GH API for all if not set).
- **Organizational Diversity**:
  - **`email_domains`**: A dictionary mapping email domains (e.g., `gmail.com`) to the count of contributors from that domain.
    - For Bitcoin Knots (when `is_knots_repo` is true), this uses emails of authors who made _original_ Knots commits.
    - For other repositories (like Bitcoin Core), this uses email data from `git_data["contributors"]` if available (which implies local git log analysis).
  - **`organization_count`**: The number of unique email domains found.
  - **`organization_diversity`**: A Shannon entropy score calculated on the distribution of contributors across different email domains, normalized to a [0, 1] scale. Higher values indicate more diversity.

#### Fork-Specific Logic for Bitcoin Knots (vs. Bitcoin Core)

When `repo_name` is `bitcoinknots/bitcoin` and `core_commit_shas` (a set of commit SHAs from Bitcoin Core for the same period) is provided:

- **`is_core_merge_commit(commit_message)`**: A helper function to heuristically identify commits that are likely merges from Bitcoin Core based on common merge commit message patterns (e.g., "Merge bitcoin/bitcoin#", "Merge remote-tracking branch 'upstream/master'").
- **Original vs. Merged Commits for Knots**:
  - Commits in Knots are classified as either "original Knots work" or "merged from Core".
  - A Knots commit is considered "merged from Core" if its SHA is in `core_commit_shas` OR its message matches `is_core_merge_commit()`.
- **`knots_original_commit_authors`**: Set of authors who made at least one original commit to Knots.
- **`core_merge_commit_authors`**: Set of authors who made at least one commit identified as a merge from Core into Knots.
- **`knots_author_original_commit_counts`**: Counter for original commits per author in Knots.
- **`knots_original_commit_authors_count`**: Count of unique authors with original Knots commits.
- **`core_merge_commit_authors_count`**: Count of unique authors involved in merging Core commits into Knots.
- **`knots_contributors_only_merging_core`**: Number of authors who _only_ merged Core changes and had no original Knots commits in the period.
- **`knots_contributors_with_original_work`**: Same as `knots_original_commit_authors_count`.
- **`knots_contributors_by_original_commits`**: List of Knots authors sorted by their original commit counts.
- **`knots_top_original_contributors`**: Top 10 original Knots contributors.
- **`knots_original_contributor_gini`**: Gini coefficient calculated _only_ on the distribution of original Knots commits among Knots authors.
- **`knots_original_bus_factor`**: Bus factor calculated _only_ based on original Knots commits.
- **`knots_original_author_emails`**: Set of emails from authors of original Knots commits, used for calculating Knots-specific organizational diversity.

### 2.2. Commit Metrics (`commits.py`)

These metrics focus on the frequency, size, quality, and authorship of commits. For Bitcoin Knots in a comparison, these metrics are calculated based on _original Knots commits_ (commits not identified as merges from Bitcoin Core).

- **`total_commits_in_period`**: Total number of commits fetched from the GitHub API for the repository within the analysis period.
- **`original_commits_in_period`**: Number of commits used for metric calculation after filtering. For Knots, this excludes Core merges. For Core, it excludes commits matching `is_core_merge_commit` patterns. For other repos, it's same as `total_commits_in_period`.
- **Commit Frequency (`calculate_commit_frequency`)**: Based on `original_commits_in_period`.
  - **`commits_per_day`**: Average commits per day over the timespan of the analyzed commits.
  - **`commits_per_week`**: `commits_per_day` \* 7.
  - **`commits_per_month`**: `commits_per_day` \* 30.
  - **`commit_activity_days`**: Number of distinct days on which commits were made.
  - **`commit_activity_ratio`**: `commit_activity_days` / total days in the analyzed commit timespan.
  - **`commit_frequency`**: A categorical assessment ("very_active", "active", "moderate", "low", "inactive") based on `commits_per_day`.
- **Commit Size (`calculate_commit_size_metrics`)**: Based on `stats` (additions, deletions) in GitHub API commit data for `original_commits_in_period`.
  - **`avg_commit_size`**: Average total lines changed (additions + deletions) per commit.
  - **`large_commit_ratio`**: Proportion of commits with more than 300 total lines changed.
- **Commit Message Quality (`analyze_commit_messages`)**: Based on `original_commits_in_period`.
  - **`avg_message_length`**: Average length of the first line of commit messages.
  - **`descriptive_ratio`**: Proportion of commit messages whose first line has more than 5 words.
  - **`quality_score`**: A score (0-10) derived from `avg_message_length` (up to 50 chars = 10 pts) and `descriptive_ratio` (ratio \* 10), averaged.
- **Commit Authorship (`analyze_commit_authorship`)**: Based on `original_commits_in_period`.
  - **`unique_authors`**: Number of unique commit authors (GitHub login or commit author name).
  - **`top_authors`**: Top 5 authors by number of original commits.
- **Merge Commits (`analyze_merge_commits`)**: Analyzes merge commits _within the set of `original_commits_in_period`_. This means for Knots, it looks for merges of Knots feature branches, not Core merges.
  - **`merge_commit_count`**: Number of commits whose messages start with "Merge" and contain "pull request", "branch", or "into".
  - **`merge_commit_ratio`**: `merge_commit_count` / count of `original_commits_in_period`.
- **Commit Activity Patterns (`analyze_commit_activity_patterns`)**: Based on `original_commits_in_period`.
  - **`commits_by_day`**: Dictionary mapping day of the week (e.g., "Monday") to the number of commits made on that day.
  - **`commits_by_hour`**: Dictionary mapping hour of the day (0-23) to the number of commits made in that hour.
- **Git Data Specific (if `git_data` is available)**:
  - **`direct_commit_count_git`**: Count of commits made directly to a main branch (from `git_data`).
  - **`direct_to_original_commit_ratio`**: `direct_commit_count_git` / `original_commits_in_period` count.

### 2.3. Pull Request Metrics (`pull_requests.py`)

These metrics analyze the lifecycle, review process, and characteristics of pull requests (PRs).

- **`total_prs`**: Total number of PRs fetched from the GitHub API for the analysis period.
- **PR State Distribution (`calculate_pr_state_distribution`)**: Based on all fetched PRs.
  - **`open_prs`**: Number of PRs currently in the "open" state.
  - **`closed_prs`**: Number of PRs in the "closed" state (can be merged or unmerged).
  - **`merged_prs`**: Number of PRs that have been merged (identified by `pr.get("merged")` being true).
  - **`open_ratio`**: `open_prs` / `total_prs`.
  - **`merged_ratio`**: `merged_prs` / `total_prs`.
  - **`closed_unmerged_ratio`**: (`closed_prs` - `merged_prs`) / `total_prs`. This represents PRs that were closed without being merged.
- **PR Review Metrics (`calculate_pr_review_metrics`)**: Based on fetched PRs and associated review/comment data (`github_data["pr_reviews"]`, `github_data["pr_comments"]`).
  - **`avg_review_count`**: Average number of reviews per PR. This counts distinct review submissions from the `pr_reviews` data. If a PR has comments from `pr_comments` but no formal reviews, it's counted as having 1 review.
  - **`reviewed_pr_ratio`**: Proportion of PRs that have at least one review or comment.
  - **`self_merged_ratio`**: Proportion of _merged_ PRs that were merged by the PR author themselves (`pr.merged_by.login == pr.author.login`).
- **PR Lifecycle Metrics (`calculate_pr_lifecycle_metrics`)**: Based on timestamps of fetched PRs.
  - **`avg_time_to_merge`**: Average time in hours from PR creation to PR merging for all merged PRs.
  - **`avg_time_to_close`**: Average time in hours from PR creation to PR closing for PRs that were closed _without_ being merged.
  - **`pr_velocity_score`**: A score (0-10) based on `avg_time_to_merge`. Shorter times get higher scores (e.g., <=24h is 10, 7 days is ~5, 30 days is ~1).
- **PR Size Metrics (`calculate_pr_size_metrics`)**: Based on `additions` and `deletions` fields in PR data.
  - **`avg_pr_size`**: Average total lines changed (additions + deletions) per PR.
  - **`large_pr_ratio`**: Proportion of PRs with more than 1000 total lines changed.
- **PR Author Distribution (`calculate_pr_author_distribution`)**:
  - **`unique_pr_authors`**: Number of unique authors who created PRs.
  - **`top_pr_authors`**: Top 5 authors by number of PRs created.
  - **`external_pr_ratio`**: Proportion of PRs submitted by authors who are not repository "OWNER", "MEMBER", or "COLLABORATOR" (based on `pr.author_association`).

### 2.4. Code Review Metrics (`code_review.py`)

These metrics assess the volume, thoroughness, diversity, and responsiveness of the code review process. They primarily use data from `github_data["pr_reviews"]` (formal review submissions) and `github_data["pr_comments"]` (general PR comments).

- **Review Volume (`calculate_review_volume_metrics`)**: Based on PRs with review data.
  - **`total_reviews`**: Total number of formal review submissions across all PRs in the sample.
  - **`total_review_comments`**: Total number of individual review comments (line comments, single comments) across all PRs in the sample.
  - **`reviews_per_pr`**: Average number of formal review submissions per PR (among PRs with review data).
  - **`comments_per_pr`**: Average number of review comments per PR (among PRs with review data).
- **Review Thoroughness (`calculate_review_thoroughness_metrics`)**: Based on PRs with review data.
  - **`multi_reviewer_ratio`**: Proportion of PRs (in the review sample) that have more than one unique reviewer (based on `review.user.login`).
  - **`substantive_review_ratio`**: Proportion of PRs (in the review sample) that either received 3+ review comments OR had a review state of `CHANGES_REQUESTED`.
  - **`review_thoroughness_score`**: A score (0-10) calculated as `multi_reviewer_ratio * 5 + substantive_review_ratio * 5`.
- **Review Diversity (`calculate_review_diversity_metrics`)**: Based on PRs with review data and their authors.
  - **`unique_reviewers`**: Total number of unique individuals who submitted reviews or PR comments.
  - **`top_reviewers`**: Top 5 reviewers by count of reviews/comments submitted.
  - **`reviewer_to_author_ratio`**: `unique_reviewers` / number of unique PR authors (for PRs in the review sample).
- **Review Responsiveness (`calculate_review_responsiveness_metrics`)**: Based on PRs with review data.
  - **`avg_time_to_first_review`**: Average time in hours from PR creation to the submission of the first formal review.
  - **`review_responsiveness_score`**: A score (0-10) based on `avg_time_to_first_review`. Shorter times get higher scores (e.g., <=2h is 10, 24h is ~7, 3 days is ~3).
- **Self-Merge Metrics (`calculate_self_merge_metrics`)**: Analyzes PRs that were merged.
  - **`self_merged_count`**: Number of merged PRs where the merger is the same as the PR author.
    - This checks `pr.merged_by.login == pr.user.login`.
    - If `merged_by` is null, it attempts to fetch the merge commit details using the `github_client` and checks if the merge commit's author or committer matches the PR author.
  - **`self_merged_ratio`**: `self_merged_count` / total number of merged PRs analyzed for self-merging.
  - **`self_merged_prs_analyzed`**: Number of merged PRs for which self-merge status could be determined.

---
