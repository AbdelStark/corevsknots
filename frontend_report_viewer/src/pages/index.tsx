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

const getRepoUrl = (repoFullName: string): string => {
  return `https://github.com/${repoFullName}`;
};

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
        <div className={styles.headerContainer}>
            <h1 className={styles.title}>
            Core <span className={styles.vsText}>VS</span> Knots
            </h1>
            <p className={styles.description}>
            Repository Health Battle!
            </p>
        </div>

        {loading && <p className={styles.description}>Loading report data...</p>}
        {error && <p className={styles.description} style={{ color: '#ff4757' }}>Error: {error}</p>}

        {reportData && (
          <>
            <div className={styles.reportMeta}>
                <p>
                    Comparing
                    <a href={getRepoUrl(reportData.repo1.name)} target="_blank" rel="noopener noreferrer">{reportData.repo1.name}</a>
                    vs
                    <a href={getRepoUrl(reportData.repo2.name)} target="_blank" rel="noopener noreferrer">{reportData.repo2.name}</a>
                </p>
                <p>Analysis Date: {new Date(reportData.analysis_metadata.date).toLocaleDateString()}</p>
                <p>Analysis Period: {reportData.analysis_metadata.period_months} months</p>
                {reportData.analysis_metadata.is_fight_mode && <p><strong>FIGHT MODE!</strong></p>}
            </div>

            <div className={styles.reportContainer}>
                {/* This div will conceptually hold the two fighter columns */}
                {/* For now, sections will stack, but styling could make them side-by-side later */}
                <OverallScoresSection reportData={reportData} />
                <ContributorSection reportData={reportData} />
                <CommitSection reportData={reportData} />
                <PullRequestSection reportData={reportData} />
                <CodeReviewSection reportData={reportData} />
                <CiCdSection reportData={reportData} />
                <IssueSection reportData={reportData} />
                <TestSection reportData={reportData} />
            </div>
          </>
        )}
      </main>
    </>
  );
}
