// import React, { useMemo, useState } from "react";
// import Sidebar from "../components/Sidebar";
// import SearchBar from "../components/SearchBar";
// import TicketList from "../components/TicketList";
// import TicketDetail from "../components/TicketDetail";
// import mockTickets from "../data/mockTickets";

// function SupportDashboard() {
//   const [activeTab, setActiveTab] = useState("assigned");
//   const [searchTerm, setSearchTerm] = useState("");
//   const [selectedTicket, setSelectedTicket] = useState(null);
//   const [sortType, setSortType] = useState(null);
// const [filterStatus, setFilterStatus] = useState(null);

//  const filteredTickets = useMemo(() => {
//   let data = mockTickets
//     .filter((ticket) =>
//       activeTab === "assigned" ? ticket.assigned : !ticket.assigned
//     )
//     .filter((ticket) => {
//       const search = searchTerm.toLowerCase();
//       return (
//         ticket.brand.toLowerCase().includes(search) ||
//         ticket.awb.toLowerCase().includes(search) ||
//         ticket.id.toLowerCase().includes(search) ||
//         ticket.summary.toLowerCase().includes(search)
//       );
//     });

//   // FILTER
//   if (filterStatus) {
//     data = data.filter(
//       (ticket) => ticket.status.toLowerCase() === filterStatus
//     );
//   }

//   // SORT
//   if (sortType === "newest") {
//     data = [...data].sort(
//       (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
//     );
//   }

//   if (sortType === "oldest") {
//     data = [...data].sort(
//       (a, b) => new Date(a.createdAt) - new Date(b.createdAt)
//     );
//   }

//   return data;
// }, [activeTab, searchTerm, sortType, filterStatus]);

//   return (
//     <div className="dashboard-layout">
//       <Sidebar />

//       <div className="dashboard-main">
//         <h1 className="dashboard-title">Support Dashboard</h1>

//         <div className="dashboard-content">
//           <div className="ticket-panel">
//             <div className="tabs">
//               <button
//                 className={activeTab === "assigned" ? "tab active" : "tab"}
//                 onClick={() => setActiveTab("assigned")}
//               >
//                 Assigned
//               </button>
//               <button
//                 className={activeTab === "unassigned" ? "tab active" : "tab"}
//                 onClick={() => setActiveTab("unassigned")}
//               >
//                 Unassigned
//               </button>
//             </div>

//             <SearchBar searchTerm={searchTerm} setSearchTerm={setSearchTerm} />

//             <div className="filter-row">
//               <button
//   className="secondary-btn"
//   onClick={() =>
//     setSortType(sortType === "newest" ? "oldest" : "newest")
//   }
// >
//   Sort ({sortType || "none"})
// </button>

// <button
//   className="secondary-btn"
//   onClick={() =>
//     setFilterStatus(filterStatus === "open" ? null : "open")
//   }
// >
//   Filter ({filterStatus || "all"})
// </button>
//             </div>

//             <TicketList
//               tickets={filteredTickets}
//               selectedTicket={selectedTicket}
//               setSelectedTicket={setSelectedTicket}
//             />
//           </div>

//           <TicketDetail ticket={selectedTicket} />
//         </div>
//       </div>
//     </div>
//   );
// }

// export default SupportDashboard;

import React, { useEffect, useMemo, useState, useCallback } from "react";
import Sidebar from "../components/Sidebar";
import SearchBar from "../components/SearchBar";
import TicketList from "../components/TicketList";
import TicketDetail from "../components/TicketDetail";
import { fetchTickets, resolveTicket, createTicketWebSocket } from "../services/api";

function SupportDashboard({ onNavigate }) {
  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [activeTab, setActiveTab] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortType, setSortType] = useState("newest");
  const [filterStatus, setFilterStatus] = useState("all");
  const [loading, setLoading] = useState(true);

  const loadTickets = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchTickets();
      setTickets(data);

      if (data.length > 0) {
        setSelectedTicket((prev) => {
          const stillExists = data.find((t) => t.id === prev?.id);
          return stillExists || data[0];
        });
      } else {
        setSelectedTicket(null);
      }
    } catch (error) {
      console.error("Error loading tickets:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  // WebSocket for real-time updates
  useEffect(() => {
    const cleanup = createTicketWebSocket((message) => {
      if (message.type === "new_ticket" || message.type === "ticket_resolved") {
        // Reload tickets when we get a WebSocket update
        loadTickets();
      }
    });
    return cleanup;
  }, [loadTickets]);

  const filteredTickets = useMemo(() => {
    let data = [...tickets];

    // Tab filtering
    data = data.filter((ticket) => {
      if (activeTab === "all") return true;
      if (activeTab === "assigned") {
        return ticket.assigned_to && ticket.assigned_to !== "Unassigned";
      }
      if (activeTab === "unassigned") {
        return !ticket.assigned_to || ticket.assigned_to === "Unassigned";
      }
      return true;
    });

    // Search
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      data = data.filter((ticket) => {
        return (
          ticket.brand?.toLowerCase().includes(term) ||
          ticket.id?.toLowerCase().includes(term) ||
          ticket.awb?.toLowerCase().includes(term) ||
          ticket.summary?.toLowerCase().includes(term) ||
          ticket.sender_email?.toLowerCase().includes(term)
        );
      });
    }

    // Filter status
    if (filterStatus !== "all") {
      data = data.filter(
        (ticket) => ticket.status?.toLowerCase() === filterStatus
      );
    }

    // Sort
    data.sort((a, b) => {
      const dateA = new Date(a.created_at);
      const dateB = new Date(b.created_at);

      if (sortType === "newest") return dateB - dateA;
      if (sortType === "oldest") return dateA - dateB;
      return 0;
    });

    return data;
  }, [tickets, activeTab, searchTerm, sortType, filterStatus]);

  const handleResolve = async (ticket) => {
    try {
      await resolveTicket(ticket.id, {
        latest_comment: "Issue resolved and customer updated.",
        resolution_notes: "Resolved from OpsFlow dashboard.",
      });

      await loadTickets();
    } catch (error) {
      console.error("Error resolving ticket:", error);
      alert("Failed to resolve ticket");
    }
  };

  const handleSortToggle = () => {
    setSortType((prev) => (prev === "newest" ? "oldest" : "newest"));
  };

  const handleFilterToggle = () => {
    const order = ["all", "open", "in progress", "resolved"];
    const currentIndex = order.indexOf(filterStatus);
    const nextIndex = (currentIndex + 1) % order.length;
    setFilterStatus(order[nextIndex]);
  };

  return (
    <div className="dashboard-layout">
      <Sidebar activePage="support" onNavigate={onNavigate} />

      <div className="dashboard-main">
        <h1 className="dashboard-title">Support Dashboard</h1>

        <div className="dashboard-content">
          <div className="ticket-panel">
            <div className="tabs">
              <button
                className={activeTab === "all" ? "tab active" : "tab"}
                onClick={() => setActiveTab("all")}
                data-testid="tab-all"
              >
                All
              </button>

              <button
                className={activeTab === "assigned" ? "tab active" : "tab"}
                onClick={() => setActiveTab("assigned")}
                data-testid="tab-assigned"
              >
                Assigned
              </button>

              <button
                className={activeTab === "unassigned" ? "tab active" : "tab"}
                onClick={() => setActiveTab("unassigned")}
                data-testid="tab-unassigned"
              >
                Unassigned
              </button>
            </div>

            <SearchBar value={searchTerm} onChange={setSearchTerm} />

            <div className="ticket-actions">
              <button className="secondary-btn" onClick={handleSortToggle}>
                Sort ({sortType})
              </button>

              <button className="secondary-btn" onClick={handleFilterToggle}>
                Filter ({filterStatus})
              </button>
            </div>

            {loading ? (
              <div className="empty-state">Loading tickets...</div>
            ) : (
              <TicketList
                tickets={filteredTickets}
                selectedTicket={selectedTicket}
                onSelectTicket={setSelectedTicket}
              />
            )}
          </div>

          <div className="detail-panel">
            <TicketDetail
              ticket={selectedTicket}
              onResolve={handleResolve}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default SupportDashboard;