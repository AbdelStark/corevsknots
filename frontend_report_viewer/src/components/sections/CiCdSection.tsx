import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface CiCdSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const CiCdSection: React.FC<CiCdSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.ci_cd;

  if (!metrics) {
    return <MetricCard title={`${displayName} - CI/CD`}><p>CI/CD data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - CI/CD`}>
      <div className={styles.metricPair} title="Whether Continuous Integration (CI) is detected.">
        <span className={styles.metricLabel}>Has CI:</span>
        <span className={styles.metricValue}>{metrics.has_ci ? 'Yes' : 'No'}</span>
      </div>
      {metrics.has_ci && (
        <>
          <div className={styles.metricPair} title="Percentage of CI workflow runs that succeeded.">
            <span className={styles.metricLabel}>Workflow Success Rate:</span>
            <span className={styles.metricValue}>{(metrics.workflow_success_rate !== undefined ? (metrics.workflow_success_rate * 100).toFixed(1) : 'N/A')}%</span>
          </div>
          <div className={styles.metricPair} title="Average number of CI workflow runs per day.">
            <span className={styles.metricLabel}>Workflows per Day:</span>
            <span className={styles.metricValue}>{metrics.workflows_per_day?.toFixed(1) ?? 'N/A'}</span>
          </div>
          <div className={styles.metricPair} title="Number of unique CI workflow configurations detected.">
            <span className={styles.metricLabel}>Unique Workflows:</span>
            <span className={styles.metricValue}>{metrics.unique_workflows ?? 'N/A'}</span>
          </div>
          <div className={styles.metricPair} title="Detected CI systems (e.g., GitHub Actions, Travis CI).">
            <span className={styles.metricLabel}>CI Systems:</span>
            <span className={styles.metricValue}>{metrics.ci_systems?.join(', ') || (metrics.ci_system_count ? `${metrics.ci_system_count} system(s)` : 'N/A')}</span>
          </div>
          <div className={styles.metricPair} title="Ratio of Pull Requests that triggered a CI run.">
            <span className={styles.metricLabel}>PRs Run CI Ratio:</span>
            <span className={styles.metricValue}>{(metrics.pr_ci_ratio !== undefined ? (metrics.pr_ci_ratio * 100).toFixed(1) : 'N/A')}%</span>
          </div>
        </>
      )}
    </MetricCard>
  );
};

export default CiCdSection;
