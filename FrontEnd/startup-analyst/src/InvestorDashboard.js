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
        const res = await fetch("https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/startups");
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
<p><strong>Founder:</strong> {startup.emailId}</p>
                <button className="btn btn-outline-success mt-2" onClick={() => handleChat(startup.emailId)}>Chat with Founder</button>
            
              
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InvestorDashboard;
