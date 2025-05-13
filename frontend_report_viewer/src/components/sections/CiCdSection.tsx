import ComparisonBarChart from '@/components/ComparisonBarChart';
import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface CiCdSectionProps {
  reportData: ComparisonData;
}

const CiCdSection: React.FC<CiCdSectionProps> = ({ reportData }) => {
  const metrics1 = reportData.repo1.metrics.ci_cd;
  const metrics2 = reportData.repo2.metrics.ci_cd;

  if (!metrics1 || !metrics2) {
    return <MetricCard title="CI/CD Comparison"><p>CI/CD data not available.</p></MetricCard>;
  }

  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  return (
    <MetricCard title="CI/CD Comparison">
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Has CI:</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.has_ci ? 'Yes' : 'No'}</span> vs <span className={styles.valueRepo2}>{metrics2.has_ci ? 'Yes' : 'No'}</span>
        </span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Workflow Success Rate:</span>
        <span>
          <span className={styles.valueRepo1}>{(metrics1.workflow_success_rate !== undefined ? (metrics1.workflow_success_rate * 100).toFixed(1) : 'N/A')}%</span> vs <span className={styles.valueRepo2}>{(metrics2.workflow_success_rate !== undefined ? (metrics2.workflow_success_rate * 100).toFixed(1) : 'N/A')}%</span>
        </span>
      </div>
      {metrics1.workflow_success_rate !== undefined && metrics2.workflow_success_rate !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.workflow_success_rate * 100}
          repo2Score={metrics2.workflow_success_rate * 100}
          chartTitle="Workflow Success Rate"
          scoreSuffix="%"
          maxValue={100}
        />
      )}
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>CI Systems Used (Repo1):</span>
        <span className={styles.metricValue}>{metrics1.ci_systems?.join(', ') || 'N/A'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>CI Systems Used (Repo2):</span>
        <span className={styles.metricValue}>{metrics2.ci_systems?.join(', ') || 'N/A'}</span>
      </div>
    </MetricCard>
  );
};

export default CiCdSection;
