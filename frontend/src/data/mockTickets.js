const mockTickets = [
  {
    id: "OPS-101",
    jiraUrl: "https://your-jira-instance.atlassian.net/browse/OPS-101",
    brand: "Nike",
    senderEmail: "support@nike.com",
    source: "Email",
    summary: "Shipment AWB123 delayed",
    fullMessage: "Hi team, shipment AWB123 has not moved for 2 days. Please check and update.",
    status: "Open",
    latestComment: "Ops team is checking with rider support.",
    assigned: true,
    assignee: "Rahul Sharma",
    createdAt: "2026-04-08 10:30 AM",
    awb: "AWB123"
  },
  {
    id: "OPS-102",
    jiraUrl: "https://your-jira-instance.atlassian.net/browse/OPS-102",
    brand: "Zara",
    senderEmail: "ops@zara.com",
    source: "Email",
    summary: "Shipment ID SHP7789 not delivered",
    fullMessage: "Customer shipment SHP7789 shows out for delivery but has not been delivered yet.",
    status: "In Progress",
    latestComment: "Delivery team contacted. Awaiting update.",
    assigned: true,
    assignee: "Aman Verma",
    createdAt: "2026-04-08 09:10 AM",
    awb: "SHP7789"
  },
  {
    id: "OPS-103",
    jiraUrl: "https://your-jira-instance.atlassian.net/browse/OPS-103",
    brand: "Myntra",
    senderEmail: "warehouse@myntra.com",
    source: "Slack",
    summary: "Tracking ID TRK567 issue from bug-reporting",
    fullMessage: "Slack report: Tracking ID TRK567 is showing invalid scan updates.",
    status: "Resolved",
    latestComment: "Issue resolved and customer updated.",
    assigned: false,
    assignee: null,
    createdAt: "2026-04-07 06:45 PM",
    awb: "TRK567"
  }
];

export default mockTickets;