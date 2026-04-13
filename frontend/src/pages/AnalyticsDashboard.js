import React, { useEffect, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from "chart.js";
import { Bar, Pie, Line } from "react-chartjs-2";
import { BarChart3, Users, AlertTriangle, Crown, TrendingUp, Clock } from "lucide-react";
import Sidebar from "../components/Sidebar";
import { fetchAnalyticsSummary } from "../services/api";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Color palette for charts - professional dark theme colors
const CHART_COLORS = [
  "#3b82f6", // Blue
  "#06b6d4", // Cyan
  "#10b981", // Emerald
  "#f59e0b", // Amber
  "#ef4444", // Red
  "#8b5cf6", // Violet
  "#ec4899", // Pink
  "#14b8a6", // Teal
  "#f97316", // Orange
  "#6366f1", // Indigo
  "#84cc16", // Lime
];

function AnalyticsDashboard({ onNavigate }) {
  const [period, setPeriod] = useState("all");
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, [period]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchAnalyticsSummary(period);
      setData(result);
    } catch (err) {
      console.error("Error loading analytics:", err);
      setError("Failed to load analytics data");
    } finally {
      setLoading(false);
    }
  };

  // Chart data for Issues by Client (Bar)
  const clientChartData = {
    labels: data?.issues_by_client?.map((item) => item.brand) || [],
    datasets: [
      {
        label: "Total Issues",
        data: data?.issues_by_client?.map((item) => item.total) || [],
        backgroundColor: CHART_COLORS.slice(0, data?.issues_by_client?.length || 1),
        borderColor: CHART_COLORS.slice(0, data?.issues_by_client?.length || 1),
        borderWidth: 0,
        borderRadius: 6,
      },
    ],
  };

  // Chart data for Issue Type Distribution (Pie)
  const issueTypePieData = {
    labels: data?.issue_types?.map((item) => item.issue_type) || [],
    datasets: [
      {
        data: data?.issue_types?.map((item) => item.count) || [],
        backgroundColor: CHART_COLORS,
        borderColor: "#1e2433",
        borderWidth: 2,
        hoverOffset: 8,
      },
    ],
  };

  // Chart data for Time Series (Line)
  const timeSeriesData = {
    labels: data?.time_series?.map((item) => item.date) || [],
    datasets: [
      {
        label: "Issues per Day",
        data: data?.time_series?.map((item) => item.count) || [],
        borderColor: "#3b82f6",
        backgroundColor: "rgba(59, 130, 246, 0.1)",
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 8,
        pointBackgroundColor: "#3b82f6",
        pointBorderColor: "#1e2433",
        pointBorderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: "#1e2433",
        titleColor: "#f0f4f8",
        bodyColor: "#a0aec0",
        borderColor: "rgba(255, 255, 255, 0.1)",
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        ticks: { 
          color: "#718096",
          font: { size: 11 }
        },
        grid: { 
          color: "rgba(255, 255, 255, 0.04)",
          drawBorder: false
        },
      },
      y: {
        ticks: { 
          color: "#718096",
          font: { size: 11 }
        },
        grid: { 
          color: "rgba(255, 255, 255, 0.04)",
          drawBorder: false
        },
        beginAtZero: true,
      },
    },
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "right",
        labels: {
          color: "#a0aec0",
          font: { size: 11 },
          padding: 16,
          usePointStyle: true,
          pointStyle: "circle",
        },
      },
      tooltip: {
        backgroundColor: "#1e2433",
        titleColor: "#f0f4f8",
        bodyColor: "#a0aec0",
        borderColor: "rgba(255, 255, 255, 0.1)",
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
      },
    },
  };

  const lineOptions = {
    ...chartOptions,
    plugins: {
      ...chartOptions.plugins,
      legend: {
        display: true,
        position: "top",
        align: "end",
        labels: {
          color: "#a0aec0",
          font: { size: 12 },
          usePointStyle: true,
          padding: 20,
        },
      },
    },
  };

  return (
    <div className="dashboard-layout">
      <Sidebar activePage="analytics" onNavigate={onNavigate} />

      <div className="dashboard-main">
        <div className="analytics-header">
          <h1 className="dashboard-title">Analytics Dashboard</h1>

          <div className="period-filter" data-testid="period-filter">
            {[
              { label: "All Time", value: "all" },
              { label: "1 Week", value: "1w" },
              { label: "1 Month", value: "1m" },
              { label: "3 Months", value: "3m" },
              { label: "6 Months", value: "6m" },
              { label: "1 Year", value: "1y" },
            ].map((p) => (
              <button
                key={p.value}
                className={`period-btn ${period === p.value ? "active" : ""}`}
                onClick={() => setPeriod(p.value)}
                data-testid={`period-${p.value}`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="loading-state" data-testid="loading-state">
            <TrendingUp size={24} style={{ marginRight: 12, opacity: 0.5 }} />
            Loading analytics...
          </div>
        ) : error ? (
          <div className="error-state" data-testid="error-state">{error}</div>
        ) : (
          <>
            {/* Summary Cards */}
            <div className="analytics-summary" data-testid="analytics-summary">
              <div className="summary-card" data-testid="total-issues-card">
                <div className="summary-icon">
                  <BarChart3 size={32} color="#3b82f6" />
                </div>
                <div className="summary-content">
                  <span className="summary-value">
                    {data?.summary?.total_issues || 0}
                  </span>
                  <span className="summary-label">Total Issues</span>
                </div>
              </div>

              <div className="summary-card" data-testid="total-clients-card">
                <div className="summary-icon">
                  <Users size={32} color="#06b6d4" />
                </div>
                <div className="summary-content">
                  <span className="summary-value">
                    {data?.summary?.total_clients || 0}
                  </span>
                  <span className="summary-label">Active Clients</span>
                </div>
              </div>

              <div className="summary-card" data-testid="top-issue-card">
                <div className="summary-icon">
                  <AlertTriangle size={32} color="#f59e0b" />
                </div>
                <div className="summary-content">
                  <span className="summary-value" style={{ fontSize: data?.summary?.top_issue_type?.issue_type?.length > 15 ? '18px' : '28px' }}>
                    {data?.summary?.top_issue_type?.issue_type || "N/A"}
                  </span>
                  <span className="summary-label">Top Issue Type</span>
                </div>
              </div>

              <div className="summary-card" data-testid="top-client-card">
                <div className="summary-icon">
                  <Crown size={32} color="#8b5cf6" />
                </div>
                <div className="summary-content">
                  <span className="summary-value" style={{ fontSize: data?.summary?.top_client?.brand?.length > 12 ? '18px' : '28px' }}>
                    {data?.summary?.top_client?.brand || "N/A"}
                  </span>
                  <span className="summary-label">Top Client</span>
                </div>
              </div>

              <div className="summary-card" data-testid="avg-tat-card">
                <div className="summary-icon">
                  <Clock size={32} color="#10b981" />
                </div>
                <div className="summary-content">
                  <span className="summary-value">
                    {data?.summary?.avg_tat_hours || 0}h
                  </span>
                  <span className="summary-label">Avg TAT</span>
                </div>
              </div>
            </div>

            {/* Charts Grid */}
            <div className="analytics-charts" data-testid="analytics-charts">
              {/* Issues by Client */}
              <div className="chart-card" data-testid="issues-by-client-chart">
                <h3 className="chart-title">Issues by Client</h3>
                <div className="chart-container">
                  {data?.issues_by_client?.length > 0 ? (
                    <Bar data={clientChartData} options={chartOptions} />
                  ) : (
                    <div className="no-data">No data available</div>
                  )}
                </div>
              </div>

              {/* Issue Type Distribution */}
              <div className="chart-card" data-testid="issue-types-chart">
                <h3 className="chart-title">Issue Type Distribution</h3>
                <div className="chart-container pie-chart">
                  {data?.issue_types?.length > 0 ? (
                    <Pie data={issueTypePieData} options={pieOptions} />
                  ) : (
                    <div className="no-data">No data available</div>
                  )}
                </div>
              </div>

              {/* Time Series */}
              <div
                className="chart-card full-width"
                data-testid="time-series-chart"
              >
                <h3 className="chart-title">Issue Frequency Over Time</h3>
                <div className="chart-container">
                  {data?.time_series?.length > 0 ? (
                    <Line data={timeSeriesData} options={lineOptions} />
                  ) : (
                    <div className="no-data">No data available</div>
                  )}
                </div>
              </div>
            </div>

            {/* Issue Types Table */}
            <div className="analytics-table" data-testid="issue-types-table">
              <h3 className="chart-title">Issue Types Breakdown</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Issue Type</th>
                    <th>Count</th>
                    <th>Percentage</th>
                  </tr>
                </thead>
                <tbody>
                  {data?.issue_types?.map((item, index) => (
                    <tr key={item.issue_type}>
                      <td>
                        <span
                          className="type-indicator"
                          style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}
                        />
                        {item.issue_type}
                      </td>
                      <td>{item.count}</td>
                      <td>
                        {data?.summary?.total_issues
                          ? (
                              (item.count / data.summary.total_issues) *
                              100
                            ).toFixed(1)
                          : 0}
                        %
                      </td>
                    </tr>
                  ))}
                  {(!data?.issue_types || data.issue_types.length === 0) && (
                    <tr>
                      <td colSpan="3" className="no-data-cell">
                        No issue data available
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default AnalyticsDashboard;
