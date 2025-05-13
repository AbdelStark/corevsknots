import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface CiCdSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
}

const CiCdSection: React.FC<CiCdSectionProps> = ({ reportData, fighterKey }) => {
  const metrics = reportData[fighterKey].metrics.ci_cd;
  const repoName = reportData[fighterKey].name;

  if (!metrics) {
    return <MetricCard title={`${repoName} - CI/CD`}><p>CI/CD data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${repoName} - CI/CD`}>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Has CI:</span>
        <span className={styles.metricValue}>{metrics.has_ci ? 'Yes' : 'No'}</span>
      </div>
      {metrics.has_ci && (
        <>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>Workflow Success Rate:</span>
            <span className={styles.metricValue}>{(metrics.workflow_success_rate !== undefined ? (metrics.workflow_success_rate * 100).toFixed(1) : 'N/A')}%</span>
          </div>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>Workflows per Day:</span>
            <span className={styles.metricValue}>{metrics.workflows_per_day?.toFixed(1) ?? 'N/A'}</span>
          </div>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>Unique Workflows:</span>
            <span className={styles.metricValue}>{metrics.unique_workflows ?? 'N/A'}</span>
          </div>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>CI Systems:</span>
            <span className={styles.metricValue}>{metrics.ci_systems?.join(', ') || (metrics.ci_system_count ? `${metrics.ci_system_count} system(s)` : 'N/A')}</span>
          </div>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>PRs Run CI Ratio:</span>
            <span className={styles.metricValue}>{(metrics.pr_ci_ratio !== undefined ? (metrics.pr_ci_ratio * 100).toFixed(1) : 'N/A')}%</span>
          </div>
        </>
      )}
    </MetricCard>
  );
};

export default CiCdSection;
