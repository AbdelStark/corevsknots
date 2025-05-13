import ComparisonBarChart from '@/components/ComparisonBarChart';
import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface PullRequestSectionProps {
  reportData: ComparisonData;
}

const PullRequestSection: React.FC<PullRequestSectionProps> = ({ reportData }) => {
  const metrics1 = reportData.repo1.metrics.pull_request;
  const metrics2 = reportData.repo2.metrics.pull_request;

  if (!metrics1 || !metrics2) {
    return <MetricCard title="Pull Request Process Comparison"><p>Pull Request data not available.</p></MetricCard>;
  }

  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  return (
    <MetricCard title="Pull Request Process Comparison">
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>PR Merge Rate:</span>
        <span>
          <span className={styles.valueRepo1}>{(metrics1.merged_ratio !== undefined ? (metrics1.merged_ratio * 100).toFixed(1) : 'N/A')}%</span> vs <span className={styles.valueRepo2}>{(metrics2.merged_ratio !== undefined ? (metrics2.merged_ratio * 100).toFixed(1) : 'N/A')}%</span>
        </span>
      </div>
      {metrics1.merged_ratio !== undefined && metrics2.merged_ratio !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.merged_ratio * 100}
          repo2Score={metrics2.merged_ratio * 100}
          chartTitle="PR Merge Rate"
          scoreSuffix="%"
          maxValue={100}
        />
      )}

      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>PR Velocity Score:</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.pr_velocity_score?.toFixed(1)}/10</span> vs <span className={styles.valueRepo2}>{metrics2.pr_velocity_score?.toFixed(1)}/10</span>
        </span>
      </div>
      {metrics1.pr_velocity_score !== undefined && metrics2.pr_velocity_score !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.pr_velocity_score}
          repo2Score={metrics2.pr_velocity_score}
          chartTitle="PR Velocity Score"
          scoreSuffix="/10"
          maxValue={10}
        />
      )}
      {/* TODO: Add other PR metrics like avg_time_to_merge, avg_pr_size */}
    </MetricCard>
  );
};

export default PullRequestSection;
