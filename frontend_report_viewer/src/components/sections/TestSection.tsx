import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface TestSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const TestSection: React.FC<TestSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.test;

  if (!metrics) {
    return <MetricCard title={`${displayName} - Testing Practices`}><p>Test data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Testing Practices`}>
      <div className={styles.metricPair} title="Whether automated tests are detected in the repository.">
        <span className={styles.metricLabel}>Has Tests:</span>
        <span className={styles.metricValue}>{metrics.has_tests ? 'Yes' : 'No'}</span>
      </div>
      {metrics.has_tests && (
        <>
          <div className={styles.metricPair} title="Number of files identified as test files.">
            <span className={styles.metricLabel}>Test Files Count:</span>
            <span className={styles.metricValue}>{metrics.test_files_count ?? 'N/A'}</span>
          </div>
          <div className={styles.metricPair} title="Detected testing frameworks or libraries.">
            <span className={styles.metricLabel}>Testing Frameworks:</span>
            <span className={styles.metricValue}>{metrics.testing_frameworks?.join(', ') || 'N/A'}</span>
          </div>
          <div className={styles.metricPair} title="Score (0-10) evaluating overall testing practices. Higher is better.">
            <span className={styles.metricLabel}>Practice Score:</span>
            <span className={styles.metricValue}>{metrics.testing_practice_score?.toFixed(1)}/10</span>
          </div>
        </>
      )}
    </MetricCard>
  );
};

export default TestSection;
