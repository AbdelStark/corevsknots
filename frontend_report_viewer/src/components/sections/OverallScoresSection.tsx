// src/components/sections/OverallScoresSection.tsx
import homeStyles from '@/styles/Home.module.css';
import cardStyles from '@/styles/MetricCard.module.css';
import nodeStatsStyles from '@/styles/NodeStatsSection.module.css';
import { ComparisonData, ContributorMetrics } from '@/types/reportTypes'; // Import ContributorMetrics
import { getDisplayName } from '@/utils/displayName';
import React from 'react';

interface OverallScoresSectionProps {
  reportData: ComparisonData;
}

const OverallScoresSection: React.FC<OverallScoresSectionProps> = ({ reportData }) => {
  const metrics1 = reportData.repo1.metrics;
  const metrics2 = reportData.repo2.metrics;
  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  const score1 = metrics1.overall_health_score;
  const score2 = metrics2.overall_health_score;

  let score1Style = `${homeStyles.valueRepo1}`;
  let score2Style = `${homeStyles.valueRepo2}`;
  let winnerLabel1 = '';
  let winnerLabel2 = '';

  if (score1 !== undefined && score2 !== undefined) {
    if (score1 > score2) {
      score1Style = `${homeStyles.valueRepo1} ${cardStyles.metricValueBetter}`;
      score2Style = `${homeStyles.valueRepo2} ${cardStyles.metricValueWorse}`;
      winnerLabel1 = "(WINNER!)";
    } else if (score2 > score1) {
      score2Style = `${homeStyles.valueRepo2} ${cardStyles.metricValueBetter}`;
      score1Style = `${homeStyles.valueRepo1} ${cardStyles.metricValueWorse}`;
      winnerLabel2 = "(WINNER!)";
    }
  }

  // Determine contributor count to display
  const contributorMetrics1 = metrics1.contributor as ContributorMetrics | undefined;
  const contributorMetrics2 = metrics2.contributor as ContributorMetrics | undefined;

  const displayContributors1 = contributorMetrics1?.total_contributors;
  const displayContributors2 = reportData.analysis_metadata.is_fight_mode
    ? contributorMetrics2?.knots_contributors_with_original_work
    : contributorMetrics2?.total_contributors;

  const contributorLabel2 = reportData.analysis_metadata.is_fight_mode
    ? "Original Authors:"
    : "Total Contributors:";

  return (
    <div className={nodeStatsStyles.nodeStatsContainer} style={{maxWidth: '700px', alignSelf:'flex-start' /* Adjust width and alignment */}}>
      <h2 className={nodeStatsStyles.sectionTitle}>GITHUB HEALTH</h2>
      <div className={nodeStatsStyles.statsGrid} style={{justifyContent: 'space-around'}}>
        {/* Core Stats Block */}
        <div className={`${nodeStatsStyles.statBlock} ${nodeStatsStyles.coreBlock}`}>
          <h3 className={nodeStatsStyles.statTitle}>{getDisplayName(repo1Name)}</h3>
          <p className={`${nodeStatsStyles.statValuePrimary} ${score1Style}`}>{score1?.toFixed(1) ?? 'N/A'}<span className={nodeStatsStyles.statValueSecondary}>/10 {winnerLabel1}</span></p>
          <div className={nodeStatsStyles.statExtraInfo}>
            <p title="GitHub Stars">⭐ {metrics1.repository?.github_stars?.toLocaleString() ?? 'N/A'}</p>
            <p title="GitHub Watchers">👁️ {metrics1.repository?.github_watchers?.toLocaleString() ?? 'N/A'}</p>
            <p title="Total Contributors (API)">👥 {displayContributors1?.toLocaleString() ?? 'N/A'}</p>
          </div>
        </div>

        {/* Knots Stats Block */}
        <div className={`${nodeStatsStyles.statBlock} ${nodeStatsStyles.knotsBlock}`}>
          <h3 className={nodeStatsStyles.statTitle}>{getDisplayName(repo2Name)}</h3>
          <p className={`${nodeStatsStyles.statValuePrimary} ${score2Style}`}>{score2?.toFixed(1) ?? 'N/A'}<span className={nodeStatsStyles.statValueSecondary}>/10 {winnerLabel2}</span></p>
          <div className={nodeStatsStyles.statExtraInfo}>
            <p title="GitHub Stars">⭐ {metrics2.repository?.github_stars?.toLocaleString() ?? 'N/A'}</p>
            <p title="GitHub Watchers">👁️ {metrics2.repository?.github_watchers?.toLocaleString() ?? 'N/A'}</p>
            <p title={contributorLabel2.slice(0,-1)}>👥 {displayContributors2?.toLocaleString() ?? 'N/A'}</p>
          </div>
        </div>
      </div>
       <p className={nodeStatsStyles.lastUpdated} style={{fontSize: '0.7rem'}}>Overall score based on weighted category performance.</p>
    </div>
  );
};

export default OverallScoresSection;
