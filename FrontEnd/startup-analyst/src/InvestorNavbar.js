import React from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from "react-router-dom";

const InvestorNavbar = () => {
    const navigate = useNavigate();
    const handleLogout = () => {
        sessionStorage.clear();
        navigate("/"); // redirect to login/signup
      };
  return (
    <nav className="navbar navbar-expand-lg navbar-dark" style={{ backgroundColor: "#007bff" }}>
      <div className="container-fluid">
        <a className="navbar-brand fw-bold" href="/">LetsVenture</a>
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
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav ms-auto align-items-center">
            <li className="nav-item">
              <a className="nav-link d-flex align-items-center" href="/investor-home">
                🏠 <span className="ms-2">Home</span>
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link d-flex align-items-center" href="/deals">
                🤝 <span className="ms-2">Deals</span>
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link d-flex align-items-center" href="/interested-meetings">
                📅 <span className="ms-2">Interested & Meetings</span>
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link d-flex align-items-center" href="/profile">
                👤 <span className="ms-2">My Profile</span>
              </a>
            </li>

            {/* ✅ Added Logout Option */}
            <li className="nav-item ms-lg-3">
              <button 
                className="btn btn-light text-primary fw-semibold px-3 py-1 d-flex align-items-center"
                style={{ borderRadius: "20px" }}
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
