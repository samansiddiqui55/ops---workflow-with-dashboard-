// import React from "react";
// import TicketCard from "./TicketCard";

// function TicketList({ tickets, selectedTicket, setSelectedTicket }) {
//   if (!tickets.length) {
//     return <p className="empty-text">No tickets found</p>;
//   }

//   return (
//     <div className="ticket-list">
//       {tickets.map((ticket) => (
//         <TicketCard
//           key={ticket.id}
//           ticket={ticket}
//           isSelected={selectedTicket?.id === ticket.id}
//           onClick={setSelectedTicket}
//         />
//       ))}
//     </div>
//   );
// }

// export default TicketList;

import React from "react";
import TicketCard from "./TicketCard";

function TicketList({ tickets, selectedTicket, onSelectTicket }) {
  if (!tickets || tickets.length === 0) {
    return <div className="empty-state">No tickets found</div>;
  }

  return (
    <div className="ticket-list">
      {tickets.map((ticket) => (
        <TicketCard
          key={ticket.id}
          ticket={ticket}
          isSelected={selectedTicket?.id === ticket.id}
          onClick={() => onSelectTicket(ticket)}
        />
      ))}
    </div>
  );
}

export default TicketList;