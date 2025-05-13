import MetricCard from '@/components/MetricCard';
import { ComparisonData, ContributorMetrics as ContributorMetricsType } from '@/types/reportTypes';
import { MetricDisplay } from '@/utils/metricDisplayUtils';
import React from 'react';
// import styles from '@/styles/Home.module.css'; // Assuming MetricDisplay handles styles

interface ContributorSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const ContributorSection: React.FC<ContributorSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.contributor as ContributorMetricsType; // Type assertion
  const opponentKey = fighterKey === 'repo1' ? 'repo2' : 'repo1';
  const opponentMetrics = reportData[opponentKey].metrics.contributor as ContributorMetricsType;

  if (!metrics || !opponentMetrics) {
    return <MetricCard title={`${displayName} - Contributors`}><p>Contributor data not fully available.</p></MetricCard>;
  }

  const isKnotsInFightModeTarget = reportData.analysis_metadata.is_fight_mode && fighterKey === 'repo2';
  // const isKnotsInFightModeOpponent = reportData.analysis_metadata.is_fight_mode && opponentKey === 'repo2';

  // Determine which primary value and label to use for the first metric (Total/Original)
  const primaryTotalLabel = isKnotsInFightModeTarget ? "Original Authors" : "Total Contributors (API)";
  const primaryTotalValue = isKnotsInFightModeTarget ? metrics.knots_contributors_with_original_work : metrics.total_contributors;

  // Determine opponent's comparable value for the first metric
  const opponentTotalValue = reportData.analysis_metadata.is_fight_mode && opponentKey === 'repo2'
                             ? opponentMetrics.knots_contributors_with_original_work
                             : opponentMetrics.total_contributors;

  return (
    <MetricCard title={`${displayName} - Contributors`}>
      <MetricDisplay
        label={primaryTotalLabel}
        primaryValue={primaryTotalValue}
        opponentValue={opponentTotalValue} // Opponent's corresponding value
        primaryFighterKey={fighterKey}
        tooltip={isKnotsInFightModeTarget ? "Number of authors with original (non-Core merge) commits to Knots." : "Total unique contributors from GitHub API."}
      />
      <MetricDisplay
        label="Active Contributors"
        primaryValue={metrics.active_contributors}
        opponentValue={opponentMetrics.active_contributors}
        primaryFighterKey={fighterKey}
        tooltip="Number of unique authors who made at least one commit in the period."
      />
      <MetricDisplay
        label="Bus Factor"
        primaryValue={isKnotsInFightModeTarget ? metrics.knots_original_bus_factor : metrics.bus_factor}
        opponentValue={reportData.analysis_metadata.is_fight_mode && opponentKey === 'repo2' ? opponentMetrics.knots_original_bus_factor : opponentMetrics.bus_factor}
        primaryFighterKey={fighterKey}
        tooltip={isKnotsInFightModeTarget ? "Knots Original Bus Factor: Min. contributors for 80% of original Knots commits." : "General Bus Factor: Min. contributors for 80% of overall/filtered commits."}
        precision={0} // Bus factor is integer
      />
      <MetricDisplay
        label="Gini Coefficient"
        primaryValue={isKnotsInFightModeTarget ? metrics.knots_original_contributor_gini : metrics.contributor_gini}
        opponentValue={reportData.analysis_metadata.is_fight_mode && opponentKey === 'repo2' ? opponentMetrics.knots_original_contributor_gini : opponentMetrics.contributor_gini}
        primaryFighterKey={fighterKey}
        unit=" (0-1)" // Unit is now just for context in label, value is formatted
        lowerIsBetter={false}
        tooltip={isKnotsInFightModeTarget ? "Knots Original Gini: Measures inequality of original Knots commit distribution." : "General Gini: Measures inequality of commit distribution."}
        precision={2} // Use 2 decimal places for Gini
      />
      <MetricDisplay
        label="Org. Count (Email Domains)"
        primaryValue={metrics.organization_count}
        opponentValue={opponentMetrics.organization_count}
        primaryFighterKey={fighterKey}
        tooltip="Number of unique email domains among commit authors."
        precision={0}
      />
      <MetricDisplay
        label="Org. Diversity (Shannon)"
        primaryValue={metrics.organization_diversity}
        opponentValue={opponentMetrics.organization_diversity}
        primaryFighterKey={fighterKey}
        unit=" (0-1)"
        tooltip="Shannon entropy of contributor distribution across email domains. Higher indicates more diverse organizational representation."
        precision={3} // Shannon entropy often has 3 decimals
      />
    </MetricCard>
  );
};

export default ContributorSection;
