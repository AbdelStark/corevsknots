import styles from '@/styles/InlineMetricBar.module.css';
import React from 'react';

interface InlineMetricBarProps {
  value: number | undefined; // Current value
  maxValue?: number;       // Max value for the bar (e.g., 100 for %, 10 for score)
  barColor?: string;       // Custom color for the bar
  height?: string;         // e.g., '10px'
  tooltip?: string;
}

const InlineMetricBar: React.FC<InlineMetricBarProps> = ({
  value = 0,
  maxValue = 100,
  barColor,
  height = '12px',
  tooltip
}) => {
  const percentage = Math.max(0, Math.min((value / maxValue) * 100, 100));

  // Default to fighter color or a generic color if not provided
  const defaultBarColor = barColor || '#feca57'; // Neon yellow default

  return (
    <div className={styles.barContainer} style={{ height }} title={tooltip}>
      <div
        className={styles.barFill}
        style={{
          width: `${percentage}%`,
          backgroundColor: defaultBarColor,
        }}
      />
    </div>
  );
};

export default InlineMetricBar;
