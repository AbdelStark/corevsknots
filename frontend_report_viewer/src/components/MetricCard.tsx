import styles from '@/styles/MetricCard.module.css'; // We'll create this CSS module next
import React from 'react';

interface MetricCardProps {
  title: string;
  children: React.ReactNode;
  // You can add more props later, e.g., for specific styling based on score, or chart data
}

const MetricCard: React.FC<MetricCardProps> = ({ title, children }) => {
  return (
    <div className={styles.card}>
      <h3 className={styles.cardTitle}>{title}</h3>
      <div className={styles.cardContent}>
        {children}
      </div>
    </div>
  );
};

export default MetricCard;
