// src/components/sections/OverallScoresSection.tsx
import HealthBarChart from '@/components/HealthBarChart';
import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface OverallScoresSectionProps {
  reportData: ComparisonData;
}

const OverallScoresSection: React.FC<OverallScoresSectionProps> = ({ reportData }) => {
  const score1 = reportData.repo1.metrics.overall_health_score;
  const score2 = reportData.repo2.metrics.overall_health_score;

  return (
    <>
      {score1 !== undefined && score2 !== undefined && (
        <HealthBarChart
          repo1Name={reportData.repo1.name}
          repo2Name={reportData.repo2.name}
          repo1Score={score1}
          repo2Score={score2}
          maxValue={10}
        />
      )}
      <MetricCard title="Overall Health Scores">
        <div className={styles.metricPair}>
          <span className={styles.metricLabel}>{reportData.repo1.name}:</span>
          <span className={`${styles.metricValue} ${styles.valueRepo1}`}>{score1?.toFixed(1) ?? 'N/A'}/10</span>
        </div>
        <div className={styles.metricPair}>
          <span className={styles.metricLabel}>{reportData.repo2.name}:</span>
          <span className={`${styles.metricValue} ${styles.valueRepo2}`}>{score2?.toFixed(1) ?? 'N/A'}/10</span>
        </div>
      </MetricCard>
    </>
  );
};

export default OverallScoresSection;
