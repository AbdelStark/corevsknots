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
        <title>Bitcoin Repo Health Viewer</title>
        <meta name="description" content="View Bitcoin repository health reports" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" /> {/* We can add a favicon later */}
      </Head>
      <main className={styles.main}>
        <h1 className={styles.title}>
          Bitcoin Repository Health Report Viewer
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

            <h3>Overall Scores:</h3>
            <p>
              {reportData.repo1.name}: {reportData.repo1.metrics.overall_health_score?.toFixed(1)}/10
            </p>
            <p>
              {reportData.repo2.name}: {reportData.repo2.metrics.overall_health_score?.toFixed(1)}/10
            </p>

            {/* Example: Contributor Metrics - this will be refactored into components later */}
            {reportData.repo1.metrics.contributor && reportData.repo2.metrics.contributor && (
              <div>
                <h3>Contributor Comparison</h3>
                <p>
                  Total (API): {reportData.repo1.name}: {reportData.repo1.metrics.contributor.total_contributors} vs {reportData.repo2.name}: {reportData.repo2.metrics.contributor.total_contributors}
                </p>
                {reportData.analysis_metadata.is_fight_mode && (
                  <>
                    <p>
                      Original Knots Authors: {reportData.repo2.metrics.contributor?.knots_contributors_with_original_work}
                    </p>
                    <p>
                      Knots Bus Factor (Original): {reportData.repo2.metrics.contributor?.knots_original_bus_factor} (Core General: {reportData.repo1.metrics.contributor?.bus_factor})
                    </p>
                  </>
                )}
              </div>
            )}
            {/* TODO: Add more sections for other metrics and charts */}
          </div>
        )}
      </main>
    </>
  );
}
