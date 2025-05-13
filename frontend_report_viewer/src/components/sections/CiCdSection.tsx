import MetricCard from '@/components/MetricCard';
import homeStyles from '@/styles/Home.module.css';
import { ComparisonData } from '@/types/reportTypes';
import { MetricDisplay } from '@/utils/metricDisplayUtils';
import React from 'react';
// import styles from '@/styles/Home.module.css';

interface CiCdSectionProps {
  reportData: ComparisonData;
  fighterKey: 'repo1' | 'repo2';
  displayName: string;
}

const CiCdSection: React.FC<CiCdSectionProps> = ({ reportData, fighterKey, displayName }) => {
  const metrics = reportData[fighterKey].metrics.ci_cd;
  const opponentKey = fighterKey === 'repo1' ? 'repo2' : 'repo1';
  const opponentMetrics = reportData[opponentKey].metrics.ci_cd;

  if (!metrics || !opponentMetrics) {
    return <MetricCard title={`${displayName} - CI/CD`}><p>CI/CD data not fully available for comparison.</p></MetricCard>;
  }

  return (
    <MetricCard title={`${displayName} - CI/CD`}>
      <MetricDisplay
        label="Has CI"
        primaryValue={metrics.has_ci ? 'Yes' : 'No'} // Convert boolean to string for display
        opponentValue={opponentMetrics.has_ci ? 'Yes' : 'No'}
        primaryFighterKey={fighterKey}
        tooltip="Whether Continuous Integration (CI) is detected."
      />
      {/* For boolean, direct comparison in MetricDisplay might not be ideal, text display is fine for now */}

      {metrics.has_ci && opponentMetrics.has_ci && (
        <>
          <MetricDisplay
            label="Workflow Success Rate"
            primaryValue={metrics.workflow_success_rate !== undefined ? metrics.workflow_success_rate * 100 : undefined}
            opponentValue={opponentMetrics.workflow_success_rate !== undefined ? opponentMetrics.workflow_success_rate * 100 : undefined}
            primaryFighterKey={fighterKey}
            unit="%"
            tooltip="Percentage of CI workflow runs that succeeded."
          />
          <MetricDisplay
            label="Workflows per Day"
            primaryValue={metrics.workflows_per_day}
            opponentValue={opponentMetrics.workflows_per_day}
            primaryFighterKey={fighterKey}
            tooltip="Average number of CI workflow runs per day."
          />
          <MetricDisplay
            label="Unique Workflows"
            primaryValue={metrics.unique_workflows}
            opponentValue={opponentMetrics.unique_workflows}
            primaryFighterKey={fighterKey}
            tooltip="Number of unique CI workflow configurations detected."
          />
          <MetricDisplay
            label="PRs Run CI Ratio"
            primaryValue={metrics.pr_ci_ratio !== undefined ? metrics.pr_ci_ratio * 100 : undefined}
            opponentValue={opponentMetrics.pr_ci_ratio !== undefined ? opponentMetrics.pr_ci_ratio * 100 : undefined}
            primaryFighterKey={fighterKey}
            unit="%"
            tooltip="Ratio of Pull Requests that triggered a CI run."
          />
        </>
      )}
       <div className={homeStyles.metricPair} title="Detected CI systems (e.g., GitHub Actions, Travis CI).">
        <span className={homeStyles.metricLabel}>CI Systems:</span>
        <span className={homeStyles.metricValue}>{metrics.ci_systems?.join(', ') || (metrics.ci_system_count ? `${metrics.ci_system_count} system(s)` : 'N/A')}</span>
      </div>
    </MetricCard>
  );
};

export default CiCdSection;
