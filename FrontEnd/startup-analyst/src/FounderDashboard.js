import React from "react";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";

export default function FounderDashboard() {
  const navigate = useNavigate();

  const handleNavigation = (path) => {
    navigate(path);
  };

  const handleLogout = () => {
    navigate("/"); // redirect to login/signup page
  };

  return (
    <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center bg-light">
      <div className="container text-center">
        <h1 className="mb-4 text-primary fw-bold">Founder Dashboard</h1>
        <p className="text-muted mb-5">
          Welcome back! Choose an option to continue.
        </p>

        <div className="row justify-content-center">
          {/* Startup Registration */}
          <div className="col-md-4 mb-3">
            <div className="card shadow-sm border-0 rounded-4">
              <div className="card-body">
                <h5 className="card-title mb-3">Startup Registration</h5>
                <p className="card-text text-muted">
                  Register your startup to get started with our AI evaluation system.
                </p>
                <button
                  className="btn btn-primary w-100"
                  onClick={() => handleNavigation("/startup-registration")}
                >
                  Go to Registration
                </button>
              </div>
            </div>
          </div>

          {/* View Registered Startups */}
          <div className="col-md-4 mb-3">
            <div className="card shadow-sm border-0 rounded-4">
              <div className="card-body">
                <h5 className="card-title mb-3">View My Startups</h5>
                <p className="card-text text-muted">
                  See your registered startups and their evaluation progress.
                </p>
                <button className="btn btn-outline-primary w-100" disabled>
                  Coming Soon
                </button>
              </div>
            </div>
          </div>

          {/* Profile Settings */}
          <div className="col-md-4 mb-3">
            <div className="card shadow-sm border-0 rounded-4">
              <div className="card-body">
                <h5 className="card-title mb-3">Profile Settings</h5>
                <p className="card-text text-muted">
                  Manage your founder profile and update contact information.
                </p>
                <button className="btn btn-outline-primary w-100" disabled>
                  Coming Soon
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-5">
          <button
            className="btn-danger px-4"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
