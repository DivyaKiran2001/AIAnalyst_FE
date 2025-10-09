// import React from "react";
// import { useNavigate } from "react-router-dom";
// import "bootstrap/dist/css/bootstrap.min.css";

// export default function FounderDashboard() {
//   const navigate = useNavigate();

//   const handleNavigation = (path) => {
//     navigate(path);
//   };

//   const handleLogout = () => {
//     navigate("/"); // redirect to login/signup page
//   };

//   return (
//     <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center bg-light">
//       <div className="container text-center">
//         <h1 className="mb-4 text-primary fw-bold">Founder Dashboard</h1>
//         <p className="text-muted mb-5">
//           Welcome back! Choose an option to continue.
//         </p>

//         <div className="row justify-content-center">
//           {/* Startup Registration */}
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

//           {/* View Registered Startups */}
//           <div className="col-md-4 mb-3">
//             <div className="card shadow-sm border-0 rounded-4">
//               <div className="card-body">
//                 <h5 className="card-title mb-3">View My Startups</h5>
//                 <p className="card-text text-muted">
//                   See your registered startups and their evaluation progress.
//                 </p>
//                 <button className="btn btn-outline-primary w-100" disabled>
//                   Coming Soon
//                 </button>
//               </div>
//             </div>
//           </div>

//           {/* Profile Settings */}
//           <div className="col-md-4 mb-3">
//             <div className="card shadow-sm border-0 rounded-4">
//               <div className="card-body">
//                 <h5 className="card-title mb-3">Profile Settings</h5>
//                 <p className="card-text text-muted">
//                   Manage your founder profile and update contact information.
//                 </p>
//                 <button className="btn btn-outline-primary w-100" disabled>
//                   Coming Soon
//                 </button>
//               </div>
//             </div>
//           </div>
//         </div>

//         <div className="mt-5">
//           <button
//             className="btn-danger px-4"
//             onClick={handleLogout}
//           >
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

const socket = io("http://localhost:8000"); // replace with your backend URL

export default function FounderDashboard() {
  const navigate = useNavigate();
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleNavigation = (path) => {
    navigate(path);
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate("/"); // redirect to login/signup page
  };

  // Fetch founder's startups
  useEffect(() => {
    const fetchStartups = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/startups");
        const data = await res.json();
        // Filter startups owned by logged-in founder
        const email = localStorage.getItem("userEmail"); // store userEmail on login
        const myStartups = data.filter((s) => s.emailId === email);
        setStartups(myStartups);
      } catch (err) {
        console.error("Error fetching startups:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStartups();
  }, []);

  const handleChat = (investorEmail) => {
    const founderEmail = localStorage.getItem("userEmail"); // logged-in founder
    const participants = [founderEmail, investorEmail];
    navigate("/chat", { state: { participants } });
  };

  return (
    <div className="min-vh-100 d-flex flex-column align-items-center justify-content-center bg-light">
      <div className="container text-center">
        <h1 className="mb-4 text-primary fw-bold">Founder Dashboard</h1>
        <p className="text-muted mb-5">
          Welcome back! Manage your startups or start chatting with investors.
        </p>

        {/* Startup Registration Button */}
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

        {/* My Startups List */}
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
                  <p><strong>Registered Name:</strong> {startup.registeredName}</p>
                  <p><strong>Incorporation:</strong> {startup.incorporationMonth} {startup.incorporationYear}</p>
                  <p><strong>About:</strong> {startup.about}</p>
                  {/* Chat Button with investor (demo: replace with actual investors later) */}
                  <button
                    className="btn btn-outline-success mt-2"
                    onClick={() => handleChat("investor@example.com")}
                  >
                    Chat with Investor
                  </button>
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
