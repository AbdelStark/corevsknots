use crate::errors::{DataError, Result};
use chrono::{DateTime, Utc};
use reqwest::blocking::Client;
use reqwest::header::{ACCEPT, AUTHORIZATION, USER_AGENT};
use serde::Deserialize;
use std::time::Duration;

const GITHUB_API_BASE_URL: &str = "https://api.github.com";

#[derive(Deserialize, Debug, Clone)]
pub struct GitHubUser {
    pub login: String,
    pub id: i64,
    // Add other user fields if needed e.g., type, avatar_url
}

#[derive(Deserialize, Debug, Clone)]
pub struct CommitAuthor {
    pub name: Option<String>,
    pub email: Option<String>,
    pub date: Option<DateTime<Utc>>,
}

#[derive(Deserialize, Debug, Clone)]
pub struct GitCommit {
    pub author: Option<CommitAuthor>,
    pub committer: Option<CommitAuthor>,
    pub message: Option<String>,
    // pub tree: Option<GitTree>,
    pub url: Option<String>,
    pub comment_count: Option<i64>,
}

#[derive(Deserialize, Debug, Clone)]
pub struct GitHubCommit {
    pub sha: String,
    pub commit: GitCommit,
    pub url: String, // API URL for this commit
    pub html_url: String,
    pub comments_url: String,
    pub author: Option<GitHubUser>, // GitHub user if available
    pub committer: Option<GitHubUser>, // GitHub user if available
                                    // pub parents: Vec<CommitParent>,
                                    // pub stats: Option<CommitStats>,
}

#[derive(Deserialize, Debug)]
pub struct RepoInfo {
    pub id: i64,
    pub name: String,
    pub full_name: String,
    pub description: Option<String>,
    pub html_url: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub pushed_at: DateTime<Utc>,
    pub stargazers_count: i32,
    pub watchers_count: i32,
    pub forks_count: i32,
    pub open_issues_count: i32,
    pub default_branch: String,
    pub language: Option<String>,
    // Add more fields as needed, e.g., license
}

#[derive(Deserialize, Debug, Clone)]
pub struct GitHubPullRequest {
    pub id: i64,
    pub number: i64,
    pub html_url: String,
    pub state: String, // e.g., "open", "closed"
    pub title: String,
    pub user: Option<GitHubUser>,
    pub body: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub closed_at: Option<DateTime<Utc>>,
    pub merged_at: Option<DateTime<Utc>>,
    pub merge_commit_sha: Option<String>,
    // pub assignee: Option<GitHubUser>,
    // pub assignees: Vec<GitHubUser>,
    // pub requested_reviewers: Vec<GitHubUser>,
    // pub labels: Vec<GitHubLabel>,
    // pub head: Option<BranchInfo>,
    // pub base: Option<BranchInfo>,
    // pub comments: Option<i64>, // Often needs separate fetch
    // pub review_comments: Option<i64>, // Often needs separate fetch
    // pub commits: Option<i64>, // Often needs separate fetch
    // pub additions: Option<i64>, // Often needs separate fetch
    // pub deletions: Option<i64>, // Often needs separate fetch
    // pub changed_files: Option<i64>, // Often needs separate fetch
    pub merged: Option<bool>,
    pub mergeable: Option<bool>,
    pub rebaseable: Option<bool>,
    pub mergeable_state: Option<String>,
    pub merged_by: Option<GitHubUser>,
    pub comments_url: String,
    pub review_comments_url: String,
    pub statuses_url: String,
}

#[derive(Deserialize, Debug, Clone)]
pub struct GitHubIssue {
    pub id: i64,
    pub number: i64,
    pub html_url: String,
    pub state: String, // "open" or "closed"
    pub title: String,
    pub user: Option<GitHubUser>,
    pub labels: Vec<GitHubLabel>, // Assuming GitHubLabel struct exists or will be added
    pub assignee: Option<GitHubUser>,
    pub assignees: Vec<GitHubUser>,
    pub locked: bool,
    pub comments: i64,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub closed_at: Option<DateTime<Utc>>,
    pub body: Option<String>,
    pub closed_by: Option<GitHubUser>,
    // pub pull_request: Option<IssuePullRequest>, // Link if issue is also a PR
}

#[derive(Deserialize, Debug, Clone)] // Simple label struct
pub struct GitHubLabel {
    pub id: i64,
    pub name: String,
    pub color: String,
    pub description: Option<String>,
}

#[derive(Deserialize, Debug, Clone)]
pub struct GitHubContributor {
    pub login: String,
    pub id: i64,
    pub contributions: i64,
    #[serde(rename = "type")] // Rename to avoid keyword conflict
    pub contributor_type: String, // e.g., "User", "Bot"
    pub html_url: String,
    // Add other fields if needed (avatar_url, etc.)
}

pub struct GitHubClient {
    client: Client,
    token: Option<String>,
}

impl GitHubClient {
    pub fn new(token: Option<String>) -> Result<Self> {
        let client = Client::builder().timeout(Duration::from_secs(30)).build()?;
        Ok(Self { client, token })
    }

    fn get<T: for<'de> Deserialize<'de>>(&self, url: &str) -> Result<T> {
        log::debug!("Sending GET request to: {}", url);
        let mut request_builder = self
            .client
            .get(url)
            .header(USER_AGENT, "corevsknots-data-loader")
            .header(ACCEPT, "application/vnd.github.v3+json");

        if let Some(token) = &self.token {
            request_builder = request_builder.header(AUTHORIZATION, format!("token {}", token));
        }

        let response = request_builder.send()?;

        if response.status().is_success() {
            let body = response.json::<T>()?;
            Ok(body)
        } else {
            let status = response.status();
            let error_text = response
                .text()
                .unwrap_or_else(|_| "Failed to read error body".to_string());
            log::error!("GitHub API Error: {} - {}", status, error_text);
            if status == reqwest::StatusCode::FORBIDDEN
                && error_text.contains("rate limit exceeded")
            {
                Err(DataError::RateLimitError)
            } else if status == reqwest::StatusCode::NOT_FOUND {
                Err(DataError::NotFoundError)
            } else {
                Err(DataError::GitHubApiError {
                    status,
                    message: error_text,
                })
            }
        }
    }

    fn get_paginated<T: for<'de> Deserialize<'de> + Clone>(&self, url: &str) -> Result<Vec<T>> {
        let mut all_items: Vec<T> = Vec::new();
        let mut next_page_url = Some(url.to_string());
        let per_page = 100; // Max allowed by GitHub

        while let Some(current_url) = next_page_url {
            let full_url = format!("{}?per_page={}", current_url, per_page);
            log::debug!("Fetching paginated data from: {}", full_url);

            let mut request_builder = self
                .client
                .get(&full_url)
                .header(USER_AGENT, "corevsknots-data-loader")
                .header(ACCEPT, "application/vnd.github.v3+json");

            if let Some(token) = &self.token {
                request_builder = request_builder.header(AUTHORIZATION, format!("token {}", token));
            }

            let response = request_builder.send()?;

            if !response.status().is_success() {
                let status = response.status();
                let error_text = response
                    .text()
                    .unwrap_or_else(|_| "Failed to read error body".to_string());
                log::error!(
                    "GitHub API Error on paginated request: {} - {}",
                    status,
                    error_text
                );
                return if status == reqwest::StatusCode::FORBIDDEN
                    && error_text.contains("rate limit exceeded")
                {
                    Err(DataError::RateLimitError)
                } else if status == reqwest::StatusCode::NOT_FOUND {
                    Err(DataError::NotFoundError)
                } else {
                    Err(DataError::GitHubApiError {
                        status,
                        message: error_text,
                    })
                };
            }

            // Extract next page URL from Link header
            next_page_url = response
                .headers()
                .get(reqwest::header::LINK)
                .and_then(|link_header| link_header.to_str().ok())
                .and_then(parse_link_header);

            let items = response.json::<Vec<T>>()?;
            if items.is_empty() {
                break; // No more items to fetch
            }
            all_items.extend(items.into_iter());
        }
        Ok(all_items)
    }

    pub fn get_repo_info(&self, repo_owner: &str, repo_name: &str) -> Result<RepoInfo> {
        let url = format!("{}/repos/{}/{}", GITHUB_API_BASE_URL, repo_owner, repo_name);
        self.get(&url)
    }

    // Fetches commits for a repository.
    // `since` and `until` should be ISO 8601 timestamps (YYYY-MM-DDTHH:MM:SSZ)
    pub fn get_commits(
        &self,
        repo_owner: &str,
        repo_name: &str,
        since: Option<String>,
        until: Option<String>,
        branch_or_sha: Option<String>,
    ) -> Result<Vec<GitHubCommit>> {
        let mut url = format!(
            "{}/repos/{}/{}/commits",
            GITHUB_API_BASE_URL, repo_owner, repo_name
        );
        let mut params: Vec<String> = Vec::new();
        if let Some(s) = since {
            params.push(format!("since={}", s));
        }
        if let Some(u) = until {
            params.push(format!("until={}", u));
        }
        if let Some(b) = branch_or_sha {
            params.push(format!("sha={}", b));
        }

        if !params.is_empty() {
            url.push('?');
            url.push_str(&params.join("&"));
        }
        self.get_paginated(&url)
    }

    // Fetches pull requests for a repository.
    // state can be "open", "closed", or "all"
    // sort can be "created", "updated", "popularity", "long-running"
    // direction can be "asc" or "desc"
    pub fn get_pull_requests(
        &self,
        repo_owner: &str,
        repo_name: &str,
        state: Option<String>,
        sort: Option<String>,
        direction: Option<String>,
    ) -> Result<Vec<GitHubPullRequest>> {
        let mut url = format!(
            "{}/repos/{}/{}/pulls",
            GITHUB_API_BASE_URL, repo_owner, repo_name
        );
        let mut params: Vec<String> = Vec::new();
        // Default state is open, but let's fetch all initially for comprehensive data
        params.push(format!(
            "state={}",
            state.unwrap_or_else(|| "all".to_string())
        ));
        if let Some(s) = sort {
            params.push(format!("sort={}", s));
        }
        if let Some(d) = direction {
            params.push(format!("direction={}", d));
        }

        if !params.is_empty() {
            url.push('?');
            url.push_str(&params.join("&"));
        }
        self.get_paginated(&url)
    }

    // Fetches issues for a repository.
    // state can be "open", "closed", or "all"
    // filter can be "assigned", "created", "mentioned", "subscribed", "all"
    // since: ISO 8601 timestamp
    pub fn get_issues(
        &self,
        repo_owner: &str,
        repo_name: &str,
        state: Option<String>,
        filter: Option<String>,
        since: Option<String>,
    ) -> Result<Vec<GitHubIssue>> {
        let mut url = format!(
            "{}/repos/{}/{}/issues",
            GITHUB_API_BASE_URL, repo_owner, repo_name
        );
        let mut params: Vec<String> = Vec::new();
        // Default state is open, let's fetch all for comprehensive data
        params.push(format!(
            "state={}",
            state.unwrap_or_else(|| "all".to_string())
        ));
        if let Some(f) = filter {
            params.push(format!("filter={}", f));
        }
        if let Some(s) = since {
            params.push(format!("since={}", s));
        }

        if !params.is_empty() {
            url.push('?');
            url.push_str(&params.join("&"));
        }

        self.get_paginated(&url)
    }

    // Fetches contributors for a repository.
    // Includes anonymous contributors if `anon=true` is added (might require different parsing)
    pub fn get_contributors(
        &self,
        repo_owner: &str,
        repo_name: &str,
    ) -> Result<Vec<GitHubContributor>> {
        let url = format!(
            "{}/repos/{}/{}/contributors",
            GITHUB_API_BASE_URL, repo_owner, repo_name
        );
        // Add `?anon=true` if needed
        self.get_paginated(&url)
        // Note: This might return an empty vec even on success if contrib data is not ready
        // GitHub docs mention a 202 Accepted response sometimes.
        // Need robust handling if contributor data is critical.
    }
}

// Helper function to parse GitHub's Link header for pagination
fn parse_link_header(link_header: &str) -> Option<String> {
    link_header.split(',').find_map(|link_part| {
        let parts: Vec<&str> = link_part.split(';').map(str::trim).collect();
        if parts.len() == 2 && parts[1] == "rel=\"next\"" {
            parts[0]
                .trim_start_matches('<')
                .trim_end_matches('>')
                .to_string()
                .into()
        } else {
            None
        }
    })
}

// TODO: Add functions to fetch PRs, Issues, Reviews, Comments, Contributors, etc.
// Each will need its own struct for deserialization and potentially specific query parameters.
