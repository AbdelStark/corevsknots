import InlineMetricBar from '@/components/InlineMetricBar';
import homeStyles from '@/styles/Home.module.css';
import cardStyles from '@/styles/MetricCard.module.css';
import React from 'react';

// Helper to determine if a value is better (higher is better by default)
export const isBetter = (val1: number | undefined, val2: number | undefined, lowerIsBetter: boolean = false): boolean | null => {
  if (val1 === undefined || val2 === undefined) return null;
  if (lowerIsBetter) return val1 < val2;
  return val1 > val2;
};

export interface MetricDisplayProps {
  label: string;
  // Value for the primary fighter column this card is in
  primaryValue: string | number | undefined;
  // Value for the opponent fighter
  opponentValue: string | number | undefined;
  unit?: string;
  lowerIsBetter?: boolean;
  tooltip?: string;
  // To correctly style the primary fighter's value (repo1 or repo2 color)
  primaryFighterKey: 'repo1' | 'repo2';
  precision?: number;
  showBar?: boolean;
  barMaxValue?: number;
}

export const MetricDisplay: React.FC<MetricDisplayProps> = ({
  label,
  primaryValue,
  opponentValue,
  unit = '',
  lowerIsBetter = false,
  tooltip,
  primaryFighterKey,
  precision,
  showBar = false,
  barMaxValue,
}) => {
  const formatValue = (val: string | number | undefined, p?: number): string => {
    if (val === undefined || val === null) return 'N/A';
    if (typeof val === 'string') return val; // Already a string (e.g., 'Yes'/'No')
    // Use provided precision, or default to 1 if float, 0 if integer
    const effectivePrecision = p ?? (val % 1 !== 0 ? 1 : 0);
    return val.toFixed(effectivePrecision);
  };

  const valPrimaryDisplay = `${formatValue(primaryValue, precision)}${unit}`;
  const valOpponentDisplay = `${formatValue(opponentValue, precision)}${unit}`;

  let primaryStyle = primaryFighterKey === 'repo1' ? homeStyles.valueRepo1 : homeStyles.valueRepo2;
  let opponentStyle = primaryFighterKey === 'repo1' ? homeStyles.valueRepo2 : homeStyles.valueRepo1;
  let primaryIsWinner = false;
  let pairStyle = homeStyles.metricPair; // Default style for the pair
  let icon = null;

  const better = isBetter(primaryValue as number, opponentValue as number, lowerIsBetter);

  if (better === true) { // Primary is better
    primaryStyle = `${primaryStyle} ${cardStyles.metricValueBetter}`;
    opponentStyle = `${opponentStyle} ${cardStyles.metricValueWorse}`;
    primaryIsWinner = true;
    pairStyle = `${homeStyles.metricPair} ${cardStyles.metricPairWinning}`;
    icon = <span className={`${cardStyles.metricIcon} ${cardStyles.winningIcon}`}>▲</span>; // Up arrow for winning
  } else if (better === false) { // Opponent is better
    opponentStyle = `${opponentStyle} ${cardStyles.metricValueBetter}`;
    primaryStyle = `${primaryStyle} ${cardStyles.metricValueWorse}`;
    pairStyle = `${homeStyles.metricPair} ${cardStyles.metricPairLosing}`;
    icon = <span className={`${cardStyles.metricIcon} ${cardStyles.losingIcon}`}>▼</span>; // Down arrow for losing
  }

  const diff = (primaryValue !== undefined && opponentValue !== undefined && typeof primaryValue === 'number' && typeof opponentValue === 'number')
               ? (primaryValue - opponentValue)
               : undefined;
  let diffDisplay = 'N/A';
  let diffStyle = cardStyles.metricValue; // Neutral style for difference itself, using cardStyles

  if (diff !== undefined) {
    const primaryWins = lowerIsBetter ? diff < 0 : diff > 0;
    const opponentWins = lowerIsBetter ? diff > 0 : diff < 0;

    const diffPrecision = precision ?? ((typeof primaryValue ==='number' && primaryValue % 1 !== 0) ||
                                     (typeof opponentValue ==='number' && opponentValue % 1 !== 0) ||
                                     (diff % 1 !== 0) ? 1 : 0);
    diffDisplay = `${diff > 0 ? '+' : ''}${diff.toFixed(diffPrecision)}${unit}`;

    if (primaryWins) diffStyle = `${cardStyles.metricValueBetter} ${primaryStyle.includes(homeStyles.valueRepo1) ? homeStyles.valueRepo1 : homeStyles.valueRepo2 }`;
    else if (opponentWins) diffStyle = `${cardStyles.metricValueBetter} ${opponentStyle.includes(homeStyles.valueRepo1) ? homeStyles.valueRepo1 : homeStyles.valueRepo2 }`;
  }

  const primaryBarColor = primaryFighterKey === 'repo1' ? '#45aaf2' : '#ff6b81';

  return (
    <div className={pairStyle} title={tooltip}>
      <span className={homeStyles.metricLabel}>{icon}{label}:</span>
      <div style={{ textAlign: 'right', display: 'flex', alignItems: 'center', justifyContent:'flex-end' }}>
        <span className={primaryStyle}>
          {valPrimaryDisplay}
          {primaryIsWinner && <span className={cardStyles.winIndicator}> WIN!</span>}
        </span>
        {showBar && typeof primaryValue === 'number' && (
          <InlineMetricBar
            value={primaryValue}
            maxValue={barMaxValue}
            barColor={primaryBarColor}
            height="10px" // Slightly smaller bar for inline
          />
        )}
        <span className={cardStyles.metricValue} style={{ marginLeft: '10px', minWidth: '70px', display: 'inline-block' }}>
            (<span className={diffStyle}>{diffDisplay}</span>)
        </span>
      </div>
    </div>
  );
};
