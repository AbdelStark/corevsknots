import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface TestSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
}

const TestSection: React.FC<TestSectionProps> = ({ reportData, fighterKey }) => {
  const metrics = reportData[fighterKey].metrics.test;
  const repoName = reportData[fighterKey].name;

  if (!metrics) {
    return <MetricCard title={`${repoName} - Testing Practices`}><p>Test data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${repoName} - Testing Practices`}>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Has Tests:</span>
        <span className={styles.metricValue}>{metrics.has_tests ? 'Yes' : 'No'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Testing Practice Score:</span>
        <span className={styles.metricValue}>{metrics.testing_practice_score?.toFixed(1)}/10</span>
      </div>
      {/* Chart removed */}
      {/* Add test_files_count, testing_frameworks if available and desired */}
    </MetricCard>
  );
};

export default TestSection;
