// import React from "react";
// import StatusBadge from "./StatusBadge";

// function TicketCard({ ticket, isSelected, onClick }) {
//   return (
//     <div
//       className={`ticket-card ${isSelected ? "selected" : ""}`}
//       onClick={() => onClick(ticket)}
//     >
//       <div className="ticket-card-header">
//         <div>
//           <h4>{ticket.brand}</h4>
//           <p className="ticket-id">{ticket.id}</p>
//         </div>
//         <StatusBadge status={ticket.status} />
//       </div>

//       <p className="ticket-awb">AWB: {ticket.awb}</p>
//       <p className="ticket-summary">{ticket.summary}</p>
//     </div>
//   );
// }

// export default TicketCard;

import React from "react";
import StatusBadge from "./StatusBadge";

function TicketCard({ ticket, isSelected, onClick }) {
  // Display Jira issue key if available, otherwise show truncated ticket ID
  const displayId = ticket.jira_issue_key || `TICKET-${(ticket.id || "").substring(0, 8)}`;
  
  return (
    <div
      className={`ticket-card ${isSelected ? "selected" : ""}`}
      onClick={onClick}
      data-testid={`ticket-card-${ticket.id}`}
    >
      <div className="ticket-card-top">
        <h3>{ticket.brand}</h3>
        <StatusBadge status={ticket.status} />
      </div>

      <p className="ticket-id" data-testid="ticket-display-id">{displayId}</p>
      {ticket.issue_type && (
        <p className="ticket-issue-type" data-testid="ticket-issue-type">{ticket.issue_type}</p>
      )}
      <p className="ticket-awb">AWB: {ticket.awb || "N/A"}</p>
      <p className="ticket-summary">{ticket.summary}</p>
    </div>
  );
}

export default TicketCard;