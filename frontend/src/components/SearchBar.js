// import React from "react";

// function SearchBar({ searchTerm, setSearchTerm }) {
//   return (
//     <input
//       type="text"
//       placeholder="Search rider, AWB, ID..."
//       value={searchTerm}
//       onChange={(e) => setSearchTerm(e.target.value)}
//       className="search-input"
//     />
//   );
// }

// export default SearchBar;

import React from "react";

function SearchBar({ value, onChange }) {
  return (
    <input
      type="text"
      className="search-input"
      placeholder="Search rider, AWB, ID..."
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

export default SearchBar;