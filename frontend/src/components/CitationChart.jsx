import { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

/**
 * Component for displaying a chart of the most cited articles in the current session
 */
const CitationChart = ({ citations }) => {
  const [citationCounts, setCitationCounts] = useState({});
  const [chartData, setChartData] = useState(null);
  
  // Process citations whenever they change
  useEffect(() => {
    if (!citations || citations.length === 0) return;
    
    // Reset and recalculate all citation counts from scratch
    // This is more reliable than incremental updates
    const newCounts = {};
    
    // Count each unique source_doc_id
    citations.forEach(citation => {
      const { source_doc_id } = citation;
      if (source_doc_id) {
        newCounts[source_doc_id] = (newCounts[source_doc_id] || 0) + 1;
      }
    });
    
    setCitationCounts(newCounts);
  }, [citations]);
  
  // Update chart data when citation counts change
  useEffect(() => {
    if (Object.keys(citationCounts).length === 0) return;
    
    // Sort sources by citation count (descending)
    const sortedSources = Object.entries(citationCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5); // Take top 5
    
    const labels = sortedSources.map(([source]) => {
      // Truncate long source names
      return source.length > 20 ? source.substring(0, 17) + '...' : source;
    });
    
    const data = sortedSources.map(([, count]) => count);
    
    setChartData({
      labels,
      datasets: [
        {
          label: 'Citation Count',
          data,
          backgroundColor: 'rgba(74, 107, 255, 0.7)',
          borderColor: 'rgba(74, 107, 255, 1)',
          borderWidth: 1,
        },
      ],
    });
  }, [citationCounts]);
  
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: 'Most Cited Articles (This Session)',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          title: (tooltipItems) => {
            const index = tooltipItems[0].dataIndex;
            const sourceId = Object.keys(citationCounts)
              .sort((a, b) => citationCounts[b] - citationCounts[a])
              .slice(0, 5)[index];
            return sourceId;
          },
          label: (context) => {
            return `Citations: ${context.parsed.y}`;
          }
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
      },
    },
  };
  
  if (!chartData || Object.keys(citationCounts).length === 0) {
    return (
      <div className="bg-gray-50 p-6 rounded-lg text-center border border-gray-200">
        <h3 className="text-lg font-medium text-gray-800 mb-2">Most Cited Articles (This Session)</h3>
        <p className="text-gray-600">No citations yet. Ask questions to see citation statistics.</p>
      </div>
    );
  }
  
  return (
    <div>
      <div className="h-64 md:h-80">
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
};

export default CitationChart;
