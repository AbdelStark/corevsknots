import ComparisonBarChart from '@/components/ComparisonBarChart'; // Import the chart component
import MetricCard from '@/components/MetricCard'; // Import the new component
import styles from '@/styles/Home.module.css'; // We'll create this next
import { ComparisonData } from '@/types/reportTypes'; // Import the types
import Head from 'next/head';
import { useEffect, useState } from 'react';

export default function Home() {
  const [reportData, setReportData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        // Assuming the JSON file is in the public folder
        const response = await fetch('/CORE_vs_KNOTS_FIGHT_REPORT.json');
        if (!response.ok) {
          throw new Error(`Failed to fetch report: ${response.status} ${response.statusText}`);
        }
        const data: ComparisonData = await response.json();
        setReportData(data);
      } catch (err: any) {
        console.error("Error fetching report data:", err);
        setError(err.message || "An unknown error occurred while fetching the report.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []); // Empty dependency array means this runs once on mount

  return (
    <>
      <Head>
        <title>Core vs Knots Health Comparison</title>
        <meta name="description" content="Comparison report for Bitcoin Core and Bitcoin Knots repository health" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" /> {/* We can add a favicon later */}
      </Head>
      <main className={styles.main}>
        <h1 className={styles.title}>
          Core vs Knots Health Comparison
        </h1>

        {loading && <p className={styles.description}>Loading report data...</p>}
        {error && <p className={styles.description} style={{ color: 'red' }}>Error: {error}</p>}

        {reportData && (
          <div className={styles.reportContainer}>
            <h2>Report for: {reportData.repo1.name} vs {reportData.repo2.name}</h2>
            <p>Analysis Date: {new Date(reportData.analysis_metadata.date).toLocaleDateString()}</p>
            <p>Analysis Period: {reportData.analysis_metadata.period_months} months</p>
            {reportData.analysis_metadata.is_fight_mode && <p><strong>Fight Mode Enabled!</strong></p>}

            <hr />

            {reportData.repo1.metrics.overall_health_score !== undefined && reportData.repo2.metrics.overall_health_score !== undefined && (
                 <ComparisonBarChart
                    repo1Name={reportData.repo1.name}
                    repo2Name={reportData.repo2.name}
                    repo1Score={reportData.repo1.metrics.overall_health_score}
                    repo2Score={reportData.repo2.metrics.overall_health_score}
                    chartTitle="Overall Health Score Comparison"
                    scoreSuffix="/10"
                    maxValue={10}
                />
            )}

            <MetricCard title="Overall Health Scores">
              <div className={styles.metricPair}>
                <span className={styles.metricLabel}>{reportData.repo1.name}:</span>
                <span className={`${styles.metricValue} ${styles.valueRepo1}`}>{reportData.repo1.metrics.overall_health_score?.toFixed(1)}/10</span>
              </div>
              <div className={styles.metricPair}>
                <span className={styles.metricLabel}>{reportData.repo2.name}:</span>
                <span className={`${styles.metricValue} ${styles.valueRepo2}`}>{reportData.repo2.metrics.overall_health_score?.toFixed(1)}/10</span>
              </div>
            </MetricCard>

            {reportData.repo1.metrics.contributor && reportData.repo2.metrics.contributor && (
              <MetricCard title="Contributor Comparison">
                <div className={styles.metricPair}>
                  <span className={styles.metricLabel}>Total Contributors (API):</span>
                  <span>
                    <span className={styles.valueRepo1}>{reportData.repo1.metrics.contributor.total_contributors}</span> vs <span className={styles.valueRepo2}>{reportData.repo2.metrics.contributor.total_contributors}</span>
                  </span>
                </div>
                {reportData.analysis_metadata.is_fight_mode && (
                  <>
                    <div className={styles.metricPair}>
                      <span className={styles.metricLabel}>Original Knots Authors:</span>
                      <span className={`${styles.metricValue} ${styles.valueRepo2}`}>{reportData.repo2.metrics.contributor?.knots_contributors_with_original_work}</span>
                    </div>
                    <div className={styles.metricPair}>
                      <span className={styles.metricLabel}>Knots Bus Factor (Original):</span>
                      <span className={`${styles.metricValue} ${styles.valueRepo2}`}>{reportData.repo2.metrics.contributor?.knots_original_bus_factor}</span>
                    </div>
                    <div className={styles.metricPair}>
                      <span className={styles.metricLabel}>Core Bus Factor (General):</span>
                      <span className={`${styles.metricValue} ${styles.valueRepo1}`}>{reportData.repo1.metrics.contributor?.bus_factor}</span>
                    </div>
                  </>
                )}
                 {/* Add general bus factor comparison if not fight mode */}
                {!reportData.analysis_metadata.is_fight_mode && reportData.repo1.metrics.contributor.bus_factor !== undefined && reportData.repo2.metrics.contributor.bus_factor !== undefined && (
                    <div className={styles.metricPair}>
                        <span className={styles.metricLabel}>Bus Factor:</span>
                        <span>
                        <span className={styles.valueRepo1}>{reportData.repo1.metrics.contributor.bus_factor}</span> vs <span className={styles.valueRepo2}>{reportData.repo2.metrics.contributor.bus_factor}</span>
                        </span>
                    </div>
                )}
              </MetricCard>
            )}

            {/* Commit Metrics */}
            {reportData.repo1.metrics.commit && reportData.repo2.metrics.commit && (
              <MetricCard title="Commit Activity Comparison">
                <div className={styles.metricPair}>
                  <span className={styles.metricLabel}>Commits per Day:</span>
                  <span>
                    <span className={styles.valueRepo1}>{reportData.repo1.metrics.commit.commits_per_day?.toFixed(1)}</span> vs <span className={styles.valueRepo2}>{reportData.repo2.metrics.commit.commits_per_day?.toFixed(1)}</span>
                  </span>
                </div>
                {reportData.repo1.metrics.commit.commits_per_day !== undefined && reportData.repo2.metrics.commit.commits_per_day !== undefined && (
                    <ComparisonBarChart
                        repo1Name={reportData.repo1.name}
                        repo2Name={reportData.repo2.name}
                        repo1Score={reportData.repo1.metrics.commit.commits_per_day}
                        repo2Score={reportData.repo2.metrics.commit.commits_per_day}
                        chartTitle="Commits per Day"
                        maxValue={Math.max(reportData.repo1.metrics.commit.commits_per_day || 0, reportData.repo2.metrics.commit.commits_per_day || 0, 1) * 1.2} // Dynamic max
                    />
                )}
                <div className={styles.metricPair}>
                  <span className={styles.metricLabel}>Commit Message Quality:</span>
                  <span>
                    <span className={styles.valueRepo1}>{reportData.repo1.metrics.commit.commit_message_quality?.quality_score?.toFixed(1)}/10</span> vs <span className={styles.valueRepo2}>{reportData.repo2.metrics.commit.commit_message_quality?.quality_score?.toFixed(1)}/10</span>
                  </span>
                </div>
                {reportData.repo1.metrics.commit.commit_message_quality?.quality_score !== undefined && reportData.repo2.metrics.commit.commit_message_quality?.quality_score !== undefined && (
                    <ComparisonBarChart
                        repo1Name={reportData.repo1.name}
                        repo2Name={reportData.repo2.name}
                        repo1Score={reportData.repo1.metrics.commit.commit_message_quality.quality_score}
                        repo2Score={reportData.repo2.metrics.commit.commit_message_quality.quality_score}
                        chartTitle="Commit Message Quality Score"
                        scoreSuffix="/10"
                        maxValue={10}
                    />
                )}
                {/* Add more commit metrics as needed */}
              </MetricCard>
            )}

            {/* Pull Request Metrics */}
            {reportData.repo1.metrics.pull_request && reportData.repo2.metrics.pull_request && (
              <MetricCard title="Pull Request Process Comparison">
                <div className={styles.metricPair}>
                  <span className={styles.metricLabel}>PR Merge Rate:</span>
                  <span>
                    <span className={styles.valueRepo1}>{(reportData.repo1.metrics.pull_request.merged_ratio !== undefined ? (reportData.repo1.metrics.pull_request.merged_ratio * 100).toFixed(1) : 'N/A' )}%</span> vs <span className={styles.valueRepo2}>{(reportData.repo2.metrics.pull_request.merged_ratio !== undefined ? (reportData.repo2.metrics.pull_request.merged_ratio * 100).toFixed(1) : 'N/A' )}%</span>
                  </span>
                </div>
                {reportData.repo1.metrics.pull_request.merged_ratio !== undefined && reportData.repo2.metrics.pull_request.merged_ratio !== undefined && (
                    <ComparisonBarChart
                        repo1Name={reportData.repo1.name}
                        repo2Name={reportData.repo2.name}
                        repo1Score={reportData.repo1.metrics.pull_request.merged_ratio * 100}
                        repo2Score={reportData.repo2.metrics.pull_request.merged_ratio * 100}
                        chartTitle="PR Merge Rate"
                        scoreSuffix="%"
                        maxValue={100}
                    />
                )}
                <div className={styles.metricPair}>
                  <span className={styles.metricLabel}>PR Velocity Score:</span>
                  <span>
                    <span className={styles.valueRepo1}>{reportData.repo1.metrics.pull_request.pr_velocity_score?.toFixed(1)}/10</span> vs <span className={styles.valueRepo2}>{reportData.repo2.metrics.pull_request.pr_velocity_score?.toFixed(1)}/10</span>
                  </span>
                </div>
                {reportData.repo1.metrics.pull_request.pr_velocity_score !== undefined && reportData.repo2.metrics.pull_request.pr_velocity_score !== undefined && (
                    <ComparisonBarChart
                        repo1Name={reportData.repo1.name}
                        repo2Name={reportData.repo2.name}
                        repo1Score={reportData.repo1.metrics.pull_request.pr_velocity_score}
                        repo2Score={reportData.repo2.metrics.pull_request.pr_velocity_score}
                        chartTitle="PR Velocity Score"
                        scoreSuffix="/10"
                        maxValue={10}
                    />
                )}
                {/* Add more PR metrics as needed */}
              </MetricCard>
            )}

            {/* Code Review Metrics */}
            {reportData.repo1.metrics.code_review && reportData.repo2.metrics.code_review && (
              <MetricCard title="Code Review Process Comparison">
                <div className={styles.metricPair}>
                  <span className={styles.metricLabel}>Review Thoroughness:</span>
                  <span>
                    <span className={styles.valueRepo1}>{reportData.repo1.metrics.code_review.review_thoroughness_score?.toFixed(1)}/10</span> vs <span className={styles.valueRepo2}>{reportData.repo2.metrics.code_review.review_thoroughness_score?.toFixed(1)}/10</span>
                  </span>
                </div>
                {reportData.repo1.metrics.code_review.review_thoroughness_score !== undefined && reportData.repo2.metrics.code_review.review_thoroughness_score !== undefined && (
                    <ComparisonBarChart
                        repo1Name={reportData.repo1.name}
                        repo2Name={reportData.repo2.name}
                        repo1Score={reportData.repo1.metrics.code_review.review_thoroughness_score}
                        repo2Score={reportData.repo2.metrics.code_review.review_thoroughness_score}
                        chartTitle="Review Thoroughness Score"
                        scoreSuffix="/10"
                        maxValue={10}
                    />
                )}
                <div className={styles.metricPair}>
                  <span className={styles.metricLabel}>Self-Merged Ratio:</span>
                  <span>
                    <span className={styles.valueRepo1}>{(reportData.repo1.metrics.code_review.self_merged_ratio !== undefined ? (reportData.repo1.metrics.code_review.self_merged_ratio * 100).toFixed(1) : 'N/A' )}%</span> vs <span className={styles.valueRepo2}>{(reportData.repo2.metrics.code_review.self_merged_ratio !== undefined ? (reportData.repo2.metrics.code_review.self_merged_ratio * 100).toFixed(1) : 'N/A' )}%</span>
                  </span>
                </div>
                {reportData.repo1.metrics.code_review.self_merged_ratio !== undefined && reportData.repo2.metrics.code_review.self_merged_ratio !== undefined && (
                    <ComparisonBarChart
                        repo1Name={reportData.repo1.name}
                        repo2Name={reportData.repo2.name}
                        repo1Score={reportData.repo1.metrics.code_review.self_merged_ratio * 100}
                        repo2Score={reportData.repo2.metrics.code_review.self_merged_ratio * 100}
                        chartTitle="Self-Merged Ratio (Lower is Better)"
                        scoreSuffix="%"
                        maxValue={Math.max(reportData.repo1.metrics.code_review.self_merged_ratio*100 || 0, reportData.repo2.metrics.code_review.self_merged_ratio*100 || 0, 10) * 1.2} // Dynamic max
                    />
                )}
                {/* Add more code review metrics as needed */}
              </MetricCard>
            )}

            {/* TODO: Add more sections for other metrics and charts */}
          </div>
        )}
      </main>
    </>
  );
}
