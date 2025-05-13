import MetricCard from '@/components/MetricCard';
import { ComparisonData } from '@/types/reportTypes';
import { MetricDisplay } from '@/utils/metricDisplayUtils';
import React from 'react';

interface CommitSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const CommitSection: React.FC<CommitSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.commit;
  const opponentKey = fighterKey === 'repo1' ? 'repo2' : 'repo1';
  const opponentMetrics = reportData[opponentKey].metrics.commit;

  if (!metrics || !opponentMetrics) {
    return <MetricCard title={`${displayName} - Commit Activity`}><p>Commit data not fully available for comparison.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Commit Activity`}>
      <MetricDisplay
        label="Frequency"
        primaryValue={metrics.commits_per_day}
        opponentValue={opponentMetrics.commits_per_day}
        primaryFighterKey={fighterKey}
        unit="/day"
        tooltip={`Commit Frequency: ${metrics.commit_frequency} (${metrics.commits_per_day?.toFixed(1)}/day). Average commits per day. Higher generally means more active development.`}
      />
      <MetricDisplay
        label="Message Quality"
        primaryValue={metrics.commit_message_quality?.quality_score}
        opponentValue={opponentMetrics.commit_message_quality?.quality_score}
        primaryFighterKey={fighterKey}
        unit="/10"
        tooltip="Score (0-10) based on commit message length and descriptiveness. Higher is better."
      />
      <MetricDisplay
        label="Avg. Commit Size"
        primaryValue={metrics.avg_commit_size}
        opponentValue={opponentMetrics.avg_commit_size}
        primaryFighterKey={fighterKey}
        unit=" lines"
        lowerIsBetter={true}
        tooltip="Average lines of code changed per commit. Smaller, focused commits are often preferred."
      />
       <MetricDisplay
        label="Large Commit Ratio"
        primaryValue={metrics.large_commit_ratio !== undefined ? metrics.large_commit_ratio * 100 : undefined}
        opponentValue={opponentMetrics.large_commit_ratio !== undefined ? opponentMetrics.large_commit_ratio * 100 : undefined}
        primaryFighterKey={fighterKey}
        unit="%"
        lowerIsBetter={true}
        tooltip="Percentage of commits changing more than 300 lines. Lower is often better."
      />
      <MetricDisplay
        label="Merge Commit Ratio (Original)"
        primaryValue={metrics.merge_commit_ratio !== undefined ? metrics.merge_commit_ratio * 100 : undefined}
        opponentValue={opponentMetrics.merge_commit_ratio !== undefined ? opponentMetrics.merge_commit_ratio * 100 : undefined}
        primaryFighterKey={fighterKey}
        unit="%"
        lowerIsBetter={true}
        tooltip="Percentage of original commits that are merge commits (e.g., feature branches). Context dependent."
      />
    </MetricCard>
  );
};

export default CommitSection;
