import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface PullRequestSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
}

const PullRequestSection: React.FC<PullRequestSectionProps> = ({ reportData, fighterKey }) => {
  const metrics = reportData[fighterKey].metrics.pull_request;
  const repoName = reportData[fighterKey].name;

  if (!metrics) {
    return <MetricCard title={`${repoName} - Pull Requests`}><p>Pull Request data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${repoName} - Pull Requests`}>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Total PRs:</span>
        <span className={styles.metricValue}>{metrics.total_prs ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Merge Rate:</span>
        <span className={styles.metricValue}>{(metrics.merged_ratio !== undefined ? (metrics.merged_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Avg. Time to Merge:</span>
        <span className={styles.metricValue}>{metrics.avg_time_to_merge?.toFixed(1)} hours</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Velocity Score:</span>
        <span className={styles.metricValue}>{metrics.pr_velocity_score?.toFixed(1)}/10</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Avg. PR Size:</span>
        <span className={styles.metricValue}>{metrics.avg_pr_size?.toFixed(0)} lines</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Large PR Ratio:</span>
        <span className={styles.metricValue}>{(metrics.large_pr_ratio !== undefined ? (metrics.large_pr_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>External PR Ratio:</span>
        <span className={styles.metricValue}>{(metrics.external_pr_ratio !== undefined ? (metrics.external_pr_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      {/* TODO: Add charts for distributions or trends if data is available */}
    </MetricCard>
  );
};

export default PullRequestSection;
