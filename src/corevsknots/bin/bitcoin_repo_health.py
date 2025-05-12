"""
Bitcoin Repository Health Analysis Tool

Usage:
    bitcoin-repo-health analyze [--repo=<repo>] [--output=<path>] [--months=<months>] [--token=<token>] [--local-path=<local>] [--use-cache | --no-cache] [--verbose]
    bitcoin-repo-health compare [--repo1=<repo1>] [--repo2=<repo2>] [--output=<path>] [--months=<months>] [--token=<token>] [--local-path1=<local1>] [--local-path2=<local2>] [--use-cache | --no-cache] [--verbose]
    bitcoin-repo-health report [--metrics=<file>] [--output=<path>] [--format=<format>]
    bitcoin-repo-health -h | --help
    bitcoin-repo-health --version

Options:
    --repo=<repo>               Repository name (e.g., bitcoin/bitcoin).
    --repo1=<repo1>             First repository name for comparison.
    --repo2=<repo2>             Second repository name for comparison.
    --output=<path>             Output directory for reports [default: ./reports].
    --months=<months>           Analysis period in months [default: 12].
    --token=<token>             GitHub personal access token.
    --local-path=<local>        Path to local repository clone for single analysis.
    --local-path1=<local1>      Path to first local repository clone for comparison.
    --local-path2=<local2>      Path to second local repository clone for comparison.
    --use-cache                 Use cached API responses [default: True].
    --no-cache                  Do not use cached API responses.
    --metrics=<file>            Path to previously collected metrics JSON file for generating a report.
    --format=<format>           Output format for the report (e.g., markdown, html, json) [default: markdown].
    -v --verbose                Enable verbose output.
    -h --help                   Show this screen.
    --version                   Show version.
"""

import sys

from docopt import docopt

from .. import __version__  # Assuming you'll add __version__ to src/corevsknots/__init__.py
from ..analyze import analyze_repository, compare_repositories

# We might need a function for generate_report_from_file in analyze.py or report.py
from ..report import generate_report
from ..utils.logger import get_logger, setup_logger


def main():
    args = docopt(__doc__, version=f"Bitcoin Repo Health {__version__}")

    if args['--verbose']:
        setup_logger(level="DEBUG")
    else:
        setup_logger(level="INFO")

    logger = get_logger(__name__)
    logger.debug(f"CLI Arguments: {args}")

    try:
        if args['analyze']:
            repo = args['--repo']
            if not repo:
                print("Error: --repo is required for analyze command.")
                sys.exit(1)
            logger.info(f"Analyzing repository: {repo}")
            metrics = analyze_repository(
                repo=repo,
                months=int(args['--months']),
                github_token=args['--token'],
                local_path=args['--local-path'],
                use_cache=not args['--no-cache']
            )
            # TODO: Decide on output_name for single analysis report
            report_path = generate_report(metrics, args['--output'], f"{repo.replace('/', '_')}_health_report", args['--format'], template="single")
            logger.info(f"Report generated at: {report_path}")

        elif args['compare']:
            repo1 = args['--repo1']
            repo2 = args['--repo2']
            if not repo1 or not repo2:
                print("Error: --repo1 and --repo2 are required for compare command.")
                sys.exit(1)

            logger.info(f"Comparing repositories: {repo1} vs {repo2}")
            comparison_data = compare_repositories(
                repo1=repo1,
                repo2=repo2,
                months=int(args['--months']),
                github_token=args['--token'],
                local_path1=args['--local-path1'],
                local_path2=args['--local-path2'],
                use_cache=not args['--no-cache']
            )
            report_name = f"{repo1.replace('/', '_')}_vs_{repo2.replace('/', '_')}_comparison"
            report_path = generate_report(comparison_data, args['--output'], report_name, args['--format'], template="comparison")
            logger.info(f"Comparison report generated at: {report_path}")

        elif args['report']:
            metrics_file = args['--metrics']
            if not metrics_file:
                print("Error: --metrics is required for report command.")
                sys.exit(1)
            logger.info(f"Generating report from metrics file: {metrics_file}")
            # TODO: Implement loading metrics from file and generating report
            # import json
            # with open(metrics_file, 'r') as f:
            #     metrics_data = json.load(f)
            # report_path = generate_report(metrics_data, args['--output'], "custom_report", args['--format'])
            # logger.info(f"Report generated at: {report_path}")
            print("Report generation from metrics file is not yet fully implemented.")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=args['--verbose'])
        sys.exit(1)

if __name__ == '__main__':
    main()
