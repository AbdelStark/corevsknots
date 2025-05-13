import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import Head from 'next/head';
import { useEffect, useState } from 'react';
// Remove direct MetricCard and ComparisonBarChart imports if only used within sections
// import MetricCard from '@/components/MetricCard';
// import ComparisonBarChart from '@/components/ComparisonBarChart';

// Import section components
import CiCdSection from '@/components/sections/CiCdSection';
import CodeReviewSection from '@/components/sections/CodeReviewSection';
import CommitSection from '@/components/sections/CommitSection';
import ContributorSection from '@/components/sections/ContributorSection';
import IssueSection from '@/components/sections/IssueSection';
import OverallScoresSection from '@/components/sections/OverallScoresSection';
import PullRequestSection from '@/components/sections/PullRequestSection';
import TestSection from '@/components/sections/TestSection';

export default function Home() {
  const [reportData, setReportData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
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
  }, []);

  return (
    <>
      <Head>
        <title>Core vs Knots Health Comparison</title>
        <meta name="description" content="Comparison report for Bitcoin Core and Bitcoin Knots repository health" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
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

            <OverallScoresSection reportData={reportData} />
            <ContributorSection reportData={reportData} />
            <CommitSection reportData={reportData} />
            <PullRequestSection reportData={reportData} />
            <CodeReviewSection reportData={reportData} />

            {/* TODO: Add more sections for CI/CD, Issues, Tests, and other metrics and charts */}
            <CiCdSection reportData={reportData} />
            <IssueSection reportData={reportData} />
            <TestSection reportData={reportData} />
          </div>
        )}
      </main>
    </>
  );
}
