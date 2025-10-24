import React, { useEffect, useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import FounderNavbar from "./FounderNavbar";

const BACKEND_URL = "https://8000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev";

const FounderMeetings = () => {
  const founderEmail = sessionStorage.getItem("emailId");
  const [meetings, setMeetings] = useState([]);

  useEffect(() => {
    const fetchMeetings = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/meetings/founder/${founderEmail}`);
        const data = await res.json();
        setMeetings(data.meetings || []);
      } catch (err) {
        console.error("Error fetching meetings:", err);
      }
    };
    if (founderEmail) fetchMeetings();
  }, [founderEmail]);

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

  return (
    <><FounderNavbar></FounderNavbar><div className="container py-5">
          <h2 className="text-primary fw-bold mb-4 text-center">Meeting Requests</h2>
          {meetings.length === 0 ? (
              <p className="text-muted text-center">No meeting requests yet.</p>
          ) : (
              <div className="row justify-content-center">
                  {meetings.map((m) => (
                      <div key={m._id} className="col-md-6 mb-3">
                          <div className="card shadow-sm p-3 rounded-4 text-start">
                              <h5 className="text-primary">{m.startupName}</h5>
                              <p className="mb-1"><strong>Investor:</strong> {m.investorEmail}</p>
                              <p className="mb-1">
                                  <strong>Time:</strong>{" "}
                                  {new Date(m.proposedDateTime).toLocaleString("en-IN", {
                                      dateStyle: "medium",
                                      timeStyle: "short",
                                      timeZone: "Asia/Kolkata",
                                  })}
                              </p>
                              <p className="mb-2">
                                  <strong>Status:</strong>{" "}
                                  <span
                                      className={`badge ${m.status === "pending"
                                              ? "bg-warning text-dark"
                                              : m.status === "accepted"
                                                  ? "bg-success"
                                                  : "bg-danger"}`}
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
      </div></>
  );
};

export default FounderMeetings;
