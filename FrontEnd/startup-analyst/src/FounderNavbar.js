import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { useNavigate } from "react-router-dom";

const FounderNavbar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    sessionStorage.clear();
    navigate("/"); // redirect to login/signup
  };

  return (
    <nav
      className="navbar navbar-expand-lg shadow-sm"
      style={{
        backgroundColor: "white",
        borderBottom: "1px solid #eee",
      }}
    >
      <div className="container-fluid">
        {/* ✅ Logo */}
        <a className="navbar-brand d-flex align-items-center" href="/">
          <img
            src="https://d1y839zkxnw8vi.cloudfront.net/public/LVX_Final_logo/LV_Primary_RAW.svg"
            alt="LetsVenture Logo"
            style={{ height: "40px", width: "auto",paddingLeft:"30px" }}
          />
        </a>

        {/* ✅ Mobile Toggle */}
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* ✅ Nav Links */}
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto align-items-center">
            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/f-dashboard"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                🏠 <span className="ms-2">Dashboard</span>
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/founder-registration"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                📝 <span className="ms-2">Registration</span>
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/founder-startups"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                🚀 <span className="ms-2">My Startups</span>
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/founder-requests"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                📩 <span className="ms-2">Requests</span>
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/founder-meetings"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                📅 <span className="ms-2">Meetings</span>
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/founder-profile"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                👤 <span className="ms-2">My Profile</span>
              </a>
            </li>

            {/* ✅ Logout Button */}
            <li className="nav-item ms-lg-3">
              <button
                className="btn fw-semibold px-3 py-1 d-flex align-items-center"
                style={{
                  borderRadius: "20px",
                  backgroundColor: "rgb(18, 0, 94)",
                  color: "white",
                  border: "none",
                }}
                onClick={handleLogout}
              >
                🚪 <span className="ms-2">Logout</span>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </nav>
  );
};

export default FounderNavbar;
