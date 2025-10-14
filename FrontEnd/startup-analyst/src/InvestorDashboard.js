import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const InvestorDashboard = () => {
  const navigate = useNavigate();
  const [startups, setStartups] = useState([]);
  const [interests, setInterests] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
const [calendarConnected, setCalendarConnected] = useState(false);
  const investorEmail = sessionStorage.getItem("emailId");

  const [showMeetingForm, setShowMeetingForm] = useState(false);
  const [meetingData, setMeetingData] = useState({ founderEmail: "", startupName: "", date: "", time: "" });
  const handleLogout = () => {
    sessionStorage.clear();
    navigate("/"); // redirect to login/signup
  };



  useEffect(() => {
  const checkConnection = async () => {
    const res = await fetch(`https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/google/is_connected?email=${investorEmail}`);
    const data = await res.json();
    setCalendarConnected(data.connected);
    if (data.connected) {
      sessionStorage.setItem("calendarConnected", "true");
    }
  };
  checkConnection();
}, [investorEmail]);

useEffect(() => {
  const fetchMeetings = async () => {
    try {
      const res = await fetch(
        `https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/meetings/investor/${investorEmail}`
      );
      const data = await res.json();
      setMeetings(data);
    } catch (err) {
      console.error("Error fetching meetings:", err);
    }
  };

  if (investorEmail) fetchMeetings();
}, [investorEmail]);
  // ---------- Grant Google Calendar Access ----------
  const handleGrantCalendarAccess = async () => {
    try {
      const res = await fetch(
        `https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/google/authorize?email=${investorEmail}`
      );
      const data = await res.json();
      window.location.href = data.auth_url; // Redirect to Google consent screen
    } catch (err) {
      console.error("Error granting access:", err);
      alert("Failed to connect Google Calendar.");
    }
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
    // Open Meeting Form
  const openMeetingForm = (founderEmail, startupName) => {
    setMeetingData({ founderEmail, startupName, date: "", time: "" });
    setShowMeetingForm(true);
  };

  const submitMeeting = async () => {
    const { founderEmail, startupName, date, time } = meetingData;
    if (!date || !time) {
      alert("Please select date and time");
      return;
    }
   
    const proposedDateTime = new Date(`${date}T${time}:00`);
    if (isNaN(proposedDateTime.getTime())) {
      alert("Invalid date/time");
      return;
    }

    setMeetingData((prev) => ({ ...prev, submitting: true }));
    try {
      const res = await fetch("https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/meetings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ founderEmail, investorEmail, startupName, proposedDateTime: proposedDateTime.toISOString() })
      });
      if (res.ok) {
        alert("Meeting request sent!");
        setShowMeetingForm(false);
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
      }
    } catch (err) {
      console.error(err);
      alert("Error sending meeting request.");
    }finally {
    setMeetingData((prev) => ({ ...prev, submitting: false }));
  }
  };

  // Render
  return (
    <div className="container mt-5">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Investor Dashboard</h2>
        <div>
          {!calendarConnected ? (
            <button className="btn btn-warning me-3" onClick={handleGrantCalendarAccess}>Connect Google Calendar</button>
          ) : (
            <span className="badge bg-success me-3">Calendar Connected</span>
          )}
          <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
        </div>
      </div>

      {/* Welcome */}
      <div className="card p-4 mb-3 bg-light">
        <h4>Welcome, Investor!</h4>
        <p>Review startups, express interest, and schedule meetings easily.</p>
      </div>

      {/* Startups */}
      <h4 className="mt-4 mb-3">Startup Opportunities</h4>
      {loading ? <p>Loading startups...</p> : (
        <div className="row">
          {startups.map(startup => {
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
                    <>
                      <button className="btn btn-success mt-2" onClick={() => handleChat(startup.emailId)}>Chat</button>
                      <button className="btn btn-outline-primary mt-2 ms-2" onClick={() => openMeetingForm(startup.emailId, startup.startupName)}>Request Meeting</button>
                    </>
                  ) : status === "pending" ? (
                    <button className="btn btn-secondary mt-2" disabled>Interest Pending</button>
                  ) : (
                    <button className="btn btn-outline-primary mt-2" onClick={() => handleInterest(startup.emailId, startup.startupName, investorEmail)}>Interested</button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Meetings Section */}
<h4 className="mt-5 mb-3">Your Scheduled Meetings</h4>
{meetings.length === 0 ? (
  <p className="text-muted">No meeting requests yet.</p>
) : (
  <div className="row">
    {meetings.map((meeting) => (
      <div key={meeting._id} className="col-md-6 mb-4">
        <div className="card shadow-sm p-3">
          <h5 className="text-primary">{meeting.startupName}</h5>
          <p><strong>Founder:</strong> {meeting.founderEmail}</p>

          <p>
            <strong>Proposed Time:</strong>{" "}
            {new Date(meeting.proposedDateTime).toLocaleString("en-IN", {
              dateStyle: "medium",
              timeStyle: "short",
            })}
          </p>

          <p>
            <strong>Status:</strong>{" "}
            <span
              className={`badge ${
                meeting.status === "pending"
                  ? "bg-warning text-dark"
                  : meeting.status === "confirmed"
                  ? "bg-success"
                  : "bg-secondary"
              }`}
            >
              {meeting.status.charAt(0).toUpperCase() + meeting.status.slice(1)}
               
            </span>
            {meeting.status === "accepted" && meeting.hangoutLink && (
                    <a
                      href={meeting.hangoutLink}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-outline-primary btn-sm mt-2"
                    >
                      Join Meet
                    </a>
                  )}
          </p>
        </div>
      </div>
    ))}
  </div>
)}


      
{showMeetingForm && (
  <div
    className="modal d-block"
    style={{
      backgroundColor: "rgba(0, 0, 0, 0.6)",
      backdropFilter: "blur(4px)",
    }}
  >
    <div className="modal-dialog modal-dialog-centered">
      <div className="modal-content p-4 rounded-4 shadow-lg">
        <h5 className="text-center mb-3 text-primary fw-bold">
          Schedule Meeting with {meetingData.startupName}
        </h5>

        <div className="mb-3">
          <label className="form-label fw-semibold">Startup Name</label>
          <input
            type="text"
            className="form-control"
            value={meetingData.startupName}
            readOnly
          />
        </div>

        <div className="mb-3">
          <label className="form-label fw-semibold">Founder Email</label>
          <input
            type="email"
            className="form-control"
            value={meetingData.founderEmail}
            readOnly
          />
        </div>

        <div className="mb-3">
          <label className="form-label fw-semibold">Investor Email</label>
          <input
            type="email"
            className="form-control"
            value={investorEmail}
            readOnly
          />
        </div>

        <div className="row">
          <div className="col-md-6 mb-3">
            <label className="form-label fw-semibold">Date</label>
            <input
              type="date"
              className="form-control"
              value={meetingData.date}
              min={new Date().toISOString().split("T")[0]}
              onChange={(e) =>
                setMeetingData({ ...meetingData, date: e.target.value })
              }
              disabled={meetingData.submitting}
            />
          </div>

          <div className="col-md-6 mb-3">
            <label className="form-label fw-semibold">Time (9 AM – 5 PM)</label>
            <input
              type="time"
              className="form-control"
              value={meetingData.time}
              min="09:00"
              max="17:00"
              step="1800" // 30-min increments
              onChange={(e) =>
                setMeetingData({ ...meetingData, time: e.target.value })
              }
              disabled={meetingData.submitting}
            />
            {meetingData.time && (
              <small className="text-muted">
                Selected Time:{" "}
                {(() => {
                  const [hour, minute] = meetingData.time.split(":");
                  const h = parseInt(hour);
                  const ampm = h >= 12 ? "PM" : "AM";
                  const displayHour = h % 12 || 12;
                  return `${displayHour}:${minute} ${ampm}`;
                })()}
              </small>
            )}
          </div>
        </div>

        <div className="d-flex justify-content-end mt-3">
          <button
            className="btn btn-secondary me-2"
            onClick={() => setShowMeetingForm(false)}
            disabled={meetingData.submitting}
          >
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={submitMeeting}
            disabled={meetingData.submitting}
          >
            {meetingData.submitting ? (
              <span>
                <span
                  className="spinner-border spinner-border-sm me-2"
                  role="status"
                  aria-hidden="true"
                ></span>
                Sending...
              </span>
            ) : (
              "Send Request"
            )}
          </button>
        </div>
      </div>
    </div>
  </div>
)}

    </div>
  );
};

export default InvestorDashboard;