// src/components/sections/OverallScoresSection.tsx
import ComparisonBarChart from '@/components/ComparisonBarChart';
import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css'; // Re-using some styles for now
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface OverallScoresSectionProps {
  reportData: ComparisonData;
}

const OverallScoresSection: React.FC<OverallScoresSectionProps> = ({ reportData }) => {
  if (!reportData.repo1.metrics.overall_health_score || !reportData.repo2.metrics.overall_health_score) {
    return null; // Or a placeholder if scores are missing
  }

  return (
    <>
      {reportData.repo1.metrics.overall_health_score !== undefined && reportData.repo2.metrics.overall_health_score !== undefined && (
        <ComparisonBarChart
          repo1Name={reportData.repo1.name}
          repo2Name={reportData.repo2.name}
          repo1Score={reportData.repo1.metrics.overall_health_score}
          repo2Score={reportData.repo2.metrics.overall_health_score}
          chartTitle="Overall Health Score Comparison"
          scoreSuffix="/10"
          maxValue={10}
        />
      )}
      <MetricCard title="Overall Health Scores">
        <div className={styles.metricPair}>
          <span className={styles.metricLabel}>{reportData.repo1.name}:</span>
          <span className={`${styles.metricValue} ${styles.valueRepo1}`}>{reportData.repo1.metrics.overall_health_score?.toFixed(1)}/10</span>
        </div>
        <div className={styles.metricPair}>
          <span className={styles.metricLabel}>{reportData.repo2.name}:</span>
          <span className={`${styles.metricValue} ${styles.valueRepo2}`}>{reportData.repo2.metrics.overall_health_score?.toFixed(1)}/10</span>
        </div>
      </MetricCard>
    </>
  );
};

export default OverallScoresSection;
