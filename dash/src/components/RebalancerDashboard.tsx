import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Pie, Line } from "react-chartjs-2";

// Register Chart.js components
ChartJS.register(
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

type Summary = {
  dates: string[];
  tickers: string[];
  recommended_weights: number[];
  static_weights: number[];
  performance: {
    recommended: number;
    static: number;
  };
};

const RebalancerDashboard: React.FC = () => {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios
      .get<Summary>(
        "http://localhost:8000/rebalancer-summary?tickers=AAPL,MSFT,GOOG&episodes=300"
      )
      .then((res) => setSummary(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading rebalancer data…</p>;
  if (!summary) return <p>No data</p>;

  const { tickers, recommended_weights, static_weights, dates } = summary;

  // Pie chart for allocations
  const pieData = {
    labels: tickers,
    datasets: [
      {
        data: recommended_weights,
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56"],
      },
    ],
  };

  // Line chart for performance
  // We need to rebuild a time series; here we only got final values,
  // so you could store an array of cum. returns in the API.
  // For demo, we'll just plot the final point vs. static.
  const lineData = {
    labels: ["Static", "Recommended"],
    datasets: [
      {
        label: "Final Portfolio Value",
        data: [summary.performance.static, summary.performance.recommended],
        borderColor: "#36A2EB",
        fill: false,
      },
    ],
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h2>RL Rebalancer Allocation</h2>
      <div style={{ height: 300 }}>
        <Pie data={pieData} />
      </div>

      <h2 style={{ marginTop: 40 }}>Performance Comparison</h2>
      <div style={{ height: 300 }}>
        <Line data={lineData} />
      </div>
    </div>
  );
};

export default RebalancerDashboard;
