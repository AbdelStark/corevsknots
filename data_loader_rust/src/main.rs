pub mod config;
pub mod db;
pub mod errors;
pub mod git_ops;
pub mod github;

use chrono::{Duration, Utc};
use url;

use crate::config::parse_config;
use crate::db::{create_tables, establish_connection};
use crate::errors::Result;
use crate::git_ops::ensure_repo_cloned_or_updated;
use crate::github::GitHubClient;

// Helper function to extract owner/repo from URL or path
fn parse_repo_url(url_or_path: &str) -> Result<(String, String)> {
    // Attempt to parse as https URL first
    if let Ok(url) = url::Url::parse(url_or_path) {
        if let Some(mut segments) = url.path_segments() {
            if let (Some(owner), Some(name)) = (segments.next(), segments.next()) {
                return Ok((owner.to_string(), name.trim_end_matches(".git").to_string()));
            }
        }
    }
    // Attempt to parse as git@host:owner/repo.git format
    else if let Some(pos) = url_or_path.find(':') {
        let path_part = &url_or_path[pos + 1..];
        if let Some(slash_pos) = path_part.find('/') {
            let owner = &path_part[..slash_pos];
            let name = path_part[slash_pos + 1..].trim_end_matches(".git");
            return Ok((owner.to_string(), name.to_string()));
        }
    }
    // Attempt to parse as owner/repo string
    else if let Some(slash_pos) = url_or_path.find('/') {
        let owner = &url_or_path[..slash_pos];
        let name = &url_or_path[slash_pos + 1..];
        return Ok((owner.to_string(), name.to_string()));
    }

    Err(errors::DataError::ConfigError(format!(
        "Could not parse owner/repo from: {}",
        url_or_path
    )))
}

fn main() -> Result<()> {
    env_logger::init();
    log::info!("Starting Rust data loader...");

    // 1. Parse configuration
    let config = parse_config();
    log::debug!("Configuration loaded: {:?}", config);

    // 2. Initialize DB connection
    let conn = establish_connection(&config.db_path)?;

    // 3. Create tables if they don't exist
    create_tables(&conn)?;

    // 4. Ensure repositories are cloned/updated
    log::info!("Ensuring repository 1 is available locally...");
    let repo1_local_path = ensure_repo_cloned_or_updated(
        &config.repo1_path,
        &config.clone_dir,
        config.github_token.as_deref(),
    )?;
    log::info!("Repository 1 path: {:?}", repo1_local_path);

    log::info!("Ensuring repository 2 is available locally...");
    let repo2_local_path = ensure_repo_cloned_or_updated(
        &config.repo2_path,
        &config.clone_dir,
        config.github_token.as_deref(),
    )?;
    log::info!("Repository 2 path: {:?}", repo2_local_path);

    // 5. Initialize GitHub Client
    let github_client = GitHubClient::new(config.github_token.clone())?;

    // === Data Fetching and Storing ===
    // Define the time period for fetching (e.g., last 12 months)
    let analysis_period_months = 12;
    let since_date = Utc::now() - Duration::days(30 * analysis_period_months);
    let since_iso = since_date.to_rfc3339();

    // Extract repo owner/name from config
    let (repo1_owner, repo1_name) = parse_repo_url(&config.repo1_path)?;
    let (repo2_owner, repo2_name) = parse_repo_url(&config.repo2_path)?;
    let repo1_full_name = format!("{}/{}", repo1_owner, repo1_name);
    let repo2_full_name = format!("{}/{}", repo2_owner, repo2_name);

    log::info!(
        "Fetching data for {} since {}...",
        repo1_full_name,
        since_iso
    );
    // Fetch commits for repo 1
    let commits1 = github_client.get_commits(
        &repo1_owner,
        &repo1_name,
        Some(since_iso.clone()),
        None,
        None,
    )?;
    log::info!("Fetched {} commits for {}", commits1.len(), repo1_full_name);
    db::insert_github_commits(&conn, &commits1, &repo1_full_name)?;

    // Fetch PRs for repo 1
    let prs1 = github_client.get_pull_requests(&repo1_owner, &repo1_name, None, None, None)?;
    log::info!("Fetched {} PRs for {}", prs1.len(), repo1_full_name);
    db::insert_github_pull_requests(&conn, &prs1, &repo1_full_name)?;

    // Fetch Issues for repo 1
    let issues1 = github_client.get_issues(
        &repo1_owner,
        &repo1_name,
        None,
        None,
        Some(since_iso.clone()),
    )?;
    log::info!("Fetched {} issues for {}", issues1.len(), repo1_full_name);
    db::insert_github_issues(&conn, &issues1, &repo1_full_name)?;

    // Fetch Contributors for repo 1
    // TODO: Call github_client.get_contributors(&repo1_owner, &repo1_name)?;
    // TODO: Call db::insert_github_contributors(&conn, &contributors1, &repo1_full_name)?;

    // TODO: Fetch other data (Reviews, Comments) for repo 1 and insert into DB

    log::info!(
        "Fetching data for {} since {}...",
        repo2_full_name,
        since_iso
    );
    // Fetch commits for repo 2
    let commits2 = github_client.get_commits(
        &repo2_owner,
        &repo2_name,
        Some(since_iso.clone()),
        None,
        None,
    )?;
    log::info!("Fetched {} commits for {}", commits2.len(), repo2_full_name);
    db::insert_github_commits(&conn, &commits2, &repo2_full_name)?;

    // Fetch PRs for repo 2
    let prs2 = github_client.get_pull_requests(&repo2_owner, &repo2_name, None, None, None)?;
    log::info!("Fetched {} PRs for {}", prs2.len(), repo2_full_name);
    db::insert_github_pull_requests(&conn, &prs2, &repo2_full_name)?;

    // Fetch Issues for repo 2
    let issues2 = github_client.get_issues(
        &repo2_owner,
        &repo2_name,
        None,
        None,
        Some(since_iso.clone()),
    )?;
    log::info!("Fetched {} issues for {}", issues2.len(), repo2_full_name);
    db::insert_github_issues(&conn, &issues2, &repo2_full_name)?;

    // Fetch Contributors for repo 2
    // TODO: Call github_client.get_contributors(&repo2_owner, &repo2_name)?;
    // TODO: Call db::insert_github_contributors(&conn, &contributors2, &repo2_full_name)?;

    // TODO: Fetch other data (Reviews, Comments) for repo 2 and insert into DB

    // TODO: Fetch git-specific data if needed (git_ops + db)

    log::info!("Data loading process completed successfully.");
    Ok(())
}
