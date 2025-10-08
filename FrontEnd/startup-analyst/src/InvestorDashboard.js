// import React from "react";
// import { useNavigate } from "react-router-dom";

// const InvestorDashboard = () => {
//   const navigate = useNavigate();

//   const handleLogout = () => {
//     navigate("/"); // redirect to login/signup page
//   };

//   return (
//     <div className="container mt-5">
//       <div className="d-flex justify-content-between align-items-center mb-4">
//         <h2>Investor Dashboard</h2>
//         <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
//       </div>

//       <div className="card p-4 mb-3">
//         <h4>Welcome, Investor!</h4>
//         <p>Here you can review startups, check investment opportunities, and track your portfolio.</p>
//       </div>

//       <div className="row">
//         <div className="col-md-6">
//           <div className="card p-3 mb-3">
//             <h5>Startup Pipeline</h5>
//             <p>See startups seeking funding and their details.</p>
//           </div>
//         </div>
//         <div className="col-md-6">
//           <div className="card p-3 mb-3">
//             <h5>Investment Portfolio</h5>
//             <p>Track your invested startups, performance, and returns.</p>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default InvestorDashboard;


import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const InvestorDashboard = () => {
  const navigate = useNavigate();
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleLogout = () => {
    localStorage.clear();
    navigate("/"); // redirect to login/signup
  };

  // Fetch startups on mount
  useEffect(() => {
    const fetchStartups = async () => {
      try {
        const res = await fetch("https://8000-genaihackat-aianalystfe-hgc0ltv9os0.ws-us121.gitpod.io/api/startups");
        const data = await res.json();
        setStartups(data);
      } catch (err) {
        console.error("Error fetching startups:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStartups();
  }, []);

  return (
    <div className="container mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Investor Dashboard</h2>
        <button className="btn btn-danger" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <div className="card p-4 mb-3 bg-light">
        <h4>Welcome, Investor!</h4>
        <p>
          Here you can review startups, check their details, and discover investment opportunities.
        </p>
      </div>

      <h4 className="mt-4 mb-3">Startup Opportunities</h4>

      {loading ? (
        <p>Loading startups...</p>
      ) : startups.length === 0 ? (
        <p>No startups found.</p>
      ) : (
        <div className="row">
          {startups.map((startup) => (
            <div key={startup._id} className="col-md-6 mb-4">
              <div className="card shadow-sm p-3 h-100">
                <h5 className="text-primary">{startup.startupName}</h5>
                <p><strong>Registered Name:</strong> {startup.registeredName}</p>
                <p><strong>Incorporation:</strong> {startup.incorporationMonth} {startup.incorporationYear}</p>
                <p><strong>About:</strong> {startup.about}</p>

            
              
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InvestorDashboard;
