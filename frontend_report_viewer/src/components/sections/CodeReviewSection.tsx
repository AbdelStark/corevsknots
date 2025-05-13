// src/components/sections/CodeReviewSection.tsx
import MetricCard from '@/components/MetricCard';
import { ComparisonData } from '@/types/reportTypes';
import { MetricDisplay } from '@/utils/metricDisplayUtils';
import React from 'react';
// import styles from '@/styles/Home.module.css'; // Not directly used

interface CodeReviewSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const CodeReviewSection: React.FC<CodeReviewSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.code_review;
  const opponentKey = fighterKey === 'repo1' ? 'repo2' : 'repo1';
  const opponentMetrics = reportData[opponentKey].metrics.code_review;

  if (!metrics || !opponentMetrics) {
    return <MetricCard title={`${displayName} - Code Review`}><p>Code Review data not fully available for comparison.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Code Review`}>
      <MetricDisplay
        label="Reviews per PR"
        primaryValue={metrics.reviews_per_pr}
        opponentValue={opponentMetrics.reviews_per_pr}
        primaryFighterKey={fighterKey}
        tooltip="Average number of formal review submissions per PR."
      />
      <MetricDisplay
        label="Comments per PR"
        primaryValue={metrics.comments_per_pr}
        opponentValue={opponentMetrics.comments_per_pr}
        primaryFighterKey={fighterKey}
        tooltip="Average number of review comments per PR."
      />
      <MetricDisplay
        label="Thoroughness Score"
        primaryValue={metrics.review_thoroughness_score}
        opponentValue={opponentMetrics.review_thoroughness_score}
        primaryFighterKey={fighterKey}
        unit="/10"
        tooltip="Score (0-10) indicating review thoroughness (multiple reviewers, substantive comments/changes requested). Higher is better."
        showBar={true}
        barMaxValue={10}
      />
      <MetricDisplay
        label="Self-Merged Ratio"
        primaryValue={metrics.self_merged_ratio !== undefined ? metrics.self_merged_ratio * 100 : undefined}
        opponentValue={opponentMetrics.self_merged_ratio !== undefined ? opponentMetrics.self_merged_ratio * 100 : undefined}
        primaryFighterKey={fighterKey}
        unit="%"
        lowerIsBetter={true}
        tooltip="Percentage of merged PRs that were merged by the PR author. Lower indicates more independent review."
        showBar={true}
        barMaxValue={100}
      />
      <MetricDisplay
        label="Avg. Time to First Review"
        primaryValue={metrics.avg_time_to_first_review}
        opponentValue={opponentMetrics.avg_time_to_first_review}
        primaryFighterKey={fighterKey}
        unit=" hours"
        lowerIsBetter={true}
        tooltip="Average time in hours from PR creation to the first formal review. Lower is better."
      />
      <MetricDisplay
        label="Responsiveness Score"
        primaryValue={metrics.review_responsiveness_score}
        opponentValue={opponentMetrics.review_responsiveness_score}
        primaryFighterKey={fighterKey}
        unit="/10"
        tooltip="Score (0-10) indicating speed of first review. Higher is better."
        showBar={true}
        barMaxValue={10}
      />
    </MetricCard>
  );
};

export default CodeReviewSection;
