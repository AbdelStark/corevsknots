import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css'; // Re-using some styles for now
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';
// import ComparisonBarChart from '@/components/ComparisonBarChart'; // If you add charts here

interface ContributorSectionProps {
  reportData: ComparisonData;
}

const ContributorSection: React.FC<ContributorSectionProps> = ({ reportData }) => {
  const metrics1 = reportData.repo1.metrics.contributor;
  const metrics2 = reportData.repo2.metrics.contributor;

  if (!metrics1 || !metrics2) {
    return <MetricCard title="Contributor Comparison"><p>Contributor data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title="Contributor Comparison">
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Total Contributors (API):</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.total_contributors}</span> vs <span className={styles.valueRepo2}>{metrics2.total_contributors}</span>
        </span>
      </div>

      {reportData.analysis_metadata.is_fight_mode ? (
        <>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>Original Knots Authors:</span>
            <span className={`${styles.metricValue} ${styles.valueRepo2}`}>{metrics2.knots_contributors_with_original_work}</span>
          </div>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>Knots Bus Factor (Original):</span>
            <span className={`${styles.metricValue} ${styles.valueRepo2}`}>{metrics2.knots_original_bus_factor}</span>
          </div>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>Core Bus Factor (General):</span>
            <span className={`${styles.metricValue} ${styles.valueRepo1}`}>{metrics1.bus_factor}</span>
          </div>
          {/* TODO: Add Gini, Org Diversity for fight mode */}
        </>
      ) : (
        <>
          {metrics1.bus_factor !== undefined && metrics2.bus_factor !== undefined && (
            <div className={styles.metricPair}>
              <span className={styles.metricLabel}>Bus Factor:</span>
              <span>
                <span className={styles.valueRepo1}>{metrics1.bus_factor}</span> vs <span className={styles.valueRepo2}>{metrics2.bus_factor}</span>
              </span>
            </div>
          )}
          {/* TODO: Add Gini, Org Diversity for general comparison */}
        </>
      )}
       {/* TODO: Consider adding charts for bus factor, contributor counts etc. */}
    </MetricCard>
  );
};

export default ContributorSection;
