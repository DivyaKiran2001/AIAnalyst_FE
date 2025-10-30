// import React, { useEffect, useState } from "react";
// import {
//   PieChart,
//   Pie,
//   Cell,
//   ResponsiveContainer,
//   Legend,
//   Tooltip,
// } from "recharts";
// import { useLocation, useNavigate } from "react-router-dom";
// import InvestorNavbar from "./InvestorNavbar";
// import "./GenerateReport.css";

// const BACKEND_URL = "http://localhost:8000";

// const colors = {
//   primary: "#2E86AB",
//   secondary: "#A23B72",
//   accent: "#F18F01",
//   success: "#4CAF50",
//   warning: "#FFC107",
//   danger: "#F44336",
//   light: "#F8F9FA",
//   dark: "#343A40",
//   gray: "#6C757D",
// };

// // ✅ Circular Progress Component
// const CircularProgress = ({ value, maxValue, label, color, size = 140 }) => {
//   const percentage = (value / maxValue) * 100;
//   const strokeWidth = 10;
//   const radius = (size - strokeWidth) / 2;
//   const circumference = 2 * Math.PI * radius;
//   const strokeDashoffset = circumference - (percentage / 100) * circumference;
//   const center = size / 2;

//   return (
//     <div className="circular-container">
//       <div className="circular-wrapper" style={{ width: size, height: size }}>
//         <svg
//           className="circular-svg"
//           width={size}
//           height={size}
//           viewBox={`0 0 ${size} ${size}`}
//         >
//           <circle
//             cx={center}
//             cy={center}
//             r={radius}
//             fill="none"
//             stroke="#e0e0e0"
//             strokeWidth={strokeWidth}
//           />
//           <circle
//             cx={center}
//             cy={center}
//             r={radius}
//             fill="none"
//             stroke={color}
//             strokeWidth={strokeWidth}
//             strokeLinecap="round"
//             strokeDasharray={circumference}
//             strokeDashoffset={strokeDashoffset}
//             transform={`rotate(-90 ${center} ${center})`}
//           />
//         </svg>
//         <div className="circular-text">
//           <div className="circular-value" style={{ color, fontSize: size / 7 }}>
//             {value}
//             {maxValue === 100 ? "%" : "/10"}
//           </div>
//           <div className="circular-label" style={{ fontSize: size / 12 }}>
//             {label}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// const GenerateReport = () => {
//   const location = useLocation();
//   const navigate = useNavigate();
//   const { emailId, startupName } = location.state || {};

//   const [startupData, setStartupData] = useState(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   // ✅ Fetch startup data
//   useEffect(() => {
//     console.log(emailId, startupName);
//     const fetchStartupData = async () => {
//       if (!emailId || !startupName) {
//         setError("Missing startup information. Please go back.");
//         setLoading(false);
//         return;
//       }

//       try {
//         const res = await fetch(`${BACKEND_URL}/api/startups`);
//         if (!res.ok) throw new Error("Failed to fetch startups");

//         const data = await res.json();
//         console.log("📦 All Startups:", data);

//         const selectedStartup = data.find(
//           (s) => s.emailId === emailId && s.startupName === startupName
//         );

//         if (!selectedStartup)
//           throw new Error("Startup not found for the given details");

//         console.log("✅ Selected Startup:", selectedStartup);
//         setStartupData(selectedStartup);
//       } catch (err) {
//         console.error("Error fetching startup data:", err);
//         setError(err.message);
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchStartupData();
//   }, [emailId, startupName]);

//   if (loading) {
//     return (
//       <>
//         <InvestorNavbar />
//         <div className="text-center mt-5 text-muted">
//           Loading startup report...
//         </div>
//       </>
//     );
//   }

//   if (error) {
//     return (
//       <>
//         <InvestorNavbar />
//         <div className="container text-center mt-5">
//           <div className="alert alert-danger">{error}</div>
//           <button className="btn btn-primary mt-3" onClick={() => navigate(-1)}>
//             Go Back
//           </button>
//         </div>
//       </>
//     );
//   }

//   // ✅ Handle first_memo safely (string or object)
//   let memo = null;
//   try {
//     if (startupData.first_memo) {
//       const parsed =
//         typeof startupData.first_memo === "string"
//           ? JSON.parse(startupData.first_memo)
//           : startupData.first_memo;
//       memo = parsed?.investment_memo || null;
//     }
//   } catch (e) {
//     console.error("❌ Error parsing first_memo:", e);
//   }

//   console.log("🧾 Parsed Investment Memo:", memo);

//   if (!memo) {
//     return (
//       <>
//         <InvestorNavbar />
//         <div className="container mt-5 text-center">
//           <h4>No investment memo available for this startup.</h4>
//         </div>
//       </>
//     );
//   }

//   // ✅ Financial Pie Chart Data
//   const financialPieData = [
//     {
//       name: "Annual Revenue",
//       value: memo.financial_highlights?.key_metrics?.annual_revenue || 0,
//       color: colors.primary,
//     },
//     {
//       name: "Growth Rate",
//       value: memo.financial_highlights?.key_metrics?.growth_rate || 0,
//       color: colors.accent,
//     },
//     {
//       name: "Runway (months)",
//       value: memo.financial_highlights?.key_metrics?.runway_months || 0,
//       color: colors.secondary,
//     },
//   ];

//   const CustomTooltip = ({ active, payload }) => {
//     if (active && payload && payload.length) {
//       return (
//         <div className="tooltip-box">
//           <p>{`${payload[0].name}: ${payload[0].value}`}</p>
//         </div>
//       );
//     }
//     return null;
//   };

//   return (
//     <>
//       <InvestorNavbar />
//       <div className="report-container">
//         <div className="header">
//           <h1 className="title">{startupName} — Investment Report</h1>
//           <p className="subtitle">
//             Comprehensive Analysis of Investment Opportunity
//           </p>
//           <div>
//             <div
//               className={`rating-badge ${memo.executive_summary?.investment_rating}`}
//             >
//               {memo.executive_summary?.investment_rating}
//             </div>
//             <div className="confidence-score">
//               Confidence: {memo.executive_summary?.confidence_score}
//             </div>
//           </div>
//         </div>

//         {/* Executive Summary */}
//         <div className="section">
//           <h2 className="section-title">Executive Summary</h2>
//           <p>{memo.executive_summary?.company_brief}</p>
//           <div className="two-column">
//             <div>
//               <h3 className="highlight-title">Highlights</h3>
//               <ul>
//                 {memo.executive_summary?.top_3_highlights?.map((h, i) => (
//                   <li key={i} className="highlight-item">
//                     {h}
//                   </li>
//                 ))}
//               </ul>
//             </div>
//             <div>
//               <h3 className="risk-title">Risks</h3>
//               <ul>
//                 {memo.executive_summary?.top_3_risks?.map((r, i) => (
//                   <li key={i} className="risk-item">
//                     {r}
//                   </li>
//                 ))}
//               </ul>
//             </div>
//           </div>
//         </div>

//         {/* Financial Highlights */}
//         <div className="section">
//           <h2 className="section-title">Financial Highlights</h2>
//           <div className="enhanced-score">
//             <CircularProgress
//               value={memo.financial_highlights?.score || 8.5}
//               maxValue={10}
//               label="Financial Score"
//               color={colors.success}
//               size={140}
//             />
//             <div className="score-content">
//               <div className="verdict">
//                 {memo.financial_highlights?.verdict}
//               </div>
//               <p>{memo.financial_highlights?.main_strength}</p>
//             </div>
//           </div>

//           <div className="metric-grid">
//             {Object.entries(memo.financial_highlights?.key_metrics || {}).map(
//               ([label, val]) => (
//                 <div key={label} className="metric-card">
//                   <div className="metric-value">{val}</div>
//                   <div className="metric-label">{label.replace(/_/g, " ")}</div>
//                 </div>
//               )
//             )}
//           </div>

//           <div className="chart-container">
//             <ResponsiveContainer width="100%" height={300}>
//               <PieChart>
//                 <Pie
//                   data={financialPieData}
//                   dataKey="value"
//                   cx="50%"
//                   cy="50%"
//                   outerRadius={100}
//                 >
//                   {financialPieData.map((entry, index) => (
//                     <Cell key={`cell-${index}`} fill={entry.color} />
//                   ))}
//                 </Pie>
//                 <Tooltip content={<CustomTooltip />} />
//                 <Legend />
//               </PieChart>
//             </ResponsiveContainer>
//           </div>
//         </div>

//         {/* Team Assessment */}
//         <div className="section">
//           <h2 className="section-title">Team Assessment</h2>
//           <div className="enhanced-score">
//             <CircularProgress
//               value={memo.team_highlights?.score || 6.5}
//               maxValue={10}
//               label="Team Score"
//               color={colors.warning}
//               size={140}
//             />
//             <div className="score-content">
//               <p>{memo.team_highlights?.overall_assessment}</p>
//             </div>
//           </div>

//           <div className="two-column">
//             <div>
//               <h3 className="highlight-title">Strengths</h3>
//               <ul>
//                 {memo.team_highlights?.key_strengths?.map((s, i) => (
//                   <li key={i} className="highlight-item">
//                     {s}
//                   </li>
//                 ))}
//               </ul>
//             </div>
//             <div>
//               <h3 className="risk-title">Critical Gaps</h3>
//               <ul>
//                 {memo.team_highlights?.critical_gaps?.map((g, i) => (
//                   <li key={i} className="risk-item">
//                     {g}
//                   </li>
//                 ))}
//               </ul>
//             </div>
//           </div>
//         </div>

//         {/* Market Analysis */}
//         <div className="section">
//           <h2 className="section-title">Market Analysis</h2>
//           <div className="enhanced-score">
//             <CircularProgress
//               value={memo.market_highlights?.validation_confidence || 70}
//               maxValue={100}
//               label="Validation Confidence"
//               color={colors.danger}
//               size={140}
//             />
//             <div className="score-content">
//               <p>
//                 <strong>Market Size:</strong>{" "}
//                 {memo.market_highlights?.market_size}
//               </p>
//               <p>
//                 <strong>Growth Potential:</strong>{" "}
//                 {memo.market_highlights?.growth_potential}
//               </p>
//               <p>
//                 <strong>Competitive Landscape:</strong>{" "}
//                 {memo.market_highlights?.competitive_landscape}
//               </p>
//             </div>
//           </div>
//           <p>
//             <strong>Main Opportunity:</strong>{" "}
//             {memo.market_highlights?.main_opportunity}
//           </p>
//         </div>

//         {/* Investment Recommendation */}
//         <div className="section">
//           <h2 className="section-title">Investment Recommendation</h2>
//           <div
//             className={`recommendation-card ${memo.investment_recommendation?.decision}`}
//           >
//             <h3>Decision: {memo.investment_recommendation?.decision}</h3>
//             <p>{memo.investment_recommendation?.reason}</p>
//           </div>

//           <h3>Next Steps</h3>
//           <ul className="next-steps-list">
//             {memo.investment_recommendation?.next_steps?.map((step, i) => (
//               <li key={i}>{step}</li>
//             ))}
//           </ul>
//         </div>
//       </div>
//     </>
//   );
// };

// export default GenerateReport;

import React, { useEffect, useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { useLocation, useNavigate } from "react-router-dom";
import InvestorNavbar from "./InvestorNavbar";
import "./GenerateReport.css";

const BACKEND_URL = "http://localhost:8000";

const colors = {
  primary: "#2E86AB",
  secondary: "#A23B72",
  accent: "#F18F01",
  success: "#4CAF50",
  warning: "#FFC107",
  danger: "#F44336",
  light: "#F8F9FA",
  dark: "#343A40",
  gray: "#6C757D",
};

// ✅ Circular Progress Component
const CircularProgress = ({ value, maxValue, label, color, size = 140 }) => {
  const percentage = (value / maxValue) * 100;
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;
  const center = size / 2;

  return (
    <div className="circular-container">
      <div className="circular-wrapper" style={{ width: size, height: size }}>
        <svg
          className="circular-svg"
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
        >
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#e0e0e0"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform={`rotate(-90 ${center} ${center})`}
          />
        </svg>
        <div className="circular-text">
          <div className="circular-value" style={{ color, fontSize: size / 7 }}>
            {value}
          </div>
          <div className="circular-label" style={{ fontSize: size / 12 }}>
            {label}
          </div>
        </div>
      </div>
    </div>
  );
};

const GenerateReport = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { emailId, startupName } = location.state || {};

  const [startupData, setStartupData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ✅ Fetch startup data
  useEffect(() => {
    console.log(emailId, startupName);
    const fetchStartupData = async () => {
      if (!emailId || !startupName) {
        setError("Missing startup information. Please go back.");
        setLoading(false);
        return;
      }

      try {
        const res = await fetch(`${BACKEND_URL}/api/startups`);
        if (!res.ok) throw new Error("Failed to fetch startups");

        const data = await res.json();
        console.log("📦 All Startups:", data);

        const selectedStartup = data.find(
          (s) => s.emailId === emailId && s.startupName === startupName
        );

        if (!selectedStartup)
          throw new Error("Startup not found for the given details");

        console.log("✅ Selected Startup:", selectedStartup);
        setStartupData(selectedStartup);
      } catch (err) {
        console.error("Error fetching startup data:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStartupData();
  }, [emailId, startupName]);

  if (loading) {
    return (
      <>
        <InvestorNavbar />
        <div className="text-center mt-5 text-muted">
          Loading startup report...
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <InvestorNavbar />
        <div className="container text-center mt-5">
          <div className="alert alert-danger">{error}</div>
          <button className="btn btn-primary mt-3" onClick={() => navigate(-1)}>
            Go Back
          </button>
        </div>
      </>
    );
  }

  // ✅ Parse memo safely (check multiple possible locations)
  let memo = null;
  try {
    let rawMemo =
      startupData.first_memo || startupData.bigqueryData?.first_memo;

    if (rawMemo) {
      const parsed =
        typeof rawMemo === "string" ? JSON.parse(rawMemo) : rawMemo;
      memo = parsed?.investment_memo || null;
    }
  } catch (e) {
    console.error("❌ Error parsing investment memo:", e);
  }

  console.log("🧾 Parsed Investment Memo:", memo);

  if (!memo) {
    return (
      <>
        <InvestorNavbar />
        <div className="container mt-5 text-center">
          <h4>No investment memo available for this startup.</h4>
        </div>
      </>
    );
  }

  // ✅ Financial Pie Chart Data
  //   const financialPieData = [
  //     {
  //       name: "Annual Revenue",
  //       value: memo.financial_highlights?.key_metrics?.annual_revenue || 0,
  //       color: colors.primary,
  //     },
  //     {
  //       name: "Growth Rate",
  //       value: memo.financial_highlights?.key_metrics?.growth_rate || 0,
  //       color: colors.accent,
  //     },
  //     {
  //       name: "Runway (months)",
  //       value: memo.financial_highlights?.key_metrics?.runway_months || 0,
  //       color: colors.secondary,
  //     },
  //   ];

  // ✅ Parse financial data safely from bigqueryData
  let parsedFinancialData = null;
  try {
    const rawFinancial = startupData.bigqueryData?.financial_data;
    if (rawFinancial) {
      parsedFinancialData =
        typeof rawFinancial === "string"
          ? JSON.parse(rawFinancial)
          : rawFinancial;
    }
  } catch (e) {
    console.error("❌ Error parsing financial_data:", e);
  }

  console.log("💰 Parsed Financial Data:", parsedFinancialData);

  const parseNumber = (val) => {
    if (!val) return 0;
    const num = parseFloat(val.toString().replace(/[^\d.-]/g, ""));
    return isNaN(num) ? 0 : num;
  };

  // Convert all different metrics to a comparable 0–100 scale
  const normalizeMetrics = (metrics) => {
    const revenue = parseNumber(metrics.monthly_revenue); // $
    const growth = parseNumber(metrics.growth_rate); // %
    const runway = parseNumber(metrics.runway); // months
    const ltvCac = parseNumber(metrics.ltv_cac_ratio); // ratio

    // Simple normalization assumptions
    const normalizedRevenue = Math.min((revenue / 100000) * 100, 100); // Cap at 100k
    const normalizedRunway = Math.min((runway / 24) * 100, 100); // Cap at 24 months
    const normalizedLtvCac = Math.min(ltvCac * 5, 100); // Weighted ratio
    const normalizedGrowth = Math.min(growth, 100); // already %

    return [
      {
        name: "Revenue Strength",
        value: normalizedRevenue,
        color: colors.primary,
      },
      { name: "Growth Rate", value: normalizedGrowth, color: colors.accent },
      {
        name: "Runway Duration",
        value: normalizedRunway,
        color: colors.secondary,
      },
      { name: "LTV:CAC Ratio", value: normalizedLtvCac, color: "#6a549fff" },
    ];
  };

  const financialPieData = normalizeMetrics(
    memo.financial_highlights?.key_metrics || {}
  );

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const { name, value } = payload[0];
      return (
        <div className="tooltip-box">
          <p>
            <strong>{name}</strong>
          </p>
          <p>Score: {value.toFixed(1)} / 100</p>
        </div>
      );
    }
    return null;
  };

  return (
    <>
      <InvestorNavbar />
      <div className="report-container">
        <div className="header">
          <h1 className="title">{startupName} — Investment Report</h1>
          <p className="subtitle">
            Comprehensive Analysis of Investment Opportunity
          </p>
          <div>
            <div
              className={`rating-badge ${memo.executive_summary?.investment_rating}`}
            >
              {memo.executive_summary?.investment_rating}
            </div>
            <div className="confidence-score">
              Confidence: {memo.executive_summary?.confidence_score}
            </div>
          </div>
        </div>

        {/* Executive Summary */}
        <div className="section">
          <h2 className="section-title">Executive Summary</h2>
          <p>{memo.executive_summary?.company_brief}</p>
          <div className="two-column">
            <div>
              <h3 className="highlight-title">Highlights</h3>
              <ul>
                {memo.executive_summary?.top_3_highlights?.map((h, i) => (
                  <li key={i} className="highlight-item">
                    {h}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="risk-title">Risks</h3>
              <ul>
                {memo.executive_summary?.top_3_risks?.map((r, i) => (
                  <li key={i} className="risk-item">
                    {r}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Financial Highlights */}
        <div className="section">
          <h2 className="section-title">Financial Highlights</h2>
          <div className="enhanced-score">
            <CircularProgress
              value={memo.financial_highlights?.score || 8.5}
              maxValue={10}
              label="Financial Score"
              color={colors.success}
              size={140}
            />
            <div className="score-content">
              <div className="verdict">
                {memo.financial_highlights?.verdict}
              </div>
              <p>{memo.financial_highlights?.main_strength}</p>
            </div>
          </div>

          <div className="metric-grid">
            {Object.entries(memo.financial_highlights?.key_metrics || {}).map(
              ([label, val]) => (
                <div key={label} className="metric-card">
                  <div className="metric-value">{val}</div>
                  <div className="metric-label">{label.replace(/_/g, " ")}</div>
                </div>
              )
            )}
          </div>

          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={financialPieData}
                  dataKey="value"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                >
                  {financialPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Team Assessment */}
        <div className="section">
          <h2 className="section-title">Team Assessment</h2>
          <div className="enhanced-score">
            <CircularProgress
              value={memo.team_highlights?.score || 6.5}
              maxValue={10}
              label="Team Score"
              color={colors.warning}
              size={140}
            />
            <div className="score-content">
              <p>{memo.team_highlights?.overall_assessment}</p>
            </div>
          </div>

          <div className="two-column">
            <div>
              <h3 className="highlight-title">Strengths</h3>
              <ul>
                {memo.team_highlights?.key_strengths?.map((s, i) => (
                  <li key={i} className="highlight-item">
                    {s}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="risk-title">Critical Gaps</h3>
              <ul>
                {memo.team_highlights?.critical_gaps?.map((g, i) => (
                  <li key={i} className="risk-item">
                    {g}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Market Analysis */}
        <div className="section">
          <h2 className="section-title">Market Analysis</h2>
          <div className="enhanced-score">
            <CircularProgress
              value={memo.market_highlights?.validation_confidence || 70}
              maxValue={100}
              label="Validation Confidence"
              color={colors.danger}
              size={140}
            />
            <div className="score-content">
              <p>
                <strong>Market Size:</strong>{" "}
                {memo.market_highlights?.market_size}
              </p>
              <p>
                <strong>Growth Potential:</strong>{" "}
                {memo.market_highlights?.growth_potential}
              </p>
              <p>
                <strong>Competitive Landscape:</strong>{" "}
                {memo.market_highlights?.competitive_landscape}
              </p>
            </div>
          </div>
          <p>
            <strong>Main Opportunity:</strong>{" "}
            {memo.market_highlights?.main_opportunity}
          </p>
        </div>

        {/* Investment Recommendation */}
        <div className="section">
          <h2 className="section-title">Investment Recommendation</h2>
          <div
            className={`recommendation-card ${memo.investment_recommendation?.decision}`}
          >
            <h3>Decision: {memo.investment_recommendation?.decision}</h3>
            <p>{memo.investment_recommendation?.reason}</p>
          </div>

          <h3>Next Steps</h3>
          <ul className="next-steps-list">
            {memo.investment_recommendation?.next_steps?.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ul>
        </div>
      </div>
    </>
  );
};

export default GenerateReport;
