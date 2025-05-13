import ComparisonBarChart from '@/components/ComparisonBarChart';
import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface IssueSectionProps {
  reportData: ComparisonData;
}

const IssueSection: React.FC<IssueSectionProps> = ({ reportData }) => {
  const metrics1 = reportData.repo1.metrics.issue;
  const metrics2 = reportData.repo2.metrics.issue;

  if (!metrics1 || !metrics2) {
    return <MetricCard title="Issue Tracking Comparison"><p>Issue data not available.</p></MetricCard>;
  }

  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  return (
    <MetricCard title="Issue Tracking Comparison">
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Total Issues:</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.total_issues}</span> vs <span className={styles.valueRepo2}>{metrics2.total_issues}</span>
        </span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Responsiveness Score:</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.responsiveness_score?.toFixed(1)}/10</span> vs <span className={styles.valueRepo2}>{metrics2.responsiveness_score?.toFixed(1)}/10</span>
        </span>
      </div>
      {metrics1.responsiveness_score !== undefined && metrics2.responsiveness_score !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.responsiveness_score}
          repo2Score={metrics2.responsiveness_score}
          chartTitle="Issue Responsiveness Score"
          scoreSuffix="/10"
          maxValue={10}
        />
      )}
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Stale Issue Ratio:</span>
        <span>
          <span className={styles.valueRepo1}>{(metrics1.stale_issue_ratio !== undefined ? (metrics1.stale_issue_ratio * 100).toFixed(1) : 'N/A')}%</span> vs <span className={styles.valueRepo2}>{(metrics2.stale_issue_ratio !== undefined ? (metrics2.stale_issue_ratio * 100).toFixed(1) : 'N/A')}%</span>
        </span>
      </div>
       {metrics1.stale_issue_ratio !== undefined && metrics2.stale_issue_ratio !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.stale_issue_ratio * 100}
          repo2Score={metrics2.stale_issue_ratio * 100}
          chartTitle="Stale Issue Ratio (Lower is Better)"
          scoreSuffix="%"
          maxValue={Math.max(metrics1.stale_issue_ratio*100 || 0, metrics2.stale_issue_ratio*100 || 0, 10) * 1.2}
        />
      )}
    </MetricCard>
  );
};

export default IssueSection;
