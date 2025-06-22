import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Chart as ChartJS,
  ArcElement,
  CategoryScale,
  LinearScale,
  BarElement,
  LogarithmicScale,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from "chart.js";
import { Doughnut, Bar } from "react-chartjs-2";

// register all required components & scales
ChartJS.register(
  ArcElement,          // for Doughnut
  CategoryScale,
  LinearScale,
  LogarithmicScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

type MonthlyRecord = {
  Month: string;
  Credit: number;
  Debit: number;
  Savings: number;
};
type BudgetData = {
  category_expenses: Record<string, number>;
  monthly_summary: MonthlyRecord[];
  recommendation: { suggestion: string };
};

const colors = [
  "#FF6384",
  "#36A2EB",
  "#FFCE56",
  "#4BC0C0",
  "#9966FF",
  "#FF9F40",
  "#8DD1E1",
  "#D62728",
  "#2CA02C",
];

const BudgetDashboard: React.FC = () => {
  const [data, setData] = useState<BudgetData | null>(null);

  useEffect(() => {
    axios
      .get<BudgetData>("http://localhost:8000/budget-summary")
      .then((res) => setData(res.data))
      .catch(console.error);
  }, []);

  if (!data) return <div>Loading...</div>;

  const { category_expenses, monthly_summary, recommendation } = data;

  // --- Doughnut setup ---
  const categoryKeys = Object.keys(category_expenses);
  const doughnutData = {
    labels: categoryKeys,
    datasets: [
      {
        data: categoryKeys.map((k) => category_expenses[k]),
        backgroundColor: categoryKeys.map((_, i) => colors[i % colors.length]),
        hoverOffset: 10,
      },
    ],
  };
  const doughnutOptions: ChartOptions<"doughnut"> = {
    maintainAspectRatio: false,
    plugins: {
      legend: { position: "right" },
      title: { display: false },
    },
  };

  // --- Bar setup (log scale) ---
  const labels = monthly_summary.map((m) => m.Month);
  const rawValues = monthly_summary.map((m) => m.Savings);
  const plotValues = rawValues.map((v) => Math.max(v, 1)); // avoid zeros

  const barData = {
    labels,
    datasets: [
      {
        label: "Savings",
        data: plotValues,
        backgroundColor: labels.map((_, i) => colors[i % colors.length]),
        barThickness: 20,
      },
    ],
  };
  const barOptions: ChartOptions<"bar"> = {
    maintainAspectRatio: false,
    scales: {
      y: {
        type: "logarithmic",
        title: { display: true, text: "Savings (log scale)" },
        ticks: {
          callback: (value) => {
            const num = Number(value);
            const idx = rawValues.indexOf(num);
            return idx >= 0 ? `₹${rawValues[idx].toLocaleString()}` : "";
          },
        },
      },
      x: { ticks: { autoSkip: false } },
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (ctx) => `₹${rawValues[ctx.dataIndex].toLocaleString()}`,
        },
      },
      legend: { display: false },
    },
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 20 }}>
      <h2>Spending by Category</h2>
      <div style={{ position: "relative", height: 300, marginBottom: 40 }}>
        <Doughnut data={doughnutData} options={doughnutOptions} redraw />
      </div>

      <h2>Monthly Savings (Log Scale)</h2>
      <div style={{ position: "relative", height: 400, marginBottom: 40 }}>
        <Bar data={barData} options={barOptions} redraw />
      </div>

      <div
        style={{
          marginTop: 20,
          padding: 20,
          background: "#f9f9f9",
          borderRadius: 8,
        }}
      >
        <h3>Recommendation</h3>
        <p>{recommendation.suggestion}</p>
      </div>
    </div>
  );
};

export default BudgetDashboard;
