import ComparisonBarChart from '@/components/ComparisonBarChart';
import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface CommitSectionProps {
  reportData: ComparisonData;
}

const CommitSection: React.FC<CommitSectionProps> = ({ reportData }) => {
  const metrics1 = reportData.repo1.metrics.commit;
  const metrics2 = reportData.repo2.metrics.commit;

  if (!metrics1 || !metrics2) {
    return <MetricCard title="Commit Activity Comparison"><p>Commit data not available.</p></MetricCard>;
  }

  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  return (
    <MetricCard title="Commit Activity Comparison">
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Commits per Day:</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.commits_per_day?.toFixed(1)}</span> vs <span className={styles.valueRepo2}>{metrics2.commits_per_day?.toFixed(1)}</span>
        </span>
      </div>
      {metrics1.commits_per_day !== undefined && metrics2.commits_per_day !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.commits_per_day}
          repo2Score={metrics2.commits_per_day}
          chartTitle="Commits per Day"
          maxValue={Math.max(metrics1.commits_per_day || 0, metrics2.commits_per_day || 0, 1) * 1.2}
        />
      )}

      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Commit Message Quality:</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.commit_message_quality?.quality_score?.toFixed(1)}/10</span> vs <span className={styles.valueRepo2}>{metrics2.commit_message_quality?.quality_score?.toFixed(1)}/10</span>
        </span>
      </div>
      {metrics1.commit_message_quality?.quality_score !== undefined && metrics2.commit_message_quality?.quality_score !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.commit_message_quality.quality_score}
          repo2Score={metrics2.commit_message_quality.quality_score}
          chartTitle="Commit Message Quality Score"
          scoreSuffix="/10"
          maxValue={10}
        />
      )}
      {/* TODO: Add other commit metrics like avg_commit_size, merge_commit_ratio */}
    </MetricCard>
  );
};

export default CommitSection;
