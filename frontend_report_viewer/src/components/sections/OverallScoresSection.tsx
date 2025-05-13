// src/components/sections/OverallScoresSection.tsx
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';
// MetricCard is not used if we mimic NodeStatsSection structure directly for this panel
// import MetricCard from '@/components/MetricCard';
import homeStyles from '@/styles/Home.module.css'; // For .valueRepo1/.valueRepo2 colors
import cardStyles from '@/styles/MetricCard.module.css'; // For better/worse text values
import nodeStatsStyles from '@/styles/NodeStatsSection.module.css'; // Reuse these styles
import { getDisplayName } from '@/utils/displayName';

interface OverallScoresSectionProps {
  reportData: ComparisonData;
}

const OverallScoresSection: React.FC<OverallScoresSectionProps> = ({ reportData }) => {
  const score1 = reportData.repo1.metrics.overall_health_score;
  const score2 = reportData.repo2.metrics.overall_health_score;
  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  let score1Style = `${homeStyles.valueRepo1}`;
  let score2Style = `${homeStyles.valueRepo2}`;

  if (score1 !== undefined && score2 !== undefined) {
    if (score1 > score2) {
      score1Style = `${homeStyles.valueRepo1} ${cardStyles.metricValueBetter}`;
      score2Style = `${homeStyles.valueRepo2} ${cardStyles.metricValueWorse}`;
    } else if (score2 > score1) {
      score2Style = `${homeStyles.valueRepo2} ${cardStyles.metricValueBetter}`;
      score1Style = `${homeStyles.valueRepo1} ${cardStyles.metricValueWorse}`;
    }
  }

  return (
    <div className={nodeStatsStyles.nodeStatsContainer} style={{maxWidth: '600px' /* Adjust width as needed */}}>
      <h2 className={nodeStatsStyles.sectionTitle}>GITHUB HEALTH</h2>
      <div className={nodeStatsStyles.statsGrid} style={{justifyContent: 'space-around'}}>
        {/* Core Score Block */}
        <div className={`${nodeStatsStyles.statBlock} ${nodeStatsStyles.coreBlock}`}>
          <h3 className={nodeStatsStyles.statTitle}>{getDisplayName(repo1Name)}</h3>
          <p className={`${nodeStatsStyles.statValuePrimary} ${score1Style}`}>{score1?.toFixed(1) ?? 'N/A'}<span className={nodeStatsStyles.statValueSecondary}>/10</span></p>
          {/* Optional: Could add a small textual description or rank here */}
        </div>

        {/* Knots Score Block */}
        <div className={`${nodeStatsStyles.statBlock} ${nodeStatsStyles.knotsBlock}`}>
          <h3 className={nodeStatsStyles.statTitle}>{getDisplayName(repo2Name)}</h3>
          <p className={`${nodeStatsStyles.statValuePrimary} ${score2Style}`}>{score2?.toFixed(1) ?? 'N/A'}<span className={nodeStatsStyles.statValueSecondary}>/10</span></p>
          {/* Optional: Could add a small textual description or rank here */}
        </div>
      </div>
      {/* No segmented bar here, using individual styled scores */}
       <p className={nodeStatsStyles.lastUpdated} style={{fontSize: '0.7rem'}}>Overall score based on weighted category performance.</p>
    </div>
  );
};

export default OverallScoresSection;
