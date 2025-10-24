import React, { useEffect, useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import FounderNavbar from "./FounderNavbar"; // import your navbar

const Fdashboard = () => {
  const [founderName, setFounderName] = useState("Divya Kiran");
  const [startupDetails, setStartupDetails] = useState({
    name: "Ziniosa",
    incorporation: "September 2024",
    about: "Ziniosa is a startup focused on fashion rental and resale innovation.",
  });

  const [meetings, setMeetings] = useState([
    { id: 1, title: "Meeting with Angel Investor", date: "2025-10-28", time: "3:00 PM" },
    { id: 2, title: "Pitch Review Session", date: "2025-10-30", time: "11:00 AM" },
  ]);

  useEffect(() => {
    // Later, you can fetch data here using your backend API.
    // Example: fetch("/api/founder/startup").then(res => res.json()).then(setStartupDetails);
  }, []);

  return (
    <>
      <FounderNavbar />
      <div className="container mt-4">
        <h2 className="fw-bold mb-3">👋 Welcome, {founderName}!</h2>
        <p className="text-muted">Here’s an overview of your startup activity and upcoming meetings.</p>

        {/* Startup Summary Cards */}
        <div className="row mt-4">
          <div className="col-md-4">
            <div className="card shadow-sm border-0 rounded-3">
              <div className="card-body">
                <h5 className="card-title">🏢 Startup</h5>
                <p className="card-text fw-semibold">{startupDetails.name}</p>
                <p className="text-muted">{startupDetails.about}</p>
              </div>
            </div>
          </div>

          <div className="col-md-4">
            <div className="card shadow-sm border-0 rounded-3">
              <div className="card-body">
                <h5 className="card-title">📅 Incorporated</h5>
                <p className="fw-semibold">{startupDetails.incorporation}</p>
                <p className="text-muted">Startup officially registered.</p>
              </div>
            </div>
          </div>

          <div className="col-md-4">
            <div className="card shadow-sm border-0 rounded-3">
              <div className="card-body">
                <h5 className="card-title">🚀 Status</h5>
                <p className="fw-semibold text-success">Active</p>
                <p className="text-muted">You’re ready to pitch!</p>
              </div>
            </div>
          </div>
        </div>

        {/* Meetings Section */}
        <div className="mt-5">
          <h4 className="fw-bold mb-3">📆 Upcoming Meetings</h4>
          {meetings.length > 0 ? (
            <table className="table table-hover shadow-sm">
              <thead className="table-primary">
                <tr>
                  <th>Title</th>
                  <th>Date</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {meetings.map((meeting) => (
                  <tr key={meeting.id}>
                    <td>{meeting.title}</td>
                    <td>{meeting.date}</td>
                    <td>{meeting.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-muted">No meetings scheduled yet.</p>
          )}
        </div>

        {/* Requests Section */}
        <div className="mt-5">
          <h4 className="fw-bold mb-3">📨 Recent Requests</h4>
          <div className="alert alert-info">
            You have 2 pending investment requests awaiting response.
          </div>
        </div>
      </div>
    </>
  );
};

export default Fdashboard;
