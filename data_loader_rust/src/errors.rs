use thiserror::Error;

#[derive(Error, Debug)]
pub enum DataError {
    #[error("Database error: {0}")]
    DbError(#[from] rusqlite::Error),

    #[error("Git operation error: {0}")]
    GitError(#[from] git2::Error),

    #[error("GitHub API request error: {0}")]
    RequestError(#[from] reqwest::Error),

    #[error("JSON deserialization error: {0}")]
    JsonError(#[from] serde_json::Error),

    #[error("IO error: {0}")]
    IoError(#[from] std::io::Error),

    #[error("Configuration error: {0}")]
    ConfigError(String),

    #[error("API rate limit exceeded")]
    RateLimitError,

    #[error("Resource not found (404)")]
    NotFoundError,

    #[error("GitHub API error: {status} - {message}")]
    GitHubApiError {
        status: reqwest::StatusCode,
        message: String,
    },

    #[error("Other error: {0}")]
    Other(String),
}

pub type Result<T> = std::result::Result<T, DataError>;
