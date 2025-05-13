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
  let opponentIsWinner = false;

  const better = isBetter(primaryValue as number, opponentValue as number, lowerIsBetter);

  if (better === true) { // Primary is better
    primaryStyle = `${primaryStyle} ${cardStyles.metricValueBetter}`;
    opponentStyle = `${opponentStyle} ${cardStyles.metricValueWorse}`;
    primaryIsWinner = true;
  } else if (better === false) { // Opponent is better
    opponentStyle = `${opponentStyle} ${cardStyles.metricValueBetter}`;
    primaryStyle = `${primaryStyle} ${cardStyles.metricValueWorse}`;
    opponentIsWinner = true; // Though we only show WIN! for primary here
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

  return (
    <div className={homeStyles.metricPair} title={tooltip}>
      <span className={homeStyles.metricLabel}>{label}:</span>
      <div style={{ textAlign: 'right' }}>
        <span className={primaryStyle}>
          {valPrimaryDisplay}
          {primaryIsWinner && <span className={cardStyles.winIndicator}> WIN!</span>}
        </span>
        {/* Removed direct VS text from here, can be part of overall card design */}
        {/* <span className={cardStyles.vsText}>vs</span> */}
        {/* <span className={opponentStyle}>{valOpponentDisplay}</span> */}
        <span className={cardStyles.metricValue} style={{ marginLeft: '10px', minWidth: '70px', display: 'inline-block' }}>
            (<span className={diffStyle}>{diffDisplay}</span>)
        </span>
      </div>
    </div>
  );
};
