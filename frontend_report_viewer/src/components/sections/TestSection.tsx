import MetricCard from '@/components/MetricCard';
import homeStyles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import { MetricDisplay } from '@/utils/metricDisplayUtils';
import React from 'react';

interface TestSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const TestSection: React.FC<TestSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.test;
  const opponentKey = fighterKey === 'repo1' ? 'repo2' : 'repo1';
  const opponentMetrics = reportData[opponentKey].metrics.test;

  if (!metrics || !opponentMetrics) {
    return <MetricCard title={`${displayName} - Testing Practices`}><p>Test data not fully available for comparison.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Testing Practices`}>
      <MetricDisplay
        label="Has Tests"
        primaryValue={metrics.has_tests ? 'Yes' : 'No'}
        opponentValue={opponentMetrics.has_tests ? 'Yes' : 'No'}
        primaryFighterKey={fighterKey}
        tooltip="Whether automated tests are detected in the repository."
      />

      {metrics.has_tests && opponentMetrics.has_tests && (
        <>
          <MetricDisplay
            label="Test Files Count"
            primaryValue={metrics.test_files_count}
            opponentValue={opponentMetrics.test_files_count}
            primaryFighterKey={fighterKey}
            tooltip="Number of files identified as test files."
          />
          <MetricDisplay
            label="Practice Score"
            primaryValue={metrics.testing_practice_score}
            opponentValue={opponentMetrics.testing_practice_score}
            primaryFighterKey={fighterKey}
            unit="/10"
            tooltip="Score (0-10) evaluating overall testing practices. Higher is better."
          />
        </>
      )}

      {(metrics.has_tests && !opponentMetrics.has_tests) && (
        <p style={{textAlign: 'center', margin: '1rem 0', color: homeStyles.valueRepo1 || '#45aaf2'}}>{displayName} has tests, opponent does not.</p>
      )}
      {(!metrics.has_tests && opponentMetrics.has_tests) && (
        <p style={{textAlign: 'center', margin: '1rem 0', color: homeStyles.valueRepo2 || '#ff6b81'}}>Opponent has tests, {displayName} does not.</p>
      )}

      <div className={homeStyles.metricPair} title="Detected testing frameworks or libraries.">
        <span className={homeStyles.metricLabel}>Testing Frameworks:</span>
        <span className={homeStyles.metricValue}>{metrics.testing_frameworks?.join(', ') || 'N/A'}</span>
      </div>

    </MetricCard>
  );
};

export default TestSection;
