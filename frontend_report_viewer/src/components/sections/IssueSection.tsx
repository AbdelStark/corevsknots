import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface IssueSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const IssueSection: React.FC<IssueSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.issue;

  if (!metrics) {
    return <MetricCard title={`${displayName} - Issue Tracking`}><p>Issue data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Issue Tracking`}>
      <div className={styles.metricPair} title="Total number of issues in the period.">
        <span className={styles.metricLabel}>Total Issues:</span>
        <span className={styles.metricValue}>{metrics.total_issues ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair} title="Number of issues currently open.">
        <span className={styles.metricLabel}>Open Issues:</span>
        <span className={styles.metricValue}>{metrics.open_issues ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair} title="Percentage of issues that are closed.">
        <span className={styles.metricLabel}>Closed Ratio:</span>
        <span className={styles.metricValue}>{(metrics.closed_ratio !== undefined ? (metrics.closed_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      <div className={styles.metricPair} title="Average time in hours for an issue to be closed. Lower is better.">
        <span className={styles.metricLabel}>Avg. Time to Close:</span>
        <span className={styles.metricValue}>{metrics.avg_time_to_close_issue?.toFixed(1)} hours</span>
      </div>
      <div className={styles.metricPair} title="Score (0-10) based on how quickly issues are addressed/closed. Higher is better.">
        <span className={styles.metricLabel}>Responsiveness Score:</span>
        <span className={styles.metricValue}>{metrics.responsiveness_score?.toFixed(1)}/10</span>
      </div>
      <div className={styles.metricPair} title="Percentage of open issues that haven't been updated in a while (e.g., >30 days). Lower is better.">
        <span className={styles.metricLabel}>Stale Issue Ratio:</span>
        <span className={styles.metricValue}>{(metrics.stale_issue_ratio !== undefined ? (metrics.stale_issue_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      {/* TODO: Add categorization_score, bug_report_ratio etc. */}
    </MetricCard>
  );
};

export default IssueSection;
