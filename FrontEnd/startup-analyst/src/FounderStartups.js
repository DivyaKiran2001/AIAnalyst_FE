import React, { useEffect, useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import FounderNavbar from "./FounderNavbar";

// const BACKEND_URL =
//   "https://8000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev";

const BACKEND_URL = "http://localhost:8000";

const FounderStartups = () => {
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);
  const founderEmail = sessionStorage.getItem("emailId");

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

  return (
    <>
      <FounderNavbar></FounderNavbar>
      <div className="container py-5">
        <h2 className="text-primary fw-bold mb-4 text-center">My Startups</h2>
        <div className="card shadow-sm border-0 rounded-4 p-4">
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
                  <strong>Incorporation:</strong> {startup.incorporationMonth}{" "}
                  {startup.incorporationYear}
                </p>
                <p className="mb-0">
                  <strong>About:</strong> {startup.about}
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
};

export default FounderStartups;
