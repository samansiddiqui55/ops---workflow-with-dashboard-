// import React from "react";
// import StatusBadge from "./StatusBadge";

// function TicketDetail({ ticket }) {
//   if (!ticket) {
//     return (
//       <div className="ticket-detail empty-detail">
//         <p>Select a Ticket to View Details</p>
//       </div>
//     );
//   }

//   return (
//     <div className="ticket-detail">
//       <div className="detail-header">
//         <div>
//           <h2>{ticket.id}</h2>
//           <p>{ticket.summary}</p>
//         </div>
//         <StatusBadge status={ticket.status} />
//       </div>

//       <div className="detail-grid">
//         <div><strong>Brand:</strong> {ticket.brand}</div>
//         <div><strong>Sender Email:</strong> {ticket.senderEmail}</div>
//         <div><strong>Source:</strong> {ticket.source}</div>
//         <div><strong>AWB / Tracking ID:</strong> {ticket.awb}</div>
//         <div><strong>Assigned To:</strong> {ticket.assignee || "Unassigned"}</div>
//         <div><strong>Created At:</strong> {ticket.createdAt}</div>
//       </div>

//       <div className="detail-section">
//         <h3>Full Message</h3>
//         <p>{ticket.fullMessage}</p>
//       </div>

//       <div className="detail-section">
//         <h3>Latest Jira Comment</h3>
//         <p>{ticket.latestComment}</p>
//       </div>

//       <div className="detail-actions">
//         <a
//           href={ticket.jiraUrl}
//           target="_blank"
//           rel="noopener noreferrer"
//           className="jira-button"
//         >
//           Open in Jira
//         </a>
//       </div>
//     </div>
//   );
// }

// export default TicketDetail;

import React from "react";
import StatusBadge from "./StatusBadge";

function TicketDetail({ ticket, onResolve }) {
  if (!ticket) {
    return (
      <div className="ticket-detail empty-detail" data-testid="empty-ticket-detail">
        <p>Select a Ticket to View Details</p>
      </div>
    );
  }

  // Display Jira issue key if available, otherwise show truncated ticket ID
  const displayId = ticket.jira_issue_key || `TICKET-${(ticket.id || "").substring(0, 8)}`;
  
  // Build proper Jira URL: https://grow-simplee.atlassian.net/browse/{ISSUE_KEY}
  const jiraBaseUrl = "https://grow-simplee.atlassian.net";
  const jiraUrl = ticket.jira_issue_key 
    ? `${jiraBaseUrl}/browse/${ticket.jira_issue_key}`
    : ticket.jira_url || "#";

  return (
    <div className="ticket-detail" data-testid="ticket-detail">
      <div className="detail-header">
        <div>
          <h2 data-testid="ticket-detail-id">{displayId}</h2>
          <p className="detail-subtitle">{ticket.summary}</p>
        </div>
        <StatusBadge status={ticket.status} />
      </div>

      <div className="detail-grid">
        <p><strong>Brand:</strong> {ticket.brand}</p>
        <p><strong>Sender Email:</strong> {ticket.sender_email}</p>
        <p><strong>Source:</strong> {ticket.source}</p>
        <p><strong>Issue Type:</strong> {ticket.issue_type || "Other"}</p>
        <p><strong>AWB / Tracking ID:</strong> {ticket.awb || "N/A"}</p>
        <p><strong>Assigned To:</strong> {ticket.assigned_to || "Unassigned"}</p>
        <p><strong>Created At:</strong> {ticket.created_at ? new Date(ticket.created_at).toLocaleString() : "N/A"}</p>
      </div>

      <div className="detail-section">
        <h3>Full Message</h3>
        <p className="message-content">{ticket.full_message}</p>
      </div>

      <div className="detail-section">
        <h3>Latest Jira Comment</h3>
        <p>{ticket.latest_comment || "No comments yet."}</p>
      </div>

      <div className="detail-actions">
        {ticket.jira_issue_key && (
          <a
            href={jiraUrl}
            target="_blank"
            rel="noreferrer"
            className="jira-btn"
            data-testid="open-jira-btn"
          >
            Open in Jira ({ticket.jira_issue_key})
          </a>
        )}

        {ticket.status !== "resolved" && (
          <button 
            className="resolve-btn" 
            onClick={() => onResolve(ticket)}
            data-testid="resolve-ticket-btn"
          >
            Resolve Ticket
          </button>
        )}
      </div>
    </div>
  );
}

export default TicketDetail;