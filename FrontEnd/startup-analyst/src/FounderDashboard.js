import React from "react";
import { useNavigate } from "react-router-dom";

const FounderDashboard = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    navigate("/"); // redirect to login/signup page
  };

  return (
    <div className="container mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Founder Dashboard</h2>
        <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
      </div>

      <div className="card p-4 mb-3">
        <h4>Welcome, Founder!</h4>
        <p>Here you can manage your startup, view analytics, and track progress.</p>
      </div>

      <div className="row">
        <div className="col-md-6">
          <div className="card p-3 mb-3">
            <h5>My Startups</h5>
            <p>List of your startups, traction, and performance metrics.</p>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card p-3 mb-3">
            <h5>Funding Requests</h5>
            <p>Track investor requests, funding status, and feedback.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FounderDashboard;
