"""
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
    --repo1=<repo1>             First repository name for comparison.
    --repo2=<repo2>             Second repository name for comparison.
    --output=<path>             Output directory for reports [default: ./reports].
    --months=<months>           Analysis period in months [default: 12].
    --token=<token>             GitHub personal access token.
    --local-path=<local>        Path to local repository clone for single analysis.
    --local-path1=<local1>      Path to first local repository clone (for compare or fight).
    --local-path2=<local2>      Path to second local repository clone (for compare or fight).
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

CORE_REPO = "bitcoin/bitcoin"
KNOTS_REPO = "bitcoinknots/bitcoin"

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

        elif args['compare'] or args['fight']:
            if args['fight']:
                repo1 = CORE_REPO
                repo2 = KNOTS_REPO
                logger.info(f"Initiating a Core vs Knots FIGHT! ({repo1} vs {repo2})")
            else: # compare command
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
                use_cache=not args['--no-cache'],
                is_fight_mode=(args['fight'] is True) # Pass a flag for special handling
            )
            report_name = f"{repo1.replace('/', '_')}_vs_{repo2.replace('/', '_')}_comparison"
            if args['fight']:
                report_name = f"CORE_vs_KNOTS_FIGHT_REPORT"
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

    # Display summary if compare or fight was successful and data is available
    if (args['compare'] or args['fight']) and 'comparison_data' in locals() and comparison_data:
        try:
            print("\n--- Repository Health Comparison Summary ---")
            repo1_name = comparison_data['repo1']['name']
            repo2_name = comparison_data['repo2']['name']
            metrics1 = comparison_data['repo1']['metrics']
            metrics2 = comparison_data['repo2']['metrics']

            print(f"Overall Score: {repo1_name}: {metrics1.get('overall_health_score', 'N/A')}/10  vs  {repo2_name}: {metrics2.get('overall_health_score', 'N/A')}/10")

            # Contributor summary
            print("\nContributors:")
            print(f"  Total: {repo1_name}: {metrics1.get('contributor', {}).get('total_contributors', 'N/A')}  vs  {repo2_name}: {metrics2.get('contributor', {}).get('total_contributors', 'N/A')}")
            if args['fight']:
                print(f"  Original to Knots: {metrics2.get('contributor', {}).get('knots_contributors_with_original_work', 'N/A')}")
                print(f"  Knots Bus Factor (Original): {metrics2.get('contributor', {}).get('knots_original_bus_factor', 'N/A')}")
            else:
                print(f"  Bus Factor: {repo1_name}: {metrics1.get('contributor', {}).get('bus_factor', 'N/A')}  vs  {repo2_name}: {metrics2.get('contributor', {}).get('bus_factor', 'N/A')}")

            # Commit summary
            print("\nCommits (per day, original for Knots in fight mode):")
            commits1_per_day = metrics1.get('commit', {}).get('commits_per_day', 'N/A')
            commits2_per_day = metrics2.get('commit', {}).get('commits_per_day', 'N/A')
            print(f"  Frequency: {repo1_name}: {commits1_per_day}  vs  {repo2_name}: {commits2_per_day}")
            print(f"  Msg Quality: {repo1_name}: {metrics1.get('commit', {}).get('commit_message_quality', {}).get('quality_score','N/A')}/10  vs  {repo2_name}: {metrics2.get('commit', {}).get('commit_message_quality', {}).get('quality_score','N/A')}/10")

            print(f"\nFull report generated at: {report_path}")
        except Exception as e:
            logger.error(f"Error generating CLI summary: {e}")

if __name__ == '__main__':
    main()
