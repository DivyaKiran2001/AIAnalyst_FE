import React from "react";
import { useNavigate } from "react-router-dom";

const InvestorDashboard = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    navigate("/"); // redirect to login/signup page
  };

  return (
    <div className="container mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Investor Dashboard</h2>
        <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
      </div>

      <div className="card p-4 mb-3">
        <h4>Welcome, Investor!</h4>
        <p>Here you can review startups, check investment opportunities, and track your portfolio.</p>
      </div>

      <div className="row">
        <div className="col-md-6">
          <div className="card p-3 mb-3">
            <h5>Startup Pipeline</h5>
            <p>See startups seeking funding and their details.</p>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card p-3 mb-3">
            <h5>Investment Portfolio</h5>
            <p>Track your invested startups, performance, and returns.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvestorDashboard;
