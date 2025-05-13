// src/components/sections/OverallScoresSection.tsx
import MetricCard from '@/components/MetricCard';
import StarRating from '@/components/StarRating';
import homeStyles from '@/styles/Home.module.css';
import cardStyles from '@/styles/MetricCard.module.css';
import { ComparisonData } from '@/types/reportTypes';
import { getDisplayName } from '@/utils/displayName';
import React from 'react';

interface OverallScoresSectionProps {
  reportData: ComparisonData;
}

const OverallScoresSection: React.FC<OverallScoresSectionProps> = ({ reportData }) => {
  const score1 = reportData.repo1.metrics.overall_health_score;
  const score2 = reportData.repo2.metrics.overall_health_score;
  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  let score1Class = `${cardStyles.metricValue} ${homeStyles.valueRepo1}`;
  let score2Class = `${cardStyles.metricValue} ${homeStyles.valueRepo2}`;

  if (score1 !== undefined && score2 !== undefined) {
    if (score1 > score2) {
      score1Class = `${cardStyles.metricValue} ${cardStyles.metricValueBetter} ${homeStyles.valueRepo1}`;
      score2Class = `${cardStyles.metricValue} ${cardStyles.metricValueWorse} ${homeStyles.valueRepo2}`;
    } else if (score2 > score1) {
      score2Class = `${cardStyles.metricValue} ${cardStyles.metricValueBetter} ${homeStyles.valueRepo2}`;
      score1Class = `${cardStyles.metricValue} ${cardStyles.metricValueWorse} ${homeStyles.valueRepo1}`;
    }
  }

  return (
    <MetricCard title="Overall Health Scores">
      <div className={homeStyles.metricPair}>
        <span className={homeStyles.metricLabel}>{getDisplayName(repo1Name)} Score:</span>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span className={score1Class} style={{ marginRight: '0.5rem' }}>{score1?.toFixed(1) ?? 'N/A'}/10</span>
          <StarRating score={score1} />
        </div>
      </div>
      <div className={homeStyles.metricPair}>
        <span className={homeStyles.metricLabel}>{getDisplayName(repo2Name)} Score:</span>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span className={score2Class} style={{ marginRight: '0.5rem' }}>{score2?.toFixed(1) ?? 'N/A'}/10</span>
          <StarRating score={score2} />
        </div>
      </div>
    </MetricCard>
  );
};

export default OverallScoresSection;
