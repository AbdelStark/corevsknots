import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface CommitSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
}

const CommitSection: React.FC<CommitSectionProps> = ({ reportData, fighterKey }) => {
  const metrics = reportData[fighterKey].metrics.commit;
  const repoName = reportData[fighterKey].name;

  if (!metrics) {
    return <MetricCard title={`${repoName} - Commit Activity`}><p>Commit data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${repoName} - Commit Activity`}>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Frequency:</span>
        <span className={styles.metricValue}>{metrics.commit_frequency} ({metrics.commits_per_day?.toFixed(1)}/day)</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Message Quality:</span>
        <span className={styles.metricValue}>{metrics.commit_message_quality?.quality_score?.toFixed(1)}/10</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Avg. Commit Size:</span>
        <span className={styles.metricValue}>{metrics.avg_commit_size?.toFixed(0)} lines</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Large Commit Ratio:</span>
        <span className={styles.metricValue}>{(metrics.large_commit_ratio !== undefined ? (metrics.large_commit_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Merge Commit Ratio (within original):</span>
        <span className={styles.metricValue}>{(metrics.merge_commit_ratio !== undefined ? (metrics.merge_commit_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      {/* TODO: Display commits_by_day/hour as small inline bars or text? Add comparison charts if needed. */}
    </MetricCard>
  );
};

export default CommitSection;
