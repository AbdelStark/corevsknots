import {
    BarElement,
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LinearScale,
    Title,
    Tooltip,
} from 'chart.js';
import React from 'react';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ComparisonBarChartProps {
  repo1Name: string;
  repo2Name: string;
  repo1Score: number | undefined;
  repo2Score: number | undefined;
  chartTitle: string;
  scoreSuffix?: string;
  maxValue?: number;
}

const ComparisonBarChart: React.FC<ComparisonBarChartProps> = ({
  repo1Name,
  repo2Name,
  repo1Score,
  repo2Score,
  chartTitle,
  scoreSuffix = '',
  maxValue = 10 // Default for scores out of 10
}) => {
  const data = {
    labels: [repo1Name, repo2Name],
    datasets: [
      {
        label: 'Overall Score', // This label might be too generic, consider passing as prop
        data: [repo1Score || 0, repo2Score || 0],
        backgroundColor: [
          'rgba(52, 152, 219, 0.7)', // Blue for Repo1
          'rgba(231, 76, 60, 0.7)',  // Red for Repo2
        ],
        borderColor: [
          'rgba(52, 152, 219, 1)',
          'rgba(231, 76, 60, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false, // Usually not needed for a simple two-bar comparison
      },
      title: {
        display: true,
        text: chartTitle,
        font: {
          size: 16,
        },
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += context.parsed.y + scoreSuffix;
            }
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: maxValue,
        ticks: {
          stepSize: maxValue / 5, // Adjust stepSize as needed
        }
      },
    },
  };

  return <div style={{ height: '300px', width: '100%', maxWidth: '500px', margin: '20px auto' }}><Bar data={data} options={options} /></div>;
};

export default ComparisonBarChart;
