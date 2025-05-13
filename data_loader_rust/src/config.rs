use clap::Parser;

/// Structure to hold command line arguments
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
pub struct Config {
    /// Path to the DuckDB database file
    #[arg(short, long, env = "DUCKDB_PATH", default_value = "repo_data.db")]
    pub db_path: String,

    /// GitHub personal access token (optional, increases rate limit)
    #[arg(short, long, env = "GITHUB_TOKEN")]
    pub github_token: Option<String>,

    /// URL or path for the first repository (e.g., bitcoin/bitcoin)
    #[arg(
        long,
        env = "REPO1_PATH",
        default_value = "https://github.com/bitcoin/bitcoin.git"
    )]
    pub repo1_path: String,

    /// URL or path for the second repository (e.g., bitcoinknots/bitcoin)
    #[arg(
        long,
        env = "REPO2_PATH",
        default_value = "https://github.com/bitcoinknots/bitcoin.git"
    )]
    pub repo2_path: String,

    /// Local directory to clone/store the repositories
    #[arg(long, env = "CLONE_DIR", default_value = "./repo_clones")]
    pub clone_dir: String,

    /// Force fetching data even if DB exists (useful for updates)
    #[arg(long, default_value_t = false)]
    pub force_fetch: bool,
}

pub fn parse_config() -> Config {
    Config::parse()
}
