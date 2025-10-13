import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const InvestorDashboard = () => {
  const navigate = useNavigate();
  const [startups, setStartups] = useState([]);
  const [interests, setInterests] = useState([]);
  const [loading, setLoading] = useState(true);

  const investorEmail = sessionStorage.getItem("emailId");

  const handleLogout = () => {
    sessionStorage.clear();
    navigate("/"); // redirect to login/signup
  };

  // Fetch startups on mount
    useEffect(() => {
    const fetchData = async () => {
      try {
        const [startupRes, interestRes] = await Promise.all([
          fetch("https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/startups"),
          fetch(`https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/interests?investorEmail=${investorEmail}`)
        ]);
        const startupData = await startupRes.json();
        const interestData = await interestRes.json();

        setStartups(startupData);
        setInterests(interestData);
      } catch (err) {
        console.error("Error fetching data:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [investorEmail]);

   // Express interest
  const handleInterest = async (founderEmail,startupName,investorEmail) => {
    try {
      const res = await fetch("https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/interests", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          startupName,
          founderEmail,
          investorEmail,
          status: "pending"
        }),
      });

      if (res.ok) {
        alert("Interest sent to founder!");
        const newInterest = await res.json();
        setInterests((prev) => [...prev, newInterest]);
      } else {
        alert("Error sending interest");
      }
    } catch (err) {
      console.error("Error:", err);
    }
  };

  // Chat after acceptance
  const handleChat = (founderEmail) => {
    const participants = [founderEmail, investorEmail];
    navigate("/chat", { state: { participants } });
  };

  // Check interest status for each startup
  const getInterestStatus = (founderEmail) => {
    const record = interests.find(
      (i) => i.founderEmail === founderEmail && i.investorEmail === investorEmail
    );
    return record ? record.status : null;
  };

  return (
    <div className="container mt-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Investor Dashboard</h2>
        <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
      </div>

      <div className="card p-4 mb-3 bg-light">
        <h4>Welcome, Investor!</h4>
        <p>Review startups and express interest in investing.</p>
      </div>

      <h4 className="mt-4 mb-3">Startup Opportunities</h4>

      {loading ? (
        <p>Loading startups...</p>
      ) : startups.length === 0 ? (
        <p>No startups found.</p>
      ) : (
        <div className="row">
          {startups.map((startup) => {
            const status = getInterestStatus(startup.emailId);
            return (
              <div key={startup._id} className="col-md-6 mb-4">
                <div className="card shadow-sm p-3 h-100">
                  <h5 className="text-primary">{startup.startupName}</h5>
                  <p><strong>Registered Name:</strong> {startup.registeredName}</p>
                  <p><strong>Incorporation:</strong> {startup.incorporationMonth} {startup.incorporationYear}</p>
                  <p><strong>About:</strong> {startup.about}</p>
                  <p><strong>Founder:</strong> {startup.emailId}</p>

                  {status === "accepted" ? (
                    <button
                      className="btn btn-success mt-2"
                      onClick={() => handleChat(startup.emailId)}
                    >
                      Chat with Founder
                    </button>
                  ) : status === "pending" ? (
                    <button className="btn btn-secondary mt-2" disabled>
                      Interest Pending
                    </button>
                  ) : (
                    <button
                      className="btn btn-outline-primary mt-2"
                      onClick={() => handleInterest(startup.emailId,startup.startupName,investorEmail)}
                    >
                      Interested
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default InvestorDashboard;