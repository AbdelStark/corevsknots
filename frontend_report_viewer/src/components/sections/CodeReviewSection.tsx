// src/components/sections/CodeReviewSection.tsx
import MetricCard from '@/components/MetricCard';
import { ComparisonData } from '@/types/reportTypes';
import React from 'react';
// import ComparisonBarChart from '@/components/ComparisonBarChart'; // Removed for single fighter view
import styles from '@/styles/Home.module.css';

interface CodeReviewSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const CodeReviewSection: React.FC<CodeReviewSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.code_review;

  if (!metrics) {
    return <MetricCard title={`${displayName} - Code Review`}><p>Code Review data not available.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - Code Review`}>
      <div className={styles.metricPair} title="Average number of formal review submissions per PR.">
        <span className={styles.metricLabel}>Reviews per PR:</span>
        <span className={styles.metricValue}>{metrics.reviews_per_pr?.toFixed(1)}</span>
      </div>
      <div className={styles.metricPair} title="Average number of review comments per PR.">
        <span className={styles.metricLabel}>Comments per PR:</span>
        <span className={styles.metricValue}>{metrics.comments_per_pr?.toFixed(1)}</span>
      </div>
      <div className={styles.metricPair} title="Score (0-10) indicating review thoroughness (multiple reviewers, substantive comments/changes requested). Higher is better.">
        <span className={styles.metricLabel}>Thoroughness Score:</span>
        <span className={styles.metricValue}>{metrics.review_thoroughness_score?.toFixed(1)}/10</span>
      </div>
      <div className={styles.metricPair} title="Percentage of merged PRs that were merged by the PR author. Lower indicates more independent review.">
        <span className={styles.metricLabel}>Self-Merged Ratio:</span>
        <span className={styles.metricValue}>{(metrics.self_merged_ratio !== undefined ? (metrics.self_merged_ratio * 100).toFixed(1) : 'N/A')}%</span>
      </div>
      <div className={styles.metricPair} title="Average time in hours from PR creation to the first formal review. Lower is better.">
        <span className={styles.metricLabel}>Avg. Time to First Review:</span>
        <span className={styles.metricValue}>{metrics.avg_time_to_first_review?.toFixed(1)} hours</span>
      </div>
      <div className={styles.metricPair} title="Score (0-10) indicating speed of first review. Higher is better.">
        <span className={styles.metricLabel}>Responsiveness Score:</span>
        <span className={styles.metricValue}>{metrics.review_responsiveness_score?.toFixed(1)}/10</span>
      </div>
    </MetricCard>
  );
};

export default CodeReviewSection;
