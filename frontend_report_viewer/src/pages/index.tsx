import styles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import Head from 'next/head';
import { useEffect, useState } from 'react';
// Remove direct MetricCard and ComparisonBarChart imports if only used within sections
// import MetricCard from '@/components/MetricCard';
// import ComparisonBarChart from '@/components/ComparisonBarChart';

// Import section components
import FighterImage from '@/components/FighterImage'; // Import FighterImage
import CiCdSection from '@/components/sections/CiCdSection';
import CodeReviewSection from '@/components/sections/CodeReviewSection';
import CommitSection from '@/components/sections/CommitSection';
import ContributorSection from '@/components/sections/ContributorSection';
import IssueSection from '@/components/sections/IssueSection';
import NodeStatsSection from '@/components/sections/NodeStatsSection'; // Import NodeStatsSection
import OverallScoresSection from '@/components/sections/OverallScoresSection';
import PullRequestSection from '@/components/sections/PullRequestSection';
import TestSection from '@/components/sections/TestSection';
import { getDisplayName, getRepoUrl } from '@/utils/displayName'; // Import from utils
import { ProcessedNodeStats } from './api/node-stats'; // Import type for node stats

// const getRepoUrl = (repoFullName: string): string => { // MOVED
//   return `https://github.com/${repoFullName}`;
// };

// Function to get display name - REMOVED, now imported

export default function Home() {
  const [reportData, setReportData] = useState<ComparisonData | null>(null);
  const [nodeStats, setNodeStats] = useState<ProcessedNodeStats | null>(null); // State for node stats
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [nodeStatsError, setNodeStatsError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);
        setNodeStatsError(null);

        // Fetch main report data
        const reportResponse = await fetch('/CORE_vs_KNOTS_FIGHT_REPORT.json');
        if (!reportResponse.ok) {
          throw new Error(`Failed to fetch report: ${reportResponse.status} ${reportResponse.statusText}`);
        }
        const reportJson: ComparisonData = await reportResponse.json();
        setReportData(reportJson);

        // Fetch node stats
        try {
            const nodeStatsResponse = await fetch('/api/node-stats');
            if (!nodeStatsResponse.ok) {
                const errData = await nodeStatsResponse.json();
                throw new Error(errData.error || `Failed to fetch node stats: ${nodeStatsResponse.status}`);
            }
            const nodeStatsJson: ProcessedNodeStats = await nodeStatsResponse.json();
            setNodeStats(nodeStatsJson);
        } catch (e: any) {
            console.error("Error fetching node stats:", e);
            setNodeStatsError(e.message || "Could not load node stats.");
        }

      } catch (err: any) {
        console.error("Error fetching data:", err);
        setError(err.message || "An unknown error occurred.");
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
        <a
          href="https://github.com/AbdelStark/corevsknots"
          target="_blank"
          rel="noopener noreferrer"
          className={styles.githubLink}
          title="View Project on GitHub"
        >
          {/* Simple Unicode Octagonal Icon as a placeholder. Replace with SVG/Image for better visuals */}
          <span className={styles.githubIcon}>🐙</span> {/* GitHub Octocat emoji as an example */}
          {/* Or use text: <span className={styles.githubIcon}>Code</span> */}
        </a>

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
        {nodeStatsError && <p className={`${styles.description} ${styles.errorMessage}`}>Node Stats Error: {nodeStatsError}</p>}

        {reportData && (
          <>

            {/* Top summary row for Node Stats and GitHub Health */}
            <div className={styles.topSummaryContainer}>
              {nodeStats &&
                <NodeStatsSection
                  nodeStats={nodeStats}
                  repo1Name={reportData.repo1.name}
                  repo2Name={reportData.repo2.name}
                />
              }
              {/* Display NodeStatsError within its potential space if nodeStats is null */}
              {!nodeStats && nodeStatsError &&
                  <div className={`${styles.nodeStatsContainer} ${styles.errorBox}`} style={{flex:1}}>
                      <h2 className={styles.sectionTitle} style={{color: '#ff4757'}}>Network Dominance Error</h2>
                      <p>{nodeStatsError}</p>
                  </div>
              }
              {/* Placeholder for spacing if nodeStats is null and no error */}
              {!nodeStats && !nodeStatsError && <div style={{flex:1}}></div> }

              <OverallScoresSection reportData={reportData} />
            </div>

            <div className={styles.fightersContainer}>
              <div className={`${styles.fighterColumn} ${styles.fighterColumn1}`}>
                <div className={styles.fighterHeader}>
                  <FighterImage
                    fighterName={getDisplayName(reportData.repo1.name)}
                    imageUrl="/player_core.png" // Assuming core is repo1
                    altText={`${getDisplayName(reportData.repo1.name)} Fighter Image`}
                  />
                  <h2 className={styles.fighterColumnTitle}>{getDisplayName(reportData.repo1.name)}</h2>
                </div>
                <ContributorSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <CommitSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <PullRequestSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <CodeReviewSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <CiCdSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <IssueSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
                <TestSection reportData={reportData} fighterKey="repo1" displayName={getDisplayName(reportData.repo1.name)} />
              </div>

              <div className={`${styles.fighterColumn} ${styles.fighterColumn2}`}>
                <div className={styles.fighterHeader}>
                  <FighterImage
                    fighterName={getDisplayName(reportData.repo2.name)}
                    imageUrl="/player_knots.png" // Assuming knots is repo2
                    altText={`${getDisplayName(reportData.repo2.name)} Fighter Image`}
                  />
                  <h2 className={styles.fighterColumnTitle}>{getDisplayName(reportData.repo2.name)}</h2>
                </div>
                <ContributorSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <CommitSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <PullRequestSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <CodeReviewSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <CiCdSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <IssueSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
                <TestSection reportData={reportData} fighterKey="repo2" displayName={getDisplayName(reportData.repo2.name)} />
              </div>
            </div>

            <div className={styles.reportMeta}>
                <p>Comparing {reportData.repo1.name} vs {reportData.repo2.name}</p>
                <p>Analysis Date: {new Date(reportData.analysis_metadata.date).toLocaleDateString()}</p>
                <p>Period: {reportData.analysis_metadata.period_months} Months</p>
            </div>
          </>
        )}
      </main>
    </>
  );
}
