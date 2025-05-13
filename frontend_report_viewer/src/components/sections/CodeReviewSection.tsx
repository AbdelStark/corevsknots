// src/components/sections/CodeReviewSection.tsx
import ComparisonBarChart from '@/components/ComparisonBarChart';
import MetricCard from '@/components/MetricCard';
import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';

interface CodeReviewSectionProps {
  reportData: ComparisonData;
}

const CodeReviewSection: React.FC<CodeReviewSectionProps> = ({ reportData }) => {
  const metrics1 = reportData.repo1.metrics.code_review;
  const metrics2 = reportData.repo2.metrics.code_review;

  if (!metrics1 || !metrics2) {
    return <MetricCard title="Code Review Process Comparison"><p>Code Review data not available.</p></MetricCard>;
  }

  const repo1Name = reportData.repo1.name;
  const repo2Name = reportData.repo2.name;

  return (
    <MetricCard title="Code Review Process Comparison">
      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Review Thoroughness:</span>
        <span>
          <span className={styles.valueRepo1}>{metrics1.review_thoroughness_score?.toFixed(1)}/10</span> vs <span className={styles.valueRepo2}>{metrics2.review_thoroughness_score?.toFixed(1)}/10</span>
        </span>
      </div>
      {metrics1.review_thoroughness_score !== undefined && metrics2.review_thoroughness_score !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.review_thoroughness_score}
          repo2Score={metrics2.review_thoroughness_score}
          chartTitle="Review Thoroughness Score"
          scoreSuffix="/10"
          maxValue={10}
        />
      )}

      <div className={styles.metricPair}>
        <span className={styles.metricLabel}>Self-Merged Ratio:</span>
        <span>
          <span className={styles.valueRepo1}>{(metrics1.self_merged_ratio !== undefined ? (metrics1.self_merged_ratio * 100).toFixed(1) : 'N/A')}%</span> vs <span className={styles.valueRepo2}>{(metrics2.self_merged_ratio !== undefined ? (metrics2.self_merged_ratio * 100).toFixed(1) : 'N/A')}%</span>
        </span>
      </div>
      {metrics1.self_merged_ratio !== undefined && metrics2.self_merged_ratio !== undefined && (
        <ComparisonBarChart
          repo1Name={repo1Name}
          repo2Name={repo2Name}
          repo1Score={metrics1.self_merged_ratio * 100}
          repo2Score={metrics2.self_merged_ratio * 100}
          chartTitle="Self-Merged Ratio (Lower is Better)"
          scoreSuffix="%"
          maxValue={Math.max(metrics1.self_merged_ratio * 100 || 0, metrics2.self_merged_ratio * 100 || 0, 10) * 1.2}
        />
      )}
      {/* TODO: Add other code review metrics */}
    </MetricCard>
  );
};

export default CodeReviewSection;
