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
import { getDisplayName, getRepoUrl } from '@/utils/displayName'; // Import from utils

// const getRepoUrl = (repoFullName: string): string => { // MOVED
//   return `https://github.com/${repoFullName}`;
// };

// Function to get display name - REMOVED, now imported

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
        <title>Core VS Knots: Health Battle!</title>
        <meta name="description" content="Bitcoin Core vs. Bitcoin Knots repository health comparison - Arcade Style!" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className={styles.main}>
        <div className={styles.headerContainer}>
            <h1 className={styles.title}>
              <a
                href={reportData ? getRepoUrl(reportData.repo1.name) : '#'}
                target="_blank" rel="noopener noreferrer"
                className={styles.fighterNameLink}
                title={`View ${reportData?.repo1.name} on GitHub`}
              >
                {reportData ? getDisplayName(reportData.repo1.name) : 'Fighter 1'}
              </a>
              <span className={styles.vsTextLarge}>VS</span>
              <a
                href={reportData ? getRepoUrl(reportData.repo2.name) : '#'}
                target="_blank" rel="noopener noreferrer"
                className={styles.fighterNameLink}
                title={`View ${reportData?.repo2.name} on GitHub`}
              >
                {reportData ? getDisplayName(reportData.repo2.name) : 'Fighter 2'}
              </a>
            </h1>
        </div>

        {loading && <p className={styles.description}>SELECT YOUR FIGHTER! (Loading...)</p>}
        {error && <p className={`${styles.description} ${styles.errorMessage}`}>SYSTEM ERROR! ({error})</p>}

        {reportData && (
          <>
            <div className={styles.reportMeta}>
                <p>
                    Comparing {reportData.repo1.name} vs {reportData.repo2.name}
                </p>
                <p>Analysis Date: {new Date(reportData.analysis_metadata.date).toLocaleDateString()}</p>
                <p>Period: {reportData.analysis_metadata.period_months} Months</p>
                {reportData.analysis_metadata.is_fight_mode && <p className={styles.fightModeText}>FIGHT MODE ENGAGED!</p>}
            </div>

            {/* Overall Scores Health Bar - Placed above columns */}
            <OverallScoresSection reportData={reportData} />

            <div className={styles.fightersContainer}>
              {/* Fighter 1 Column (Core) */}
              <div className={`${styles.fighterColumn} ${styles.fighterColumn1}`}>
                {/* <h2 className={styles.fighterTitle}>{reportData.repo1.name}</h2> */} {/* Title now in main header */}
                <ContributorSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <CommitSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <PullRequestSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <CodeReviewSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <CiCdSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <IssueSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <TestSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
              </div>

              {/* Fighter 2 Column (Knots) */}
              <div className={`${styles.fighterColumn} ${styles.fighterColumn2}`}>
                {/* <h2 className={styles.fighterTitle}>{reportData.repo2.name}</h2> */} {/* Title now in main header */}
                <ContributorSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <CommitSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <PullRequestSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <CodeReviewSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <CiCdSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <IssueSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <TestSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
              </div>
            </div>
          </>
        )}
      </main>
    </>
  );
}
