import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import { useNavigate } from "react-router-dom";

const InvestorNavbar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    sessionStorage.clear();
    navigate("/");
  };

  return (
    <nav
      className="navbar navbar-expand-lg shadow-sm"
      style={{
        backgroundColor: "white",
        borderBottom: "1px solid #e6e6e6",
      }}
    >
      <div className="container-fluid">
        {/* ✅ Logo */}
        <a className="navbar-brand d-flex align-items-center fw-bold" href="/">
          <img
            src="https://d1y839zkxnw8vi.cloudfront.net/public/LVX_Final_logo/LV_Primary_RAW.svg"
            alt="LetsVenture Logo"
            style={{ height: "40px", width: "auto", paddingLeft: "30px" }}
          />
        </a>

        {/* ✅ Mobile Toggle */}
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* ✅ Nav Items */}
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto align-items-center">
            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/investor-home"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                🏠 <span className="ms-2">Home</span>
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/investor-deals"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                🤝 <span className="ms-2">Deals</span>
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/interested-meetings"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                📅 <span className="ms-2">Interested & Meetings</span>
              </a>
            </li>

            <li className="nav-item">
              <a
                className="nav-link fw-semibold d-flex align-items-center"
                href="/profile"
                style={{ color: "rgb(18, 0, 94)" }}
              >
                👤 <span className="ms-2">My Profile</span>
              </a>
            </li>

            {/* ✅ Logout */}
            <li className="nav-item ms-lg-3">
              <button
                className="btn btn-light fw-semibold text-primary d-flex align-items-center"
                style={{ borderRadius: "20px", padding: "6px 14px" }}
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

export default InvestorNavbar;
