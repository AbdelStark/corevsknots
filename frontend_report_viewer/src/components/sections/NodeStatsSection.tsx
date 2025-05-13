import { ProcessedNodeStats } from '@/pages/api/node-stats';
import styles from '@/styles/NodeStatsSection.module.css';
import { getDisplayName } from '@/utils/displayName';
import React from 'react';

interface NodeStatsSectionProps {
  nodeStats: ProcessedNodeStats | null;
  repo1Name: string; // Full name like bitcoin/bitcoin - used to derive Core display name
  repo2Name: string; // Full name like bitcoinknots/bitcoin - used to derive Knots display name
}

const NodeStatsSection: React.FC<NodeStatsSectionProps> = ({ nodeStats, repo1Name, repo2Name }) => {
  if (!nodeStats) {
    return (
      <div className={styles.nodeStatsContainer}>
        <h2 className={styles.sectionTitle}>NETWORK DOMINANCE</h2>
        <p className={styles.loadingText}>Calculating node distribution...</p>
      </div>
    );
  }

  const coreDisplayName = getDisplayName(repo1Name);
  const knotsDisplayName = getDisplayName(repo2Name);
  // Assuming btcsuite doesn't have a dynamic display name from repo names
  const btcsuiteDisplayName = "BTCSuite";

  const totalDisplay = nodeStats.totalReachable.toLocaleString();

  return (
    <div className={styles.nodeStatsContainer}>
      <h2 className={styles.sectionTitle}>
        NETWORK DOMINANCE
        <span className={styles.totalNodes}>(Total: {totalDisplay} Nodes)</span>
      </h2>
      <div className={styles.statsGrid}>
        <div className={`${styles.statBlock} ${styles.coreBlock}`}>
          <h3 className={styles.statTitle}>{coreDisplayName}</h3>
          <p className={styles.statValuePrimary}>{nodeStats.core.count.toLocaleString()}</p>
          <p className={styles.statValueSecondary}>{nodeStats.coreShare.toFixed(2)}%</p>
        </div>

        <div className={`${styles.statBlock} ${styles.knotsBlock}`}>
          <h3 className={styles.statTitle}>{knotsDisplayName}</h3>
          <p className={styles.statValuePrimary}>{nodeStats.knots.count.toLocaleString()}</p>
          <p className={styles.statValueSecondary}>{nodeStats.knotsShare.toFixed(2)}%</p>
        </div>

        {nodeStats.btcsuite && nodeStats.btcsuite.count > 0 && (
             <div className={`${styles.statBlock} ${styles.btcsuiteBlock}`}>
                <h3 className={styles.statTitle}>{btcsuiteDisplayName}</h3>
                <p className={styles.statValuePrimary}>{nodeStats.btcsuite.count.toLocaleString()}</p>
                <p className={styles.statValueSecondary}>{nodeStats.btcsuiteShare.toFixed(2)}%</p>
            </div>
        )}

        {nodeStats.other.count > 0 && (
             <div className={`${styles.statBlock} ${styles.otherBlock}`}>
                <h3 className={styles.statTitle}>Other Clients</h3>
                <p className={styles.statValuePrimary}>{nodeStats.other.count.toLocaleString()}</p>
                <p className={styles.statValueSecondary}>{nodeStats.otherShare.toFixed(2)}%</p>
            </div>
        )}
      </div>

      <div className={styles.segmentedBarContainer}>
        <div
          className={`${styles.segment} ${styles.coreSegment}`}
          style={{ width: `${nodeStats.coreShare}%` }}
          title={`${coreDisplayName}: ${nodeStats.coreShare.toFixed(2)}% (${nodeStats.core.count.toLocaleString()})`}
        ></div>
        <div
          className={`${styles.segment} ${styles.knotsSegment}`}
          style={{ width: `${nodeStats.knotsShare}%` }}
          title={`${knotsDisplayName}: ${nodeStats.knotsShare.toFixed(2)}% (${nodeStats.knots.count.toLocaleString()})`}
        ></div>
        {nodeStats.btcsuite && nodeStats.btcsuite.count > 0 && nodeStats.btcsuiteShare > 0 && (
            <div
            className={`${styles.segment} ${styles.btcsuiteSegment}`}
            style={{ width: `${nodeStats.btcsuiteShare}%` }}
            title={`${btcsuiteDisplayName}: ${nodeStats.btcsuiteShare.toFixed(2)}% (${nodeStats.btcsuite.count.toLocaleString()})`}
            ></div>
        )}
        {nodeStats.otherShare > 0 && (
            <div
            className={`${styles.segment} ${styles.otherSegment}`}
            style={{ width: `${nodeStats.otherShare}%` }}
            title={`Other: ${nodeStats.otherShare.toFixed(2)}% (${nodeStats.other.count.toLocaleString()})`}
            ></div>
        )}
      </div>
      {nodeStats.last_updated &&
        <p className={styles.lastUpdated}>Node data from Luke Dashjr, last processed: {new Date(nodeStats.last_updated).toLocaleString()}</p>
      }
    </div>
  );
};

export default NodeStatsSection;
