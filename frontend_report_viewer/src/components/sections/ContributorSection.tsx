import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css'; // Re-using some styles for now
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';
// import ComparisonBarChart from '@/components/ComparisonBarChart'; // If you add charts here

interface ContributorSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string; // Added displayName
}

const ContributorSection: React.FC<ContributorSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.contributor;
  // const repoName = reportData[fighterKey].name; // Use displayName for card title

  if (!metrics) {
    return <MetricCard title={`${displayName} - Contributors`}><p>Contributor data not available.</p></MetricCard>;
  }

  // Determine if we should show general or original metrics for this fighter
  const isKnotsInFightMode = reportData.analysis_metadata.is_fight_mode && fighterKey === 'repo2';

  const busFactorToShow = isKnotsInFightMode ? metrics.knots_original_bus_factor : metrics.bus_factor;
  const giniToShow = isKnotsInFightMode ? metrics.knots_original_contributor_gini : metrics.contributor_gini;
  const busFactorLabel = isKnotsInFightMode ? "Bus Factor (Knots Original):" : "Bus Factor (General):";
  const giniLabel = isKnotsInFightMode ? "Gini (Knots Original):" : "Gini (General):";

  return (
    <MetricCard title={`${displayName} - Contributors`}>
      <div className={styles.metricPair} title="Total unique contributors listed by the GitHub API for the analyzed period.">
        <span className={styles.metricLabel}>Total (API):</span>
        <span className={styles.metricValue}>{metrics.total_contributors ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair} title="Number of unique authors who made at least one commit in the period.">
        <span className={styles.metricLabel}>Active:</span>
        <span className={styles.metricValue}>{metrics.active_contributors ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair} title="Percentage of total contributors who were active in the period.">
        <span className={styles.metricLabel}>Active Ratio:</span>
        <span className={styles.metricValue}>{(metrics.active_ratio !== undefined ? (metrics.active_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>

      {isKnotsInFightMode && (
        <div className={styles.metricPair} title="Number of authors who made original (non-Core merge) commits to Knots.">
            <span className={styles.metricLabel}>Original Knots Authors:</span>
            <span className={styles.metricValue}>{metrics.knots_contributors_with_original_work ?? 'N/A'}</span>
        </div>
      )}

      <div className={styles.metricPair} title="Minimum number of contributors whose departure would critically impact the project (loss of 80% of contributions). Lower is riskier.">
        <span className={styles.metricLabel}>{busFactorLabel}</span>
        <span className={styles.metricValue}>{busFactorToShow ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair} title="Measures commit inequality (0=perfect equality, 1=perfect inequality). Higher indicates more centralized development.">
        <span className={styles.metricLabel}>{giniLabel}</span>
        <span className={styles.metricValue}>{giniToShow?.toFixed(3) ?? 'N/A'}</span>
      </div>

      <div className={styles.metricPair} title="Number of unique email domains among commit authors.">
        <span className={styles.metricLabel}>Org. Count (Email Domains):</span>
        <span className={styles.metricValue}>{metrics.organization_count ?? 'N/A'}</span>
      </div>
      <div className={styles.metricPair} title="Shannon entropy of contributor distribution across email domains (0-1). Higher indicates more diverse organizational representation.">
        <span className={styles.metricLabel}>Org. Diversity (Shannon):</span>
        <span className={styles.metricValue}>{metrics.organization_diversity?.toFixed(3) ?? 'N/A'}</span>
      </div>
      {/* TODO: Add charts for bus factor, Gini, org diversity */}
    </MetricCard>
  );
};

export default ContributorSection;
