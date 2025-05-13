import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface CommitSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const CommitSection: React.FC<CommitSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.commit;

  if (!metrics) {
    return <MetricCard title={`${displayName} - Commit Activity`}><p>Commit data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Commit Activity`}>
      <div className={styles.metricPair} title="Average commits per day. Higher generally means more active development.">
        <span className={styles.metricLabel}>Frequency:</span>
        <span className={styles.metricValue}>{metrics.commit_frequency} ({metrics.commits_per_day?.toFixed(1)}/day)</span>
      </div>
      <div className={styles.metricPair} title="Score (0-10) based on commit message length and descriptiveness. Higher is better.">
        <span className={styles.metricLabel}>Message Quality:</span>
        <span className={styles.metricValue}>{metrics.commit_message_quality?.quality_score?.toFixed(1)}/10</span>
      </div>
      <div className={styles.metricPair} title="Average lines of code changed per commit.">
        <span className={styles.metricLabel}>Avg. Commit Size:</span>
        <span className={styles.metricValue}>{metrics.avg_commit_size?.toFixed(0)} lines</span>
      </div>
      <div className={styles.metricPair} title="Percentage of commits changing more than 300 lines.">
        <span className={styles.metricLabel}>Large Commit Ratio:</span>
        <span className={styles.metricValue}>{(metrics.large_commit_ratio !== undefined ? (metrics.large_commit_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      <div className={styles.metricPair} title="Percentage of original commits (non-Core merges for Knots) that are merge commits (e.g., merging feature branches).">
        <span className={styles.metricLabel}>Merge Commit Ratio (Original):</span>
        <span className={styles.metricValue}>{(metrics.merge_commit_ratio !== undefined ? (metrics.merge_commit_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      {/* TODO: Display commits_by_day/hour as small inline bars or text? Add comparison charts if needed. */}
    </MetricCard>
  );
};

export default CommitSection;
