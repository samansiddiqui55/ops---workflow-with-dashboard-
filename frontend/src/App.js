import React, { useState } from "react";
import "./App.css";
import SupportDashboard from "./pages/SupportDashboard";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";

function App() {
  const [currentPage, setCurrentPage] = useState("support");

  const handleNavigate = (page) => {
    setCurrentPage(page);
  };

  return (
    <>
      {currentPage === "support" && (
        <SupportDashboard onNavigate={handleNavigate} />
      )}
      {currentPage === "analytics" && (
        <AnalyticsDashboard onNavigate={handleNavigate} />
      )}
    </>
  );
}

export default App;
