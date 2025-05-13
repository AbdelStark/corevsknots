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
      <div className={styles.nodeStatsContainer} style={{ minHeight: '200px' /* Ensure some height while loading */}}>
        <h2 className={styles.sectionTitle}>NETWORK DOMINANCE</h2>
        <p className={styles.loadingText}>Calculating node distribution...</p>
      </div>
    );
  }

  const coreDisplayName = getDisplayName(repo1Name);
  const knotsDisplayName = getDisplayName(repo2Name);

  // Calculate a combined share for Core + Knots for the bar, if others are significant
  // This helps the bar visually represent their proportion of the *total tracked* in uainfo.json
  const corePlusKnotsShare = nodeStats.coreShare + nodeStats.knotsShare;
  // We want the bar to represent 100% as the sum of Core + Knots + Others + BTCSuite (if shown)
  // So, the effective width for each segment should be its share of this specific total.
  // However, for simplicity now, let the bar segments just use their direct shares.
  // This means the bar might not fill 100% if there are other nodes.

  return (
    <div className={styles.nodeStatsContainer}>
      <h2 className={styles.sectionTitle}>
        NETWORK DOMINANCE
      </h2>
      <div className={styles.statsGrid} style={{ justifyContent: 'space-around' /* Ensure even spacing for 2 items */}}>
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

        {/* btcsuite and other removed from direct display */}
      </div>

      {/* Segmented Bar for Visualization - now only Core and Knots */}
      <div className={styles.segmentedBarContainer}>
        <div
          className={`${styles.segment} ${styles.coreSegment}`}
          style={{ width: `${nodeStats.coreShare}%` }} // Width is direct share of total reachable
          title={`${coreDisplayName}: ${nodeStats.coreShare.toFixed(2)}% (${nodeStats.core.count.toLocaleString()} nodes)`}
        ></div>
        <div
          className={`${styles.segment} ${styles.knotsSegment}`}
          style={{ width: `${nodeStats.knotsShare}%` }}
          title={`${knotsDisplayName}: ${nodeStats.knotsShare.toFixed(2)}% (${nodeStats.knots.count.toLocaleString()} nodes)`}
        ></div>
        {/* Placeholder for the remainder, to make the bar visually add up to 100% of tracked nodes */}
        {(nodeStats.btcsuiteShare + nodeStats.otherShare > 0) && (
            <div
            className={`${styles.segment} ${styles.otherSegmentPlaceholder}`}
            style={{ width: `${nodeStats.btcsuiteShare + nodeStats.otherShare}%` }}
            title={`Other clients (incl. BTCSuite): ${(nodeStats.btcsuiteShare + nodeStats.otherShare).toFixed(2)}%`}
            ></div>
        )}
      </div>
      {nodeStats.last_updated &&
        <p className={styles.lastUpdated}>
          Node data from <a href="https://luke.dashjr.org/programs/bitcoin/files/charts/software.html" target="_blank" rel="noopener noreferrer">Luke Dashjr</a>, last processed: {new Date(nodeStats.last_updated).toLocaleString()}
        </p>
      }
    </div>
  );
};

export default NodeStatsSection;
