import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface PullRequestSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const PullRequestSection: React.FC<PullRequestSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.pull_request;

  if (!metrics) {
    return <MetricCard title={`${displayName} - Pull Requests`}><p>Pull Request data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Pull Requests`}>
      <div className={styles.metricPair} title="Total number of Pull Requests in the period.">
        <span className={styles.metricLabel}>Total PRs:</span>
        <span className={styles.metricValue}>{metrics.total_prs ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair} title="Percentage of PRs that were merged.">
        <span className={styles.metricLabel}>Merge Rate:</span>
        <span className={styles.metricValue}>{(metrics.merged_ratio !== undefined ? (metrics.merged_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      <div className={styles.metricPair} title="Average time in hours for a PR to be merged after creation. Lower is better.">
        <span className={styles.metricLabel}>Avg. Time to Merge:</span>
        <span className={styles.metricValue}>{metrics.avg_time_to_merge?.toFixed(1)} hours</span>
      </div>
      <div className={styles.metricPair} title="Score (0-10) indicating PR processing speed. Higher is better.">
        <span className={styles.metricLabel}>Velocity Score:</span>
        <span className={styles.metricValue}>{metrics.pr_velocity_score?.toFixed(1)}/10</span>
      </div>
      <div className={styles.metricPair} title="Average lines of code changed per Pull Request.">
        <span className={styles.metricLabel}>Avg. PR Size:</span>
        <span className={styles.metricValue}>{metrics.avg_pr_size?.toFixed(0)} lines</span>
      </div>
      <div className={styles.metricPair} title="Percentage of PRs changing more than 1000 lines.">
        <span className={styles.metricLabel}>Large PR Ratio:</span>
        <span className={styles.metricValue}>{(metrics.large_pr_ratio !== undefined ? (metrics.large_pr_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      <div className={styles.metricPair} title="Percentage of PRs submitted by non-core contributors.">
        <span className={styles.metricLabel}>External PR Ratio:</span>
        <span className={styles.metricValue}>{(metrics.external_pr_ratio !== undefined ? (metrics.external_pr_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      {/* TODO: Add charts for distributions or trends if data is available */}
    </MetricCard>
  );
};

export default PullRequestSection;
