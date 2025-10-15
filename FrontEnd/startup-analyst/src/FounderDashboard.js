


import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import io from "socket.io-client";
import "bootstrap/dist/css/bootstrap.min.css";

const BACKEND_URL = "https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io";
const socket = io(BACKEND_URL);

export default function FounderDashboard() {
  const navigate = useNavigate();
  const [startups, setStartups] = useState([]);
  const [investorRequests, setInvestorRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [meetings, setMeetings] = useState([]);
  const [calendarConnected, setCalendarConnected] = useState(false);

  const founderEmail = sessionStorage.getItem("emailId");

  const handleNavigation = (path) => {
    navigate(path);
  };

  const handleLogout = () => {
    sessionStorage.clear();
    navigate("/");
  };

  // ✅ Fetch founder’s startups
  useEffect(() => {
    const fetchStartups = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/startups`);
        const data = await res.json();
        const myStartups = data.filter((s) => s.emailId === founderEmail);
        setStartups(myStartups);
      } catch (err) {
        console.error("Error fetching startups:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStartups();
  }, [founderEmail]);

  // ✅ Fetch investor interest requests
  useEffect(() => {
    const fetchInvestorRequests = async () => {
      try {
        const res = await fetch(
          `${BACKEND_URL}/api/founder/interested-investors?founderEmail=${founderEmail}`
        );
        console.log(res)
        
        const data = await res.json();
        console.log("Investor interests:", data.investors);
        setInvestorRequests(data.investors || []);
      } catch (err) {
        console.error("Error fetching investor requests:", err);
      }
    };
    if (founderEmail) fetchInvestorRequests();
  }, [founderEmail]);

 

  // ✅ Fetch meetings for this founder
  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/meetings/founder/${founderEmail}`);
        const data = await res.json();
        setMeetings(data);
      } catch (err) {
        console.error("Error fetching meetings:", err);
      }
    };
    if (founderEmail) fetchMeetings();
  }, [founderEmail]);

  // ✅ Check if Google Calendar connected
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/google/is_connected?email=${founderEmail}`);
        const data = await res.json();
        setCalendarConnected(data.connected);
      } catch (err) {
        console.error("Error checking calendar connection:", err);
      }
    };
    if (founderEmail) checkConnection();
  }, [founderEmail]);

  // ✅ Grant Google Calendar Access
  const handleGrantCalendarAccess = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/google/authorize?email=${founderEmail}`);
      const data = await res.json();
      window.location.href = data.auth_url;
    } catch (err) {
      console.error("Error granting calendar access:", err);
      alert("Failed to connect Google Calendar.");
    }
  };

  // ✅ Respond to meeting requests
  const handleMeetingResponse = async (meetingId, action) => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/meetings/respond`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ meetingId, action }),
      });

      const data = await res.json();

      if (res.ok) {
        alert(`Meeting ${action}ed successfully!`);
        setMeetings((prev) =>
          prev.map((m) =>
            m._id === meetingId
              ? { ...m, status: action === "accept" ? "accepted" : "declined", hangoutLink: data.hangoutLink }
              : m
          )
        );
      } else {
        alert(`Error: ${data.detail}`);
      }
    } catch (err) {
      console.error("Error responding to meeting:", err);
    }
  };

  const handleChat = (investorEmail) => {
    const participants = [founderEmail, investorEmail];
    navigate("/chat", { state: { participants } });
  };

// ✅ Accept or Reject investor interest
  const handleResponse = async (investorEmail, action) => {
    try {
      if (action === "accept") {
        const res = await fetch(`${BACKEND_URL}/api/interests/accept`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            founderEmail,
            investorEmail,
          }),
        });
        const data = await res.json();
        alert("✅ Interest accepted. You can now chat with the investor.");
      } else {
        alert("❌ Request rejected.");
      }

      setInvestorRequests((prev) =>
        prev.map((req) =>
          req.investorEmail === investorEmail
            ? { ...req, status: action === "accept" ? "accepted" : "rejected" }
            : req
        )
      );
    } catch (err) {
      console.error("Error responding:", err);
    }
  };
//   return (
//   <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center bg-light">
//     <div className="container text-center">
//       <h1 className="mb-4 text-primary fw-bold">Founder Dashboard</h1>
//       <p className="text-muted mb-5">
//         Welcome back! Manage your startups and investor requests.
//       </p>

//       {/* --- Dashboard Options Row --- */}
//       <div className="row justify-content-center g-4 mb-5">
//         {/* Startup Registration */}
//         <div className="col-md-4 col-sm-6">
//           <div className="card shadow-sm border-0 rounded-4 h-100">
//             <div className="card-body">
//               <h5 className="card-title mb-3 text-primary">Startup Registration</h5>
//               <p className="card-text text-muted">
//                 Register your startup to get started with our AI evaluation system.
//               </p>
//               <button
//                 className="btn btn-primary w-100"
//                 onClick={() => handleNavigation("/startup-registration")}
//               >
//                 Go to Registration
//               </button>
//             </div>
//           </div>
//         </div>

//         {/* My Startups */}
//         <div className="col-md-4 col-sm-6">
//           <div className="card shadow-sm border-0 rounded-4 h-100">
//             <div className="card-body">
//               <h5 className="card-title mb-3 text-primary">My Startups</h5>
//               {loading ? (
//                 <p>Loading startups...</p>
//               ) : startups.length === 0 ? (
//                 <p className="text-muted">No startups registered yet.</p>
//               ) : (
//                 startups.map((startup) => (
//                   <div key={startup._id} className="text-start mb-3 border-top pt-2">
//                     <h6 className="fw-bold">{startup.startupName}</h6>
//                     <p className="mb-1">
//                       <strong>Registered:</strong> {startup.registeredName}
//                     </p>
//                     <p className="mb-1">
//                       <strong>Incorporation:</strong>{" "}
//                       {startup.incorporationMonth} {startup.incorporationYear}
//                     </p>
//                     <p className="mb-0">
//                       <strong>About:</strong> {startup.about}
//                     </p>
//                   </div>
//                 ))
//               )}
//             </div>
//           </div>
//         </div>

//         {/* Investor Requests */}
//         <div className="col-md-4 col-sm-6">
//           <div className="card shadow-sm border-0 rounded-4 h-100">
//             <div className="card-body">
//               <h5 className="card-title mb-3 text-success">Investor Requests</h5>
//               {investorRequests.length === 0 ? (
//                 <p className="text-muted">No investor requests yet.</p>
//               ) : (
//                 investorRequests.map((req, index) => (
//                   <div
//                     key={index}
//                     className="text-start mb-3 border-top pt-2"
//                   >
//                     <h6 className="fw-bold text-primary">
//                       {req.investorEmail}
//                     </h6>
//                     <p className="mb-1">
//                       <strong>Startup:</strong> {req.startupName}
//                     </p>
//                     <p className="mb-2">
//                       <strong>Status:</strong>{" "}
//                       <span
//                         className={
//                           req.status === "accepted"
//                             ? "text-success"
//                             : req.status === "rejected"
//                             ? "text-danger"
//                             : "text-warning"
//                         }
//                       >
//                         {req.status}
//                       </span>
//                     </p>

//                     {req.status === "pending" && (
//                       <div className="d-flex gap-2">
//                         <button
//                           className="btn btn-success btn-sm"
//                           onClick={() =>
//                             handleResponse(req.investorEmail, "accept")
//                           }
//                         >
//                           Accept
//                         </button>
//                         <button
//                           className="btn btn-outline-danger btn-sm"
//                           onClick={() =>
//                             handleResponse(req.investorEmail, "reject")
//                           }
//                         >
//                           Reject
//                         </button>
//                       </div>
//                     )}

//                     {req.status === "accepted" && (
//                       <button
//                         className="btn btn-outline-primary btn-sm mt-2"
//                         onClick={() => handleChat(req.investorEmail)}
//                       >
//                         Chat
//                       </button>
//                     )}
//                   </div>
//                 ))
//               )}
//             </div>
//           </div>
//         </div>
//       </div>

//       {/* --- Logout Button --- */}
//       <div className="mt-4">
//         <button className="btn btn-danger px-4" onClick={handleLogout}>
//           Logout
//         </button>
//       </div>
//     </div>
//   </div>
// );

return (
    <div className="min-vh-100 d-flex flex-column align-items-center bg-light">
      <div className="container text-center py-5">
        {/* ---------- Header ---------- */}
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1 className="text-primary fw-bold">Founder Dashboard</h1>
          <div>
            {!calendarConnected ? (
              <button
                className="btn btn-warning me-3"
                onClick={handleGrantCalendarAccess}
              >
                Connect Google Calendar
              </button>
            ) : (
              <span className="badge bg-success me-3 p-2">
                Calendar Connected
              </span>
            )}
            <button className="btn btn-danger" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>

        <p className="text-muted mb-5">
          Manage your startups, investor requests, and meeting schedules.
        </p>

        {/* ---------- Dashboard Cards ---------- */}
        <div className="row justify-content-center g-4 mb-5">
          {/* Startup Registration */}
          <div className="col-md-4 col-sm-6">
            <div className="card shadow-sm border-0 rounded-4 h-100">
              <div className="card-body">
                <h5 className="card-title text-primary">
                  Startup Registration
                </h5>
                <p className="text-muted">
                  Register your startup to get started with AI evaluation.
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

          {/* My Startups */}
          <div className="col-md-4 col-sm-6">
            <div className="card shadow-sm border-0 rounded-4 h-100">
              <div className="card-body">
                <h5 className="card-title text-primary">My Startups</h5>
                {loading ? (
                  <p>Loading startups...</p>
                ) : startups.length === 0 ? (
                  <p className="text-muted">No startups registered yet.</p>
                ) : (
                  startups.map((startup) => (
                    <div
                      key={startup._id}
                      className="text-start mb-3 border-top pt-2"
                    >
                      <h6 className="fw-bold">{startup.startupName}</h6>
                      <p className="mb-1">
                        <strong>Registered:</strong> {startup.registeredName}
                      </p>
                      <p className="mb-1">
                        <strong>Incorporation:</strong>{" "}
                        {startup.incorporationMonth} {startup.incorporationYear}
                      </p>
                      <p className="mb-0">
                        <strong>About:</strong> {startup.about}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Investor Requests */}
          <div className="col-md-4 col-sm-6">
            <div className="card shadow-sm border-0 rounded-4 h-100">
              <div className="card-body">
                <h5 className="card-title text-success">Investor Requests</h5>
                {investorRequests.length === 0 ? (
                  <p className="text-muted">No investor requests yet.</p>
                ) : (
                  investorRequests.map((req, index) => (
                    <div key={index} className="text-start mb-3 border-top pt-2">
                      <h6 className="fw-bold text-primary">
                        {req.investorEmail}
                      </h6>
                      <p className="mb-1">
                        <strong>Startup:</strong> {req.startupName}
                      </p>
                      <p className="mb-2">
                        <strong>Status:</strong>{" "}
                        <span
                          className={
                            req.status === "accepted"
                              ? "text-success"
                              : req.status === "rejected"
                              ? "text-danger"
                              : "text-warning"
                          }
                        >
                          {req.status}
                        </span>
                      </p>

                      {req.status === "pending" && (
                        <div className="d-flex gap-2">
                          <button
                            className="btn btn-success btn-sm"
                            onClick={() =>
                              handleResponse(req.investorEmail, "accept")
                            }
                          >
                            Accept
                          </button>
                          <button
                            className="btn btn-outline-danger btn-sm"
                            onClick={() =>
                              handleResponse(req.investorEmail, "reject")
                            }
                          >
                            Reject
                          </button>
                        </div>
                      )}

                      {req.status === "accepted" && (
                        <button
                          className="btn btn-outline-primary btn-sm mt-2"
                          onClick={() => handleChat(req.investorEmail)}
                        >
                          Chat
                        </button>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* ---------- Meeting Management ---------- */}
        <h3 className="text-primary fw-bold mt-4 mb-3">Meeting Requests</h3>
        {meetings.length === 0 ? (
          <p className="text-muted">No meeting requests yet.</p>
        ) : (
          <div className="row justify-content-center">
            {meetings.map((m) => (
              <div key={m._id} className="col-md-6 mb-3">
                <div className="card shadow-sm p-3 rounded-4 text-start">
                  <h5 className="text-primary">{m.startupName}</h5>
                  <p className="mb-1">
                    <strong>Investor:</strong> {m.investorEmail}
                  </p>
                  <p className="mb-1">
                    <strong>Time:</strong>{" "}
                    {new Date(m.proposedDateTime).toLocaleString("en-IN", {
                      dateStyle: "medium",
                      timeStyle: "short",
                      timeZone: "Asia/Kolkata", // force IST
                    })}
                  </p>
                  <p className="mb-2">
                    <strong>Status:</strong>{" "}
                    <span
                      className={`badge ${
                        m.status === "pending"
                          ? "bg-warning text-dark"
                          : m.status === "accepted"
                          ? "bg-success"
                          : "bg-danger"
                      }`}
                    >
                      {m.status.charAt(0).toUpperCase() + m.status.slice(1)}
                    </span>
                  </p>

                  {m.status === "pending" && (
                    <div className="d-flex gap-2 mt-2">
                      <button
                        className="btn btn-success btn-sm"
                        onClick={() => handleMeetingResponse(m._id, "accept")}
                      >
                        Accept
                      </button>
                      <button
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => handleMeetingResponse(m._id, "decline")}
                      >
                        Decline
                      </button>
                    </div>
                  )}

                  {m.status === "accepted" && m.hangoutLink && (
                    <a
                      href={m.hangoutLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-outline-primary btn-sm mt-2"
                    >
                      Join Meet
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}


