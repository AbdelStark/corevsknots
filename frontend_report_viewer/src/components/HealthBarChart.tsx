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

interface HealthBarChartProps {
  repo1Name: string;
  repo2Name: string;
  repo1Score: number | undefined;
  repo2Score: number | undefined;
  maxValue?: number;
}

const HealthBarChart: React.FC<HealthBarChartProps> = ({
  repo1Name,
  repo2Name,
  repo1Score = 0,
  repo2Score = 0,
  maxValue = 10,
}) => {
  const data = {
    labels: ['HP'], // Single category for horizontal bars
    datasets: [
      {
        label: repo1Name,
        data: [repo1Score],
        backgroundColor: '#45aaf2', // Fighter 1 color (Arcade Blue)
        borderColor: '#378abf',
        borderWidth: 2,
        borderRadius: 4, // Slightly rounded edges
        borderSkipped: false, // Render border on all sides
      },
      {
        label: repo2Name,
        data: [repo2Score],
        backgroundColor: '#ff6b81', // Fighter 2 color (Arcade Pink/Red)
        borderColor: '#d95a6f',
        borderWidth: 2,
        borderRadius: 4,
        borderSkipped: false,
      },
    ],
  };

  const options: any = {
    indexAxis: 'y', // This makes it a horizontal bar chart
    responsive: true,
    maintainAspectRatio: false, // Allow custom height/width via container
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          color: '#e0e0e0',
          font: {
            family: 'Press Start 2P',
            size: 10,
          },
        },
      },
      title: {
        display: false, // Title can be handled outside the chart
      },
      tooltip: {
        enabled: true,
        backgroundColor: '#1a1a2e',
        titleColor: '#feca57',
        bodyColor: '#e0e0e0',
        borderColor: '#feca57',
        borderWidth: 1,
        titleFont: {
            family: 'Press Start 2P',
        },
        bodyFont: {
            family: 'Press Start 2P',
        },
        callbacks: {
            label: function(context: any) {
                return `${context.dataset.label}: ${context.formattedValue}/${maxValue}`;
            }
        }
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        max: maxValue,
        grid: {
          color: 'rgba(255, 255, 255, 0.1)', // Lighter grid lines for dark theme
          borderColor: 'rgba(255, 255, 255, 0.1)',
        },
        ticks: {
          color: '#e0e0e0',
          font: {
            family: 'Press Start 2P',
            size: 10,
          },
          stepSize: maxValue / 2, // e.g., 0, 5, 10
        },
      },
      y: {
        grid: {
          display: false, // No y-axis grid lines for a health bar look
        },
        ticks: {
          display: false, // No y-axis labels
        },
      },
    },
  };

  // Container style for a retro health bar look
  return (
    <div style={{
        height: '100px', // Adjust height as needed
        width: '90%',
        maxWidth: '700px',
        margin: '1rem auto 2rem auto',
        padding: '10px',
        border: '3px solid #feca57',
        borderRadius: '8px',
        backgroundColor: '#2c2c54', // Darker background for the chart area
        boxShadow: '0 0 10px #feca57aa inset, 0 0 10px #feca57aa'
    }}>
      <Bar data={data} options={options} />
    </div>
  );
};

export default HealthBarChart;
