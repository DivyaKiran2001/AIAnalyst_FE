import React from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import InvestorNavbar from "./InvestorNavbar";

const InvestorHome = () => {
  return (
    <>
      <InvestorNavbar />

      <div className="container mt-4">
        <h2 className="fw-bold text-primary mb-4">Welcome back, Investor 👋</h2>

        {/* Overview Cards */}
        <div className="row g-4 mb-4">
          <div className="col-md-3">
            <div className="card text-center shadow-sm border-0">
              <div className="card-body">
                <h5 className="card-title text-primary">Active Deals</h5>
                <p className="display-6 fw-bold">12</p>
                <p className="text-muted">Startups currently in your portfolio</p>
              </div>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card text-center shadow-sm border-0">
              <div className="card-body">
                <h5 className="card-title text-primary">Upcoming Meetings</h5>
                <p className="display-6 fw-bold">4</p>
                <p className="text-muted">Scheduled with founders</p>
              </div>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card text-center shadow-sm border-0">
              <div className="card-body">
                <h5 className="card-title text-primary">Interested Startups</h5>
                <p className="display-6 fw-bold">8</p>
                <p className="text-muted">Marked as interested</p>
              </div>
            </div>
          </div>

          <div className="col-md-3">
            <div className="card text-center shadow-sm border-0">
              <div className="card-body">
                <h5 className="card-title text-primary">Total Invested</h5>
                <p className="display-6 fw-bold">$2.5M</p>
                <p className="text-muted">Across all active deals</p>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card shadow-sm border-0">
          <div className="card-body">
            <h5 className="card-title text-primary mb-3">Recent Activity</h5>
            <ul className="list-group list-group-flush">
              <li className="list-group-item">
                ✅ You confirmed interest in <strong>NeuroTech AI</strong>
              </li>
              <li className="list-group-item">
                📅 Meeting scheduled with <strong>EcoPower Labs</strong> on Oct 28
              </li>
              <li className="list-group-item">
                💼 Deal updated: <strong>HealthChain</strong> reached Seed Round
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="text-center text-muted py-3 mt-4 border-top">
        © 2025 LetsVenture Investor Platform
      </footer>
    </>
  );
};

export default InvestorHome;
