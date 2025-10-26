// import React, { useEffect, useState } from "react";
// import "bootstrap/dist/css/bootstrap.min.css";
// import InvestorNavbar from "./InvestorNavbar"; // If you have one, else remove
// const BACKEND_URL = "http://localhost:8000";

// const InvestorDeals = () => {
//   const [startups, setStartups] = useState([]);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     const fetchStartups = async () => {
//       try {
//         const res = await fetch(`${BACKEND_URL}/api/startups`);
//         const data = await res.json();
//         setStartups(data);
//       } catch (err) {
//         console.error("Error fetching startup list:", err);
//       } finally {
//         setLoading(false);
//       }
//     };

//     fetchStartups();
//   }, []);

//   const handleGenerateReport = (startup) => {
//     alert(`Generate report for: ${startup.startupName}`);
//     // Later connect to your report generation endpoint
//   };

//   return (
//     <>
//       <InvestorNavbar />

//       <div style={{ backgroundColor: "#f5f5f5", minHeight: "100vh" }}>
//         <div className="container py-5">
//           <h2
//             className="fw-bold mb-4 text-center"
//             style={{ color: "rgb(18,0,94)" }}
//           >
//             Available Startup Deals
//           </h2>

//           {loading ? (
//             <p className="text-center">Loading startups...</p>
//           ) : startups.length === 0 ? (
//             <p className="text-muted text-center">No startups yet.</p>
//           ) : (
//             <div className="row g-4">
//               {startups.map((startup, index) => (
//                 <div key={index} className="col-md-6 col-lg-4">
//                   <div
//                     className="card shadow-sm border-0 rounded-4 h-100 p-4"
//                     style={{ backgroundColor: "white", color: "rgb(18,0,94)" }}
//                   >
//                     <h4 className="fw-bold mb-2">{startup.startupName}</h4>

//                     <p className="mb-1">
//                       <strong>Registered:</strong> {startup.registeredName}
//                     </p>

//                     <p className="mb-1">
//                       <strong>Incorporation:</strong>{" "}
//                       {startup.incorporationMonth} {startup.incorporationYear}
//                     </p>

//                     <p className="mb-3" style={{ minHeight: "60px" }}>
//                       <strong>About:</strong> {startup.about}
//                     </p>

//                     {/* Generate Report Button */}
//                     <button
//                       className="btn mt-auto"
//                       style={{
//                         backgroundColor: "rgb(18,0,94)",
//                         color: "white",
//                         fontWeight: "bold",
//                         width: "100%",
//                         padding: "10px",
//                         borderRadius: "10px",
//                       }}
//                       onClick={() => handleGenerateReport(startup)}
//                     >
//                       Generate Report
//                     </button>
//                   </div>
//                 </div>
//               ))}
//             </div>
//           )}
//         </div>
//       </div>
//     </>
//   );
// };

// export default InvestorDeals;

import React, { useEffect, useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import InvestorNavbar from "./InvestorNavbar";
import { Modal } from "react-bootstrap";

const BACKEND_URL = "http://localhost:8000";

const InvestorDeals = () => {
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    const fetchStartups = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/startups`);
        const data = await res.json();
        setStartups(data);
      } catch (err) {
        console.error("Error fetching startups:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStartups();
  }, []);

  const handleGenerateReport = async (startup) => {
    alert(`Generate Report for: ${startup.startupName}`);
    // Later connect report-generation API here
  };

  return (
    <>
      <InvestorNavbar />

      {/* ✅ Pitch Deck Preview Modal */}
      <Modal
        show={!!previewUrl}
        onHide={() => setPreviewUrl(null)}
        size="xl"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Pitch Deck Preview</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ height: "80vh" }}>
          <iframe
            src={previewUrl}
            width="100%"
            height="100%"
            style={{ border: "none" }}
            title="Pitch Deck Preview"
          ></iframe>
        </Modal.Body>
      </Modal>

      <div style={{ backgroundColor: "#f5f5f5", minHeight: "100vh" }}>
        <div className="container py-5">
          <h2
            className="fw-bold mb-4 text-center"
            style={{ color: "rgb(18,0,94)" }}
          >
            Available Startup Deals
          </h2>

          {loading ? (
            <p className="text-center">Loading startups...</p>
          ) : startups.length === 0 ? (
            <p className="text-muted text-center">No startups available.</p>
          ) : (
            startups.map((startup, index) => (
              <div
                key={index}
                className="card shadow-sm border-0 rounded-4 p-4 mb-4"
                style={{ backgroundColor: "white", color: "rgb(18,0,94)" }}
              >
                <h4 className="fw-bold">{startup.startupName}</h4>

                <p className="mb-1">
                  <strong>Registered:</strong> {startup.registeredName}
                </p>

                <p className="mb-1">
                  <strong>Incorporation:</strong> {startup.incorporationMonth}{" "}
                  {startup.incorporationYear}
                </p>

                <p className="mb-3">
                  <strong>About:</strong> {startup.about}
                </p>

                {/* ✅ Pitch Decks Section */}
                {startup.uploadedFiles && startup.uploadedFiles.length > 0 && (
                  <>
                    <hr />
                    <h6 className="fw-bold mb-3">Pitch Decks & Documents</h6>

                    {startup.uploadedFiles.map((file, index) => {
                      const previewLink = `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(
                        file.gcsUrl
                      )}`;

                      return (
                        <div key={index} className="mb-4">
                          <p className="fw-semibold">📄 {file.fileName}</p>

                          {/* ✅ Preview area */}
                          <iframe
                            src={previewLink}
                            style={{
                              width: "100%",
                              height: "420px",
                              border: "1px solid #ddd",
                              borderRadius: "6px",
                            }}
                            title={file.fileName}
                          ></iframe>

                          {/* ✅ Buttons */}
                          <div className="mt-2 d-flex gap-2">
                            <button
                              className="btn btn-sm"
                              style={{
                                backgroundColor: "rgb(18,0,94)",
                                color: "white",
                                fontWeight: "bold",
                                padding: "6px 16px",
                              }}
                              onClick={() => setPreviewUrl(previewLink)}
                            >
                              Preview
                            </button>

                            <a
                              href={file.gcsUrl}
                              download
                              className="btn btn-sm"
                              style={{
                                backgroundColor: "rgb(18,0,94)",
                                color: "white",
                                fontWeight: "bold",
                                padding: "6px 16px",
                              }}
                            >
                              Download
                            </a>
                          </div>
                        </div>
                      );
                    })}
                  </>
                )}

                {/* ✅ Generate Report Button */}
                <button
                  className="btn mt-2"
                  style={{
                    backgroundColor: "rgb(18,0,94)",
                    color: "white",
                    fontWeight: "bold",
                    width: "100%",
                    padding: "10px",
                    borderRadius: "10px",
                  }}
                  onClick={() => handleGenerateReport(startup)}
                >
                  Generate Report
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
};

export default InvestorDeals;
