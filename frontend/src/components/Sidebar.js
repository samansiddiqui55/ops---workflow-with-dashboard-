import React from "react";
import { Ticket, BarChart3 } from "lucide-react";
import logo from "../assets/logo.png";

function Sidebar({ activePage = "support", onNavigate }) {
  return (
    <div className="sidebar">
      <div className="sidebar-top">
        <img src={logo} alt="OpsFlow Logo" className="logo-img" />
      </div>

      <div className="sidebar-menu">
        <div
          className={`sidebar-item ${activePage === "support" ? "active" : ""}`}
          onClick={() => onNavigate && onNavigate("support")}
          data-testid="nav-support"
        >
          <Ticket className="sidebar-icon" size={22} />
          <span>Support</span>
        </div>

        <div
          className={`sidebar-item ${activePage === "analytics" ? "active" : ""}`}
          onClick={() => onNavigate && onNavigate("analytics")}
          data-testid="nav-analytics"
        >
          <BarChart3 className="sidebar-icon" size={22} />
          <span>Analytics</span>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
