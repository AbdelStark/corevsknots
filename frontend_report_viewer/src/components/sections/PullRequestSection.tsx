import MetricCard from '@/components/MetricCard';
import { ComparisonData } from '@/types/reportTypes';
import { MetricDisplay } from '@/utils/metricDisplayUtils';
import React from 'react';

interface PullRequestSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const PullRequestSection: React.FC<PullRequestSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.pull_request;
  const opponentKey = fighterKey === 'repo1' ? 'repo2' : 'repo1';
  const opponentMetrics = reportData[opponentKey].metrics.pull_request;

  if (!metrics || !opponentMetrics) {
    return <MetricCard title={`${displayName} - Pull Requests`}><p>Pull Request data not fully available for comparison.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Pull Requests`}>
      <MetricDisplay
        label="Total PRs"
        primaryValue={metrics.total_prs}
        opponentValue={opponentMetrics.total_prs}
        primaryFighterKey={fighterKey}
        tooltip="Total number of Pull Requests in the period."
      />
      <MetricDisplay
        label="Merge Rate"
        primaryValue={metrics.merged_ratio !== undefined ? metrics.merged_ratio * 100 : undefined}
        opponentValue={opponentMetrics.merged_ratio !== undefined ? opponentMetrics.merged_ratio * 100 : undefined}
        primaryFighterKey={fighterKey}
        unit="%"
        tooltip="Percentage of PRs that were merged."
      />
      <MetricDisplay
        label="Avg. Time to Merge"
        primaryValue={metrics.avg_time_to_merge}
        opponentValue={opponentMetrics.avg_time_to_merge}
        primaryFighterKey={fighterKey}
        unit=" hours"
        lowerIsBetter={true}
        tooltip="Average time in hours for a PR to be merged after creation. Lower is better."
      />
      <MetricDisplay
        label="Velocity Score"
        primaryValue={metrics.pr_velocity_score}
        opponentValue={opponentMetrics.pr_velocity_score}
        primaryFighterKey={fighterKey}
        unit="/10"
        tooltip="Score (0-10) indicating PR processing speed. Higher is better."
      />
      <MetricDisplay
        label="Avg. PR Size"
        primaryValue={metrics.avg_pr_size}
        opponentValue={opponentMetrics.avg_pr_size}
        primaryFighterKey={fighterKey}
        unit=" lines"
        lowerIsBetter={true}
        tooltip="Average lines of code changed per Pull Request. Smaller, focused PRs are often preferred."
      />
      <MetricDisplay
        label="Large PR Ratio"
        primaryValue={metrics.large_pr_ratio !== undefined ? metrics.large_pr_ratio * 100 : undefined}
        opponentValue={opponentMetrics.large_pr_ratio !== undefined ? opponentMetrics.large_pr_ratio * 100 : undefined}
        primaryFighterKey={fighterKey}
        unit="%"
        lowerIsBetter={true}
        tooltip="Percentage of PRs changing more than 1000 lines. Lower is often better."
      />
      <MetricDisplay
        label="External PR Ratio"
        primaryValue={metrics.external_pr_ratio !== undefined ? metrics.external_pr_ratio * 100 : undefined}
        opponentValue={opponentMetrics.external_pr_ratio !== undefined ? opponentMetrics.external_pr_ratio * 100 : undefined}
        primaryFighterKey={fighterKey}
        unit="%"
        tooltip="Percentage of PRs submitted by non-core contributors. Higher can indicate broader community involvement."
      />
    </MetricCard>
  );
};

export default PullRequestSection;
