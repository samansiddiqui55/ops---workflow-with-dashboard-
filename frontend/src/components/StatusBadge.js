// import React from "react";

// function StatusBadge({ status }) {
//   const normalized = status?.toLowerCase();

//   return (
//     <span className={`status-badge ${normalized}`}>
//       {status}
//     </span>
//   );
// }

// export default StatusBadge;

import React from "react";

function StatusBadge({ status }) {
  const normalized = (status || "").toLowerCase();

  return (
    <span className={`status-badge ${normalized.replace(/\s+/g, "-")}`}>
      {status || "unknown"}
    </span>
  );
}

export default StatusBadge;