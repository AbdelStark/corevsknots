use crate::errors::Result;
use crate::github::{GitHubCommit, GitHubContributor, GitHubIssue, GitHubPullRequest};
use rusqlite::params;
use rusqlite::Connection;

/// Establishes a connection to the SQLite database file.
pub fn establish_connection(db_path: &str) -> Result<Connection> {
    log::info!("Connecting to database: {}", db_path);
    let conn = Connection::open(db_path)?;
    // Enable foreign keys for potential relational data later
    conn.execute("PRAGMA foreign_keys = ON;", [])?;
    log::info!("Database connection established.");
    Ok(conn)
}

/// Creates the necessary database tables if they don't exist.
pub fn create_tables(conn: &Connection) -> Result<()> {
    log::info!("Creating database tables if they don't exist...");

    // SQLite uses slightly different types (INTEGER, TEXT, REAL, BLOB)
    // Using TEXT for timestamps (ISO 8601 format) is common and simple.
    // Using INTEGER for GitHub IDs/Numbers.
    // VARCHAR maps to TEXT in SQLite.
    conn.execute_batch(
        r"
        BEGIN;

        -- Schemas are not directly supported in SQLite,
        -- table names will include the prefix implicitly.

        CREATE TABLE IF NOT EXISTS github_commits (
            sha TEXT PRIMARY KEY,
            repo_name TEXT,
            author_login TEXT,
            committer_login TEXT,
            message TEXT,
            commit_timestamp TEXT, -- Store as ISO 8601 string
            api_url TEXT
        );

        CREATE TABLE IF NOT EXISTS github_pull_requests (
            id INTEGER PRIMARY KEY, -- GitHub PR ID
            number INTEGER,
            repo_name TEXT,
            state TEXT, -- open, closed, merged
            title TEXT,
            user_login TEXT,
            created_at TEXT,
            updated_at TEXT,
            closed_at TEXT,
            merged_at TEXT,
            merge_commit_sha TEXT,
            UNIQUE (repo_name, number) -- Ensure uniqueness per repo
        );

        CREATE TABLE IF NOT EXISTS github_issues (
            id INTEGER PRIMARY KEY, -- GitHub Issue ID
            number INTEGER,
            repo_name TEXT,
            state TEXT, -- open, closed
            title TEXT,
            user_login TEXT,
            created_at TEXT,
            updated_at TEXT,
            closed_at TEXT,
            comments_count INTEGER,
            UNIQUE (repo_name, number) -- Ensure uniqueness per repo
        );

        CREATE TABLE IF NOT EXISTS github_contributors (
            id INTEGER, -- GitHub User ID
            repo_name TEXT,
            login TEXT,
            contributions INTEGER,
            contributor_type TEXT,
            PRIMARY KEY (repo_name, login) -- Composite key
        );

        -- Add tables for reviews, comments, contributors, etc.

        CREATE TABLE IF NOT EXISTS git_commits (
            sha TEXT PRIMARY KEY,
            repo_name TEXT,
            author_name TEXT,
            author_email TEXT,
            commit_timestamp TEXT,
            message TEXT
        );

        COMMIT;
        ",
    )?;

    log::info!("Table creation check complete.");
    Ok(())
}

/// Inserts or replaces GitHub commit data into the database.
pub fn insert_github_commits(
    conn: &Connection,
    commits: &[GitHubCommit],
    repo_name_full: &str,
) -> Result<()> {
    log::info!(
        "Inserting {} commits for repo '{}' into database...",
        commits.len(),
        repo_name_full
    );
    let mut stmt = conn.prepare_cached(
        r"
        INSERT OR REPLACE INTO github_commits (
            sha, repo_name, author_login, committer_login, message, commit_timestamp, api_url
        )
        VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)
        ",
    )?;

    conn.execute_batch("BEGIN TRANSACTION;")?; // Start transaction for bulk insert

    for commit in commits {
        let author_login = commit.author.as_ref().map(|u| u.login.as_str());
        let committer_login = commit.committer.as_ref().map(|u| u.login.as_str());
        let commit_timestamp = commit
            .commit
            .committer // Use committer date as it usually represents when it entered the repo
            .as_ref()
            .and_then(|c| c.date)
            .map(|dt| dt.to_rfc3339());

        stmt.execute(params![
            commit.sha,
            repo_name_full,
            author_login,
            committer_login,
            commit.commit.message,
            commit_timestamp,
            commit.url
        ])?;
    }

    conn.execute_batch("COMMIT;")?; // Commit transaction
    log::info!("Successfully inserted commits for {}", repo_name_full);
    Ok(())
}

/// Inserts or replaces GitHub Pull Request data into the database.
pub fn insert_github_pull_requests(
    conn: &Connection,
    prs: &[GitHubPullRequest],
    repo_name_full: &str,
) -> Result<()> {
    log::info!(
        "Inserting {} PRs for repo '{}' into database...",
        prs.len(),
        repo_name_full
    );
    let mut stmt = conn.prepare_cached(
        r"
        INSERT OR REPLACE INTO github_pull_requests (
            id, number, repo_name, state, title, user_login,
            created_at, updated_at, closed_at, merged_at, merge_commit_sha
        )
        VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)
        ",
    )?;

    conn.execute_batch("BEGIN TRANSACTION;")?;

    for pr in prs {
        let user_login = pr.user.as_ref().map(|u| u.login.as_str());
        let created_at_str = pr.created_at.to_rfc3339();
        let updated_at_str = pr.updated_at.to_rfc3339();
        let closed_at_str = pr.closed_at.map(|dt| dt.to_rfc3339());
        let merged_at_str = pr.merged_at.map(|dt| dt.to_rfc3339());

        stmt.execute(params![
            pr.id,
            pr.number,
            repo_name_full,
            pr.state,
            pr.title,
            user_login,
            created_at_str,
            updated_at_str,
            closed_at_str,
            merged_at_str,
            pr.merge_commit_sha
        ])?;
    }

    conn.execute_batch("COMMIT;")?;
    log::info!("Successfully inserted PRs for {}", repo_name_full);
    Ok(())
}

/// Inserts or replaces GitHub Issue data into the database.
pub fn insert_github_issues(
    conn: &Connection,
    issues: &[GitHubIssue],
    repo_name_full: &str,
) -> Result<()> {
    log::info!(
        "Inserting {} issues for repo '{}' into database...",
        issues.len(),
        repo_name_full
    );
    let mut stmt = conn.prepare_cached(
        r"
        INSERT OR REPLACE INTO github_issues (
            id, number, repo_name, state, title, user_login,
            created_at, updated_at, closed_at, comments_count
        )
        VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10)
        ",
    )?;
    // TODO: Handle labels, assignees separately if needed (many-to-many tables)

    conn.execute_batch("BEGIN TRANSACTION;")?;

    for issue in issues {
        let user_login = issue.user.as_ref().map(|u| u.login.as_str());
        let created_at_str = issue.created_at.to_rfc3339();
        let updated_at_str = issue.updated_at.to_rfc3339();
        let closed_at_str = issue.closed_at.map(|dt| dt.to_rfc3339());

        stmt.execute(params![
            issue.id,
            issue.number,
            repo_name_full,
            issue.state,
            issue.title,
            user_login,
            created_at_str,
            updated_at_str,
            closed_at_str,
            issue.comments
        ])?;
    }

    conn.execute_batch("COMMIT;")?;
    log::info!("Successfully inserted issues for {}", repo_name_full);
    Ok(())
}

/// Inserts or replaces GitHub Contributor data into the database.
pub fn insert_github_contributors(
    conn: &Connection,
    contributors: &[GitHubContributor],
    repo_name_full: &str,
) -> Result<()> {
    // TODO: Implement insertion logic similar to commits/issues/prs
    log::warn!("insert_github_contributors is not yet implemented.");
    Ok(())
}

// TODO: Add functions to insert fetched data into the tables using rusqlite prepared statements
// e.g., insert_github_contributors(conn: &Connection, contributors: &[GitHubContributor], repo_name: &str) -> Result<()>
