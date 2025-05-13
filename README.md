# Bitcoin Repository Health Analysis Tool

A comprehensive tool for analyzing and comparing the health of Bitcoin repositories based on open source and software development best practices.

## Overview

This tool analyzes GitHub repositories (specifically Bitcoin Core and Bitcoin Knots) to evaluate their health based on key metrics:

- **Contributor Base** - Diversity, activity, and bus factor
- **Commit Patterns** - Frequency, quality, and distribution
- **Pull Request Workflow** - Merge rates, review processes, and velocity
- **Code Review Practices** - Thoroughness, independence, and responsiveness
- **CI/CD Integration** - Pipeline presence, success rates, and workflow
- **Issue Management** - Responsiveness, categorization, and resolution
- **Testing Practices** - Test coverage signals, framework usage, and quality

The goal is to provide objective data about repository health and development practices to help users make informed decisions about which implementations to trust and run.

## Background

The Bitcoin community occasionally experiences technical debates that can become polarized, including the recent OP_RETURN drama. This tool was created to provide objective data about repository health and development practices to help users evaluate competing implementations.

## Installation

### From PyPI

```bash
pip install bitcoin-repo-health
```

### From Source

```bash
git clone https://github.com/AbdelStark/corevsknots.git
cd corevsknots
pip install -e .
```

## Usage

### Command Line Interface

The tool provides a command-line interface for analyzing repositories:

```bash
# Analyze a single repository (e.g., bitcoin/bitcoin)
bitcoin-repo-health analyze --repo bitcoin/bitcoin --output ./reports

# Compare two repositories
bitcoin-repo-health compare --repo1 bitcoin/bitcoin --repo2 bitcoinknots/bitcoin --output ./reports

# "Fight" mode: Compare Bitcoin Core vs. Bitcoin Knots with fork-specific logic
bitcoin-repo-health fight --output ./reports --months 6 # Example: analyze last 6 months

# Generate a report from previously collected metrics (Not yet fully implemented)
# bitcoin-repo-health report --metrics ./reports/bitcoin_bitcoin_metrics.json --format markdown
```

### Options

The command-line interface is defined as follows (from `bitcoin-repo-health --help`):

```text
Bitcoin Repository Health Analysis Tool

Usage:
    bitcoin-repo-health analyze [--repo=<repo>] [--output=<path>] [--months=<months>] [--token=<token>] [--local-path=<local>] [--use-cache | --no-cache] [--verbose]
    bitcoin-repo-health compare [--repo1=<repo1>] [--repo2=<repo2>] [--output=<path>] [--months=<months>] [--token=<token>] [--local-path1=<local1>] [--local-path2=<local2>] [--use-cache | --no-cache] [--verbose]
    bitcoin-repo-health fight [--output=<path>] [--months=<months>] [--token=<token>] [--local-path1=<local1>] [--local-path2=<local2>] [--use-cache | --no-cache] [--verbose]
    bitcoin-repo-health report [--metrics=<file>] [--output=<path>] [--format=<format>]
    bitcoin-repo-health -h | --help
    bitcoin-repo-health --version

Options:
    --repo=<repo>               Repository name (e.g., bitcoin/bitcoin) for analyze.
                                If not provided, the tool might prompt or use a default.
    --repo1=<repo1>             First repository name for comparison (e.g., bitcoin/bitcoin).
    --repo2=<repo2>             Second repository name for comparison (e.g., bitcoinknots/bitcoin).
                                For the 'fight' command, these are automatically set to
                                Bitcoin Core and Bitcoin Knots respectively.
    --output=<path>             Output directory for reports [default: ./reports].
    --months=<months>           Analysis period in months [default: 12].
    --token=<token>             GitHub personal access token. Can also be set via GITHUB_TOKEN
                                environment variable.
    --local-path=<local>        Path to local repository clone for single analysis.
    --local-path1=<local1>      Path to first local repository clone (for compare or fight).
    --local-path2=<local2>      Path to second local repository clone (for compare or fight).
    --use-cache                 Use cached API responses [default: True].
    --no-cache                  Do not use cached API responses. This will make fresh API calls.
    --metrics=<file>            Path to previously collected metrics JSON file for generating
                                a report from existing data. (Report generation from file
                                is not yet fully implemented).
    --format=<format>           Output format for the report (e.g., markdown, html, json)
                                [default: markdown]. This applies when generating a new report
                                or from a metrics file.
    -v --verbose                  Enable verbose output, showing DEBUG level logs.
    -h --help                     Show this help message and exit.
    --version                     Show version information and exit.
```

### GitHub API Rate Limiting

The tool uses the GitHub API, which has rate limits. To increase your rate limit, you can provide a GitHub personal access token:

```bash
export GITHUB_TOKEN=your_token_here
bitcoin-repo-health analyze --repo bitcoin/bitcoin
```

Or pass it directly:

```bash
bitcoin-repo-health analyze --repo bitcoin/bitcoin --token your_token_here
```

### Configuration File

You can use a YAML configuration file to customize the analysis:

```yaml
# config.yaml
period: 12
output_dir: ./reports
output_format: markdown
use_cache: true
github_token: your_token_here
repositories:
  bitcoin_core:
    name: bitcoin/bitcoin
    clone_url: https://github.com/bitcoin/bitcoin.git
    default_branch: master
  bitcoin_knots:
    name: bitcoinknots/bitcoin
    clone_url: https://github.com/bitcoinknots/bitcoin.git
    default_branch: master
```

Then use it with:

```bash
bitcoin-repo-health analyze --repo bitcoin/bitcoin --config config.yaml
```

## Example Reports

### Repository Health Report

The tool generates comprehensive health reports that include:

- Overall health score with breakdown by category
- Contributor base analysis with bus factor calculation
- Commit patterns and quality metrics
- Pull request workflow evaluation
- Code review process assessment
- CI/CD pipeline analysis
- Issue management effectiveness
- Testing practices evaluation
- Recommendations for improvement

### Comparison Report

When comparing repositories, the tool generates:

- Side-by-side metrics comparison
- Highlighted differences and their significance
- Relative strengths of each repository
- Recommendations for improvement

## Development

### Project Structure

```text
corevsknots/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── fetch/
│   │   ├── github_api.py
│   │   ├── git_cli.py
│   │   └── cache.py
│   ├── metrics/
│   │   ├── contributor.py
│   │   ├── commits.py
│   │   ├── pull_requests.py
│   │   ├── code_review.py
│   │   ├── ci_cd.py
│   │   ├── issues.py
│   │   └── tests.py
│   ├── analyze.py
│   ├── report/
│   │   ├── markdown_generator.py
│   │   └── chart_generator.py
│   └── utils/
│       ├── logger.py
│       └── time_utils.py
├── bin/
│   └── bitcoin-repo-health
├── tests/
├── examples/
├── docs/
├── README.md
├── setup.py
└── requirements.txt
```

### Development Setup

1. Clone the repository

   ```bash
   git clone https://github.com/AbdelStark/corevsknots.git
   cd corevsknots
   ```

2. Create and activate a virtual environment

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies

   ```bash
   pip install -e ".[testing]"
   ```

4. Install pre-commit hooks

   ```bash
   pre-commit install
   ```

5. Run code formatting

   ```bash
   make format
   ```

6. Run linting and type checking

   ```bash
   make lint
   make typecheck
   ```

7. Run tests

   ```bash
   make test
   ```

### Available Make Commands

- `make format` - Format code with Black and isort
- `make lint` - Run linting with flake8
- `make typecheck` - Run type checking with mypy
- `make test` - Run tests with pytest
- `make test-cov` - Run tests with coverage
- `make clean` - Clean up build artifacts
- `make install-dev` - Install in development mode
- `make install-hooks` - Install pre-commit hooks
- `make check` - Run all checks (format, lint, typecheck, test)
- `make reset` - Full cleanup and reinstall

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
