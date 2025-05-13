import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface IssueSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
}

const IssueSection: React.FC<IssueSectionProps> = ({ reportData, fighterKey }) => {
  const metrics = reportData[fighterKey].metrics.issue;
  const repoName = reportData[fighterKey].name;

  if (!metrics) {
    return <MetricCard title={`${repoName} - Issue Tracking`}><p>Issue data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${repoName} - Issue Tracking`}>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Total Issues:</span>
        <span className={styles.metricValue}>{metrics.total_issues ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Open Issues:</span>
        <span className={styles.metricValue}>{metrics.open_issues ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Closed Ratio:</span>
        <span className={styles.metricValue}>{(metrics.closed_ratio !== undefined ? (metrics.closed_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Avg. Time to Close:</span>
        <span className={styles.metricValue}>{metrics.avg_time_to_close_issue?.toFixed(1)} hours</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Responsiveness Score:</span>
        <span className={styles.metricValue}>{metrics.responsiveness_score?.toFixed(1)}/10</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Stale Issue Ratio:</span>
        <span className={styles.metricValue}>{(metrics.stale_issue_ratio !== undefined ? (metrics.stale_issue_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      {/* TODO: Add categorization_score, bug_report_ratio etc. */}
    </MetricCard>
  );
};

export default IssueSection;
