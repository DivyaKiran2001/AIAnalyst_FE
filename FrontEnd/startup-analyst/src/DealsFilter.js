import React from "react";

const DealsFilter = ({
  selectedSector,
  setSelectedSector,
  selectedWeightage,
  setSelectedWeightage,
}) => {
  const sectors = [
    "Technology",
    "Healthcare",
    "Energy",
    "Industrials",
    "Consumer Staples",
    "Consumer Discretionary",
    "Financials",
    "Utilities",
    "Communication Services",
    "Real Estate",
    "Materials",
  ];

  const weightages = [
    { label: "Financials", value: "financials" },
    { label: "Team", value: "team" },
    { label: "Market", value: "market" },
  ];

  return (
    <div
      className="card shadow-sm border-0 rounded-4 p-4 mb-4"
      style={{ backgroundColor: "white" }}
    >
      <div className="row">
        {/* Sector Filter */}
        <div className="col-md-6 mb-3">
          <label
            className="form-label fw-bold"
            style={{ color: "rgb(18,0,94)" }}
          >
            Sector
          </label>
          <select
            className="form-select"
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            style={{
              borderColor: "rgb(18,0,94)",
              color: "rgb(18,0,94)",
            }}
          >
            <option value="">All Sectors</option>
            {sectors.map((sector) => (
              <option key={sector} value={sector}>
                {sector}
              </option>
            ))}
          </select>
        </div>

        {/* Weightage Filter */}
        <div className="col-md-6 mb-3">
          <label
            className="form-label fw-bold"
            style={{ color: "rgb(18,0,94)" }}
          >
            Weightages
          </label>
          <select
            className="form-select"
            value={selectedWeightage}
            onChange={(e) => setSelectedWeightage(e.target.value)}
            style={{
              borderColor: "rgb(18,0,94)",
              color: "rgb(18,0,94)",
            }}
          >
            <option value="">No Sorting</option>
            {weightages.map((weightage) => (
              <option key={weightage.value} value={weightage.value}>
                {weightage.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default DealsFilter;
