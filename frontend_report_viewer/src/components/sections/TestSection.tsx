import ComparisonBarChart from '@/components/ComparisonBarChart';
import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface TestSectionProps {
  reportData: ComparisonData;
}

const TestSection: React.FC<TestSectionProps> = ({ reportData }) => {
  const metrics1 = reportData.repo1.metrics.test;
  const metrics2 = reportData.repo2.metrics.test;

  if (!metrics1 || !metrics2) {
    return <MetricCard title="Testing Practices Comparison"><p>Test data not available.</p></MetricCard>;
  }

  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  return (
    <MetricCard title="Testing Practices Comparison">
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Has Tests:</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.has_tests ? 'Yes' : 'No'}</span> vs <span className={styles.valueRepo2}>{metrics2.has_tests ? 'Yes' : 'No'}</span>
        </span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Testing Practice Score:</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.testing_practice_score?.toFixed(1)}/10</span> vs <span className={styles.valueRepo2}>{metrics2.testing_practice_score?.toFixed(1)}/10</span>
        </span>
      </div>
      {metrics1.testing_practice_score !== undefined && metrics2.testing_practice_score !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.testing_practice_score}
          repo2Score={metrics2.testing_practice_score}
          chartTitle="Testing Practice Score"
          scoreSuffix="/10"
          maxValue={10}
        />
      )}
      {/* Add test_files_count, testing_frameworks if available and desired */}
    </MetricCard>
  );
};

export default TestSection;
