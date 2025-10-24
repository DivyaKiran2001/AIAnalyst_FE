import React from "react";
import { useNavigate } from "react-router-dom";
import "bootstrap/dist/css/bootstrap.min.css";
import FounderNavbar from "./FounderNavbar";

const FounderRegistration = () => {
  const navigate = useNavigate();

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <>
      <FounderNavbar />

      <div
        className="d-flex justify-content-center align-items-center"
        style={{
          backgroundColor: "#f2f2f2",
          minHeight: "100vh",
          padding: "30px 0",
        }}
      >
        <div
          className="card shadow-lg border-0 rounded-4 p-4"
          style={{
            width: "75%",
            maxWidth: "800px",
            backgroundColor: "white",
            color: "rgb(18, 0, 94)",
          }}
        >
          <div className="card-body">
            <h2 className="fw-bold mb-3 text-center">Startup Registration</h2>

            <div className="mb-3">
              <p className="fs-5 fw-semibold text-center mb-2">
                You've chosen to build something bold — we're here to back you.
              </p>
              <p className="text-center mb-3">
                <strong>Smart Capital. Connections. Growth.</strong>
                <br />
                Build with India’s trusted founder network.
              </p>

              <div>
                <h5 className="fw-bold mb-2">Here’s what you should know:</h5>
                <ul className="mb-3" style={{ lineHeight: "1.6" }}>
                  <li>
                    <strong>LVX</strong> is sector-agnostic — we back bold
                    founders across stages.
                  </li>
                  <li>
                    Raise early-stage capital through our SEBI-registered Angel
                    Fund (AIF). All angels come in as a single entity on your cap
                    table.
                  </li>
                  <li>
                    Tap into our network of HNIs, angels, and
                    founder-investors. Typical cheque sizes: $100K–$1M.
                  </li>
                  <li>
                    Access founder-mentors, business connects, and our{" "}
                    <strong>LVX Startup Kit</strong> to scale faster.
                  </li>
                  <li>
                    For growth-stage founders: Raise Series A to Pre-IPO capital
                    with strategic investors.
                  </li>
                </ul>
              </div>

              <p className="text-center mb-4">
                Getting started takes just{" "}
                <strong>2–3 minutes.</strong> Fill out your profile to unlock
                capital, connects, and community.
              </p>
            </div>

            <div className="text-center">
              <button
                className="btn fw-semibold px-4 py-2"
                style={{
                  backgroundColor: "rgb(18, 0, 94)",
                  color: "white",
                  borderRadius: "25px",
                }}
                onClick={() => handleNavigation("/startup-registration")}
              >
                🚀 Begin Registration
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default FounderRegistration;
