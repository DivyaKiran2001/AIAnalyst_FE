// import React, { useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";
// import io from "socket.io-client";
// import "bootstrap/dist/css/bootstrap.min.css";

// const socket = io("https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io"); // replace with your backend URL

// export default function FounderDashboard() {
//   const navigate = useNavigate();
//   const [startups, setStartups] = useState([]);
//   const [loading, setLoading] = useState(true);

//   const handleNavigation = (path) => {
//     navigate(path);
//   };

//   const handleLogout = () => {
//     localStorage.clear();
//     navigate("/"); // redirect to login/signup page
//   };

//   // Fetch founder's startups
//   useEffect(() => {
//     const fetchStartups = async () => {
//       try {
//         const res = await fetch("https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/startups");
//         const data = await res.json();
//         console.log("STTTTT",data)
//         // Filter startups owned by logged-in founder
//         const founderEmail = localStorage.getItem("emailId"); // consistent key
//         if (!founderEmail) {
//           console.warn("⚠️ No founder email found in localStorage.");
//           setStartups([]);
//           return;
//         }
//         const myStartups = data.filter((s) => s.emailId === founderEmail);
//         console.log("Mystartups",myStartups)
//         setStartups(myStartups);
//       } catch (err) {
//         console.error("Error fetching startups:", err);
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchStartups();
//   }, []);

//   const handleChat = (investorEmail) => {
//     const founderEmail = localStorage.getItem("userEmail"); // logged-in founder
//     const participants = [founderEmail, investorEmail];
//     navigate("/chat", { state: { participants } });
//   };

//   return (
//     <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center bg-light">
//       <div className="container text-center">
//         <h1 className="mb-4 text-primary fw-bold">Founder Dashboard</h1>
//         <p className="text-muted mb-5">
//           Welcome back! Manage your startups or start chatting with investors.
//         </p>

//         {/* Startup Registration Button */}
//         <div className="row justify-content-center mb-4">
//           <div className="col-md-4 mb-3">
//             <div className="card shadow-sm border-0 rounded-4">
//               <div className="card-body">
//                 <h5 className="card-title mb-3">Startup Registration</h5>
//                 <p className="card-text text-muted">
//                   Register your startup to get started with our AI evaluation system.
//                 </p>
//                 <button
//                   className="btn btn-primary w-100"
//                   onClick={() => handleNavigation("/startup-registration")}
//                 >
//                   Go to Registration
//                 </button>
//               </div>
//             </div>
//           </div>
//         </div>

//         {/* My Startups List */}
//         <h4 className="mt-4 mb-3">My Startups</h4>
//         {loading ? (
//           <p>Loading startups...</p>
//         ) : startups.length === 0 ? (
//           <p>You have not registered any startups yet.</p>
//         ) : (
//           <div className="row">
//             {startups.map((startup) => (
//               <div key={startup._id} className="col-md-6 mb-4">
//                 <div className="card shadow-sm p-3 h-100">
//                   <h5 className="text-primary">{startup.startupName}</h5>
//                   <p><strong>Registered Name:</strong> {startup.registeredName}</p>
//                   <p><strong>Incorporation:</strong> {startup.incorporationMonth} {startup.incorporationYear}</p>
//                   <p><strong>About:</strong> {startup.about}</p>
//                   {/* Chat Button with investor (demo: replace with actual investors later) */}
//                   <button
//                     className="btn btn-outline-success mt-2"
//                     onClick={() => handleChat("investor@example.com")}
//                   >
//                     Chat with Investor
//                   </button>
//                 </div>
//               </div>
//             ))}
//           </div>
//         )}

//         <div className="mt-5">
//           <button className="btn btn-danger px-4" onClick={handleLogout}>
//             Logout
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }


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

  const founderEmail = localStorage.getItem("emailId");

  const handleNavigation = (path) => {
    navigate(path);
  };

  const handleLogout = () => {
    localStorage.clear();
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

  // ✅ Accept or Reject an interest
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
        console.log("Accepted:", data);
        alert("✅ Interest accepted. You can now chat with the investor.");
      } else if (action === "reject") {
        // Just update status manually (optional endpoint could be added)
        alert("❌ Request rejected.");
      }
      // Refresh list after response
      setInvestorRequests((prev) =>
        prev.map((req) =>
          req.investorEmail === investorEmail
            ? { ...req, status: action === "accept" ? "accepted" : "rejected" }
            : req
        )
      );
    } catch (err) {
      console.error("Error responding to request:", err);
    }
  };

  const handleChat = (investorEmail) => {
    const participants = [founderEmail, investorEmail];
    navigate("/chat", { state: { participants } });
  };

  return (
    <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center bg-light">
      <div className="container text-center">
        <h1 className="mb-4 text-primary fw-bold">Founder Dashboard</h1>
        <p className="text-muted mb-5">
          Welcome back! Manage your startups and investor requests.
        </p>

        {/* --- Startup Registration --- */}
        <div className="row justify-content-center mb-4">
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
        </div>

        {/* --- My Startups --- */}
        <h4 className="mt-4 mb-3">My Startups</h4>
        {loading ? (
          <p>Loading startups...</p>
        ) : startups.length === 0 ? (
          <p>You have not registered any startups yet.</p>
        ) : (
          <div className="row">
            {startups.map((startup) => (
              <div key={startup._id} className="col-md-6 mb-4">
                <div className="card shadow-sm p-3 h-100">
                  <h5 className="text-primary">{startup.startupName}</h5>
                  <p>
                    <strong>Registered Name:</strong> {startup.registeredName}
                  </p>
                  <p>
                    <strong>Incorporation:</strong> {startup.incorporationMonth}{" "}
                    {startup.incorporationYear}
                  </p>
                  <p>
                    <strong>About:</strong> {startup.about}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* --- Investor Requests --- */}
        <h4 className="mt-5 mb-3 text-success">Investor Requests</h4>
        {investorRequests.length === 0 ? (
          <p>No investor requests yet.</p>
        ) : (
          <div className="row justify-content-center">
            {investorRequests.map((req, index) => (
              <div key={index} className="col-md-6 mb-3">
                <div className="card shadow-sm p-3">
                  <h5 className="text-dark">
                    Investor: <span className="text-primary">{req.investorEmail}</span>
                  </h5>
                  <p>
                    <strong>Startup:</strong> {req.startupName}
                  </p>
                  <p>
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
                    <div className="d-flex gap-2 justify-content-center mt-2">
                      <button
                        className="btn btn-success"
                        onClick={() => handleResponse(req.investorEmail, "accept")}
                      >
                        Accept
                      </button>
                      <button
                        className="btn btn-outline-danger"
                        onClick={() => handleResponse(req.investorEmail, "reject")}
                      >
                        Reject
                      </button>
                    </div>
                  )}

                  {req.status === "accepted" && (
                    <button
                      className="btn btn-outline-primary mt-2"
                      onClick={() => handleChat(req.investorEmail)}
                    >
                      Chat with {req.investorEmail}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-5">
          <button className="btn btn-danger px-4" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </div>
  );
}
