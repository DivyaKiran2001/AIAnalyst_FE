import React, { useEffect, useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import FounderNavbar from "./FounderNavbar";

const BACKEND_URL =
  "https://8000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev";

const FounderMeetings = () => {
  const founderEmail = sessionStorage.getItem("emailId");
  const [meetings, setMeetings] = useState([]);
  const [calendarConnected, setCalendarConnected] = useState(false);

  // Fetch meetings
  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const res = await fetch(
          `${BACKEND_URL}/api/meetings/founder/${founderEmail}`
        );
        const data = await res.json();
        setMeetings(data.meetings || []);
      } catch (err) {
        console.error("Error fetching meetings:", err);
      }
    };
    if (founderEmail) fetchMeetings();
  }, [founderEmail]);

  // Check Google Calendar connection
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const res = await fetch(
          `${BACKEND_URL}/api/google/is_connected?email=${founderEmail}`
        );
        const data = await res.json();
        setCalendarConnected(data.connected);
      } catch (err) {
        console.error("Error checking calendar connection:", err);
      }
    };
    if (founderEmail) checkConnection();
  }, [founderEmail]);

  // Handle Google Calendar reconnect
  const handleReconnectCalendar = () => {
    window.location.href = `${BACKEND_URL}/api/google/authorize?email=${founderEmail}`;
  };

  // Handle accept/decline
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
              ? {
                  ...m,
                  status: action === "accept" ? "accepted" : "declined",
                  hangoutLink: data.hangoutLink,
                }
              : m
          )
        );
      } else if (
        res.status === 401 &&
        data.detail &&
        data.detail.includes("Google authorization expired")
      ) {
        const connectNow = window.confirm(
          "Your Google Calendar authorization has expired. Connect again now?"
        );
        if (connectNow) handleReconnectCalendar();
      } else {
        alert(`Error: ${data.detail}`);
      }
    } catch (err) {
      console.error("Error responding to meeting:", err);
      alert("Something went wrong. Please try again.");
    }
  };

  return (
    <>
      <FounderNavbar />
      <div
        className="min-vh-100 py-5"
        style={{ backgroundColor: "#f0f0f0" }} // grey page background
      >
        <div className="container">
          <h2
            className="text-center mb-3"
            style={{ color: "rgb(18, 0, 94)", fontWeight: "700" }}
          >
            Meeting Requests
          </h2>

          {/* Calendar Connection Status */}
          <div className="text-center mb-4">
            {calendarConnected ? (
              <span
                className="badge"
                style={{
                  backgroundColor: "rgb(18, 0, 94)",
                  color: "#fff",
                  padding: "0.5rem 1rem",
                  fontSize: "1rem",
                }}
              >
                Calendar Connected
              </span>
            ) : (
              <>
                <span
                  className="badge bg-danger p-2"
                  style={{ fontSize: "1rem", marginRight: "10px" }}
                >
                  Calendar Not Connected
                </span>
                <button
                  className="btn btn-outline-dark-blue btn-sm"
                  style={{
                    backgroundColor: "rgb(18,0,94)",
                    color: "#fff",
                    borderColor: "rgb(18,0,94)",
                  }}
                  onClick={handleReconnectCalendar}
                >
                  Connect Now
                </button>
              </>
            )}
          </div>

          {meetings.length === 0 ? (
            <p
              className="text-center text-muted"
              style={{ fontSize: "1.1rem" }}
            >
              No meeting requests yet.
            </p>
          ) : (
            <div className="row justify-content-center">
              {meetings.map((m) => (
                <div key={m._id} className="col-md-6 mb-4">
                  <div
                    className="card shadow-sm p-4 rounded-4"
                    style={{ backgroundColor: "#ffffff" }} // white card
                  >
                    <h5
                      style={{ color: "rgb(18, 0, 94)", fontWeight: "600" }}
                      className="mb-2"
                    >
                      {m.startupName}
                    </h5>
                    <p className="mb-1">
                      <strong style={{ color: "rgb(18, 0, 94)" }}>Investor:</strong>{" "}
                      {m.investorEmail}
                    </p>
                    <p className="mb-1">
                      <strong style={{ color: "rgb(18, 0, 94)" }}>Time:</strong>{" "}
                      {new Date(m.proposedDateTime).toLocaleString("en-IN", {
                        dateStyle: "medium",
                        timeStyle: "short",
                        timeZone: "Asia/Kolkata",
                      })}
                    </p>
                    <p className="mb-2">
                      <strong style={{ color: "rgb(18, 0, 94)" }}>Status:</strong>{" "}
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
                      <div className="d-flex gap-2 mt-3">
                        <button
                          className="btn btn-sm"
                          style={{
                            backgroundColor: "rgb(18,0,94)",
                            color: "#fff",
                          }}
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
                        className="btn btn-outline-dark-blue btn-sm mt-3"
                        style={{
                          color: "rgb(18,0,94)",
                          borderColor: "rgb(18,0,94)",
                        }}
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
    </>
  );
};

export default FounderMeetings;
