import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css'; // Re-using some styles for now
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';
// import ComparisonBarChart from '@/components/ComparisonBarChart'; // If you add charts here

interface ContributorSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2'; // Added fighterKey
}

const ContributorSection: React.FC<ContributorSectionProps> = ({ reportData, fighterKey }) => {
  const metrics = reportData[fighterKey].metrics.contributor;
  const repoName = reportData[fighterKey].name;
  // Determine opponent for specific fight mode comparisons if necessary
  // const opponentKey = fighterKey === 'repo1' ? 'repo2' : 'repo1';
  // const opponentMetrics = reportData[opponentKey].metrics.contributor;

  if (!metrics) {
    return <MetricCard title={`${repoName} - Contributors`}><p>Contributor data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${repoName} - Contributors`}>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Total (API):</span>
        <span className={styles.metricValue}>{metrics.total_contributors ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Active:</span>
        <span className={styles.metricValue}>{metrics.active_contributors ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Active Ratio:</span>
        <span className={styles.metricValue}>{(metrics.active_ratio !== undefined ? (metrics.active_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>

      {/* Fight Mode Specific for Knots (repo2) */}
      {reportData.analysis_metadata.is_fight_mode && fighterKey === 'repo2' && (
        <>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>Original Knots Authors:</span>
            <span className={styles.metricValue}>{metrics.knots_contributors_with_original_work ?? 'N/A'}</span>
          </div>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>Knots Bus Factor (Original):</span>
            <span className={styles.metricValue}>{metrics.knots_original_bus_factor ?? 'N/A'}</span>
          </div>
          <div className={styles.metricPair}>
            <span className={styles.metricLabel}>Knots Gini (Original):</span>
            <span className={styles.metricValue}>{metrics.knots_original_contributor_gini?.toFixed(3) ?? 'N/A'}</span>
          </div>
        </>
      )}
      {/* General Bus Factor & Gini */}
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Bus Factor (General):</span>
        <span className={styles.metricValue}>{metrics.bus_factor ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Gini (General):</span>
        <span className={styles.metricValue}>{metrics.contributor_gini?.toFixed(3) ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Org. Count (Email Domains):</span>
        <span className={styles.metricValue}>{metrics.organization_count ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Org. Diversity (Shannon):</span>
        <span className={styles.metricValue}>{metrics.organization_diversity?.toFixed(3) ?? 'N/A'}</span>
      </div>
      {/* TODO: Add charts for bus factor, Gini, org diversity */}
    </MetricCard>
  );
};

export default ContributorSection;
