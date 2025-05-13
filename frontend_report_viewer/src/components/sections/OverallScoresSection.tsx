// src/components/sections/OverallScoresSection.tsx
import HealthBarChart from '@/components/HealthBarChart';
import MetricCard from '@/components/MetricCard';
import homeStyles from '@/styles/Home.module.css';
import cardStyles from '@/styles/MetricCard.module.css'; // Import MetricCard styles for winner/loser
import { ComparisonData } from '@/types/reportTypes';
import { getDisplayName } from '@/utils/displayName'; // Import from utils
import React from 'react';

interface OverallScoresSectionProps {
  reportData: ComparisonData;
}

const OverallScoresSection: React.FC<OverallScoresSectionProps> = ({ reportData }) => {
  const score1 = reportData.repo1.metrics.overall_health_score;
  const score2 = reportData.repo2.metrics.overall_health_score;
  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  // Determine winner for styling
  let score1Class = cardStyles.metricValue;
  let score2Class = cardStyles.metricValue;

  if (score1 !== undefined && score2 !== undefined) {
    if (score1 > score2) {
      score1Class = `${cardStyles.metricValue} ${cardStyles.metricValueBetter} ${homeStyles.valueRepo1}`;
      score2Class = `${cardStyles.metricValue} ${cardStyles.metricValueWorse} ${homeStyles.valueRepo2}`;
    } else if (score2 > score1) {
      score2Class = `${cardStyles.metricValue} ${cardStyles.metricValueBetter} ${homeStyles.valueRepo2}`;
      score1Class = `${cardStyles.metricValue} ${cardStyles.metricValueWorse} ${homeStyles.valueRepo1}`;
    } else {
        score1Class = `${cardStyles.metricValue} ${homeStyles.valueRepo1}`;
        score2Class = `${cardStyles.metricValue} ${homeStyles.valueRepo2}`;
    }
  } else {
    score1Class = `${cardStyles.metricValue} ${homeStyles.valueRepo1}`;
    score2Class = `${cardStyles.metricValue} ${homeStyles.valueRepo2}`;
  }


  return (
    <>
      {score1 !== undefined && score2 !== undefined && (
        <HealthBarChart
          repo1Name={getDisplayName(repo1Name)} // Use display name for chart label
          repo2Name={getDisplayName(repo2Name)}
          repo1Score={score1}
          repo2Score={score2}
          maxValue={10}
        />
      )}
      <MetricCard title="Overall Health Scores">
        <div className={homeStyles.metricPair}>
          <span className={homeStyles.metricLabel}>{getDisplayName(repo1Name)}:</span>
          <span className={score1Class}>{score1?.toFixed(1) ?? 'N/A'}/10</span>
        </div>
        <div className={homeStyles.metricPair}>
          <span className={homeStyles.metricLabel}>{getDisplayName(repo2Name)}:</span>
          <span className={score2Class}>{score2?.toFixed(1) ?? 'N/A'}/10</span>
        </div>
      </MetricCard>
    </>
  );
};

// Helper function (can be moved to a utils file)
// const getDisplayName = (repoFullName: string): string => {
//   if (repoFullName.toLowerCase().includes('bitcoinknots')) return 'Knots';
//   if (repoFullName.toLowerCase().includes('bitcoin/bitcoin')) return 'Core';
//   return repoFullName;
// };

export default OverallScoresSection;
