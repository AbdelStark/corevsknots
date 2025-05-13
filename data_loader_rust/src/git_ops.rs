use crate::errors::Result;
use git2::{AutotagOption, Cred, FetchOptions, FetchPrune, RemoteCallbacks, Repository};
use std::fs;
use std::path::{Path, PathBuf};

/// Ensures a repository is cloned or updated.
/// Returns the path to the local repository.
pub fn ensure_repo_cloned_or_updated(
    repo_url: &str,
    local_base_dir: &str,
    github_token: Option<&str>,
) -> Result<PathBuf> {
    let repo_name = repo_url
        .split('/')
        .last()
        .unwrap_or("unknown_repo")
        .replace(".git", "");
    let local_repo_path = Path::new(local_base_dir).join(&repo_name);

    if !Path::new(local_base_dir).exists() {
        fs::create_dir_all(local_base_dir)?;
    }

    if local_repo_path.exists() {
        log::info!(
            "Repository {} exists locally, attempting to update...",
            repo_name
        );
        let repo = Repository::open(&local_repo_path)?;
        fetch_all_and_prune(&repo, github_token)?;
    } else {
        log::info!("Cloning repository {} from {}...", repo_name, repo_url);
        let mut fo = FetchOptions::new();
        if let Some(token) = github_token {
            let mut callbacks = RemoteCallbacks::new();
            callbacks.credentials(|_url, _username_from_server, _allowed_types| {
                Cred::userpass_plaintext(token, "") // Use token as username, empty password
            });
            fo.remote_callbacks(callbacks);
        }
        fo.download_tags(AutotagOption::All);
        git2::build::RepoBuilder::new()
            .fetch_options(fo)
            .clone(repo_url, &local_repo_path)?;
        log::info!(
            "Repository {} cloned successfully to {:?}.",
            repo_name,
            local_repo_path
        );
    }
    Ok(local_repo_path)
}

fn fetch_all_and_prune(repo: &Repository, github_token: Option<&str>) -> Result<()> {
    log::info!("Fetching all remotes for {:?}", repo.path());
    let mut fo = FetchOptions::new();
    if let Some(token) = github_token {
        let mut callbacks = RemoteCallbacks::new();
        callbacks.credentials(|_url, _username_from_server, _allowed_types| {
            Cred::userpass_plaintext(token, "")
        });
        fo.remote_callbacks(callbacks);
    }
    fo.prune(FetchPrune::On);
    fo.download_tags(AutotagOption::All);

    let remotes = repo.remotes()?;
    for remote_name_opt in remotes.iter() {
        if let Some(remote_name) = remote_name_opt {
            log::debug!("Fetching remote: {}", remote_name);
            match repo.find_remote(remote_name) {
                Ok(mut remote) => {
                    remote.fetch(&[] as &[&str], Some(&mut fo), None)?;
                    log::info!("Fetched remote {} successfully.", remote_name);
                }
                Err(e) => {
                    log::warn!("Could not find remote {}: {}. Skipping.", remote_name, e);
                }
            }
        }
    }
    log::info!("Finished fetching all remotes for {:?}", repo.path());
    Ok(())
}

// TODO: Add functions to extract commit data, etc., from the local repo using git2
// This might involve iterating over revwalk, similar to how it's done in Python.
