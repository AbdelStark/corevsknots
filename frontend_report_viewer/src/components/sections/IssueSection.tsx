import MetricCard from '@/components/MetricCard';
import { ComparisonData } from '@/types/reportTypes';
import { MetricDisplay } from '@/utils/metricDisplayUtils';
import React from 'react';

interface IssueSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const IssueSection: React.FC<IssueSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.issue;
  const opponentKey = fighterKey === 'repo1' ? 'repo2' : 'repo1';
  const opponentMetrics = reportData[opponentKey].metrics.issue;

  if (!metrics || !opponentMetrics) {
    return <MetricCard title={`${displayName} - Issue Tracking`}><p>Issue data not fully available for comparison.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Issue Tracking`}>
      <MetricDisplay
        label="Total Issues"
        primaryValue={metrics.total_issues}
        opponentValue={opponentMetrics.total_issues}
        primaryFighterKey={fighterKey}
        tooltip="Total number of issues in the period."
      />
      <MetricDisplay
        label="Open Issues"
        primaryValue={metrics.open_issues}
        opponentValue={opponentMetrics.open_issues}
        primaryFighterKey={fighterKey}
        tooltip="Number of issues currently open."
      />
      <MetricDisplay
        label="Closed Ratio"
        primaryValue={metrics.closed_ratio !== undefined ? metrics.closed_ratio * 100 : undefined}
        opponentValue={opponentMetrics.closed_ratio !== undefined ? opponentMetrics.closed_ratio * 100 : undefined}
        primaryFighterKey={fighterKey}
        unit="%"
        tooltip="Percentage of issues that are closed."
      />
      <MetricDisplay
        label="Avg. Time to Close"
        primaryValue={metrics.avg_time_to_close_issue}
        opponentValue={opponentMetrics.avg_time_to_close_issue}
        primaryFighterKey={fighterKey}
        unit=" hours"
        lowerIsBetter={true}
        tooltip="Average time in hours for an issue to be closed. Lower is better."
      />
      <MetricDisplay
        label="Responsiveness Score"
        primaryValue={metrics.responsiveness_score}
        opponentValue={opponentMetrics.responsiveness_score}
        primaryFighterKey={fighterKey}
        unit="/10"
        tooltip="Score (0-10) based on how quickly issues are addressed/closed. Higher is better."
      />
      <MetricDisplay
        label="Stale Issue Ratio"
        primaryValue={metrics.stale_issue_ratio !== undefined ? metrics.stale_issue_ratio * 100 : undefined}
        opponentValue={opponentMetrics.stale_issue_ratio !== undefined ? opponentMetrics.stale_issue_ratio * 100 : undefined}
        primaryFighterKey={fighterKey}
        unit="%"
        lowerIsBetter={true}
        tooltip="Percentage of open issues that haven't been updated in a while (e.g., >30 days). Lower is better."
      />
    </MetricCard>
  );
};

export default IssueSection;
