// import React, { useEffect, useState } from "react";
// import "bootstrap/dist/css/bootstrap.min.css";
// import FounderNavbar from "./FounderNavbar";

// // const BACKEND_URL =
// //   "https://final-be-753168549263.us-central1.run.app";

// const BACKEND_URL = "https://final-be-753168549263.us-central1.run.app";

// const FounderStartups = () => {
//   const [startups, setStartups] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const founderEmail = sessionStorage.getItem("emailId");

//   useEffect(() => {
//     const fetchStartups = async () => {
//       try {
//         const res = await fetch(`${BACKEND_URL}/api/startups`);
//         const data = await res.json();
//         const myStartups = data.filter((s) => s.emailId === founderEmail);
//         setStartups(myStartups);
//       } catch (err) {
//         console.error("Error fetching startups:", err);
//       } finally {
//         setLoading(false);
//       }
//     };
//     fetchStartups();
//   }, [founderEmail]);

//   return (
//     <>
//       <FounderNavbar></FounderNavbar>
//       <div className="container py-5">
//         <h2 className="text-primary fw-bold mb-4 text-center">My Startups</h2>
//         <div className="card shadow-sm border-0 rounded-4 p-4">
//           {loading ? (
//             <p>Loading startups...</p>
//           ) : startups.length === 0 ? (
//             <p className="text-muted">No startups registered yet.</p>
//           ) : (
//             startups.map((startup) => (
//               <div
//                 key={startup._id}
//                 className="text-start mb-3 border-top pt-2"
//               >
//                 <h6 className="fw-bold">{startup.startupName}</h6>
//                 <p className="mb-1">
//                   <strong>Registered:</strong> {startup.registeredName}
//                 </p>
//                 <p className="mb-1">
//                   <strong>Incorporation:</strong> {startup.incorporationMonth}{" "}
//                   {startup.incorporationYear}
//                 </p>
//                 <p className="mb-0">
//                   <strong>About:</strong> {startup.about}
//                 </p>
//               </div>
//             ))
//           )}
//         </div>
//       </div>
//     </>
//   );
// };

// export default FounderStartups;

import React, { useEffect, useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import FounderNavbar from "./FounderNavbar";
import { Modal, Button } from "react-bootstrap";
import { getAuth, onAuthStateChanged } from "firebase/auth";

const BACKEND_URL = "https://final-be-753168549263.us-central1.run.app";

const FounderStartups = () => {
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);
  const founderEmail = sessionStorage.getItem("emailId");

  const [previewUrl, setPreviewUrl] = useState(null);

  // useEffect(() => {
  //   const fetchStartups = async () => {
  //     try {
  //       const res = await fetch(`${BACKEND_URL}/api/startup-details`);
  //       const data = await res.json();
  //       const myStartups = data.filter((s) => s.emailId === founderEmail);
  //       console.log(myStartups);
  //       setStartups(myStartups);
  //     } catch (err) {
  //       console.error("Error fetching startups:", err);
  //     } finally {
  //       setLoading(false);
  //     }
  //   };
  //   fetchStartups();
  // }, [founderEmail]);

  useEffect(() => {
    console.log("Session email:", founderEmail);
  }, [founderEmail]);

  useEffect(() => {
    const auth = getAuth();

    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (!user) {
        console.error("⚠ User not logged in");
        setLoading(false);
        return;
      }
      console.log(founderEmail);
      // sessionStorage.setItem("emailId", user.email);

      try {
        const token = await user.getIdToken(true);

        const res = await fetch(`${BACKEND_URL}/api/startup-details`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) throw new Error(`Failed to fetch startups: ${res.status}`);
        const data = await res.json();

        setStartups(data); // ✅ all startups for this user
      } catch (err) {
        console.error("Error fetching startups:", err);
      } finally {
        setLoading(false);
      }
    });

    // Cleanup on unmount
    return () => unsubscribe();
  }, []);

  return (
    <>
      <FounderNavbar />

      {/* Modal for PDF Preview */}
      <Modal
        show={!!previewUrl}
        onHide={() => setPreviewUrl(null)}
        size="xl"
        centered
      >
        <Modal.Header closeButton>
          <Modal.Title>Document Preview</Modal.Title>
        </Modal.Header>
        <Modal.Body style={{ height: "80vh" }}>
          <iframe
            src={previewUrl}
            width="100%"
            height="100%"
            style={{ border: "none" }}
            title="PDF Preview"
          ></iframe>
        </Modal.Body>
      </Modal>

      <div style={{ backgroundColor: "#f5f5f5", minHeight: "100vh" }}>
        <div className="container py-5">
          <h2
            className="fw-bold mb-4 text-center"
            style={{ color: "rgb(18,0,94)" }}
          >
            My Startups
          </h2>

          {loading ? (
            <p className="text-center">Loading startups...</p>
          ) : startups.length === 0 ? (
            <p className="text-muted text-center">
              No startups registered yet.
            </p>
          ) : (
            startups.map((startup) => (
              <div
                key={startup._id}
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

                {/* Uploaded Files Preview */}
                {startup.uploadedFiles && startup.uploadedFiles.length > 0 && (
                  <>
                    <hr />
                    <h6 className="fw-bold mb-3">Pitch Decks & Documents</h6>

                    {/* {startup.uploadedFiles.map((file, index) => {
                      const isPDF = file.fileName
                        .toLowerCase()
                        .endsWith(".pdf");
                      const previewUrl = isPDF
                        ? file.gcsUrl
                        : `https://drive.google.com/viewerng/viewer?embedded=true&url=${file.gcsUrl}`;
                      console.log(previewUrl);
                      return (
                        <div key={index} className="mb-4">
                          <p className="fw-semibold">📄 {file.fileName}</p>

                          <iframe
                            src={previewUrl}
                            style={{
                              width: "100%",
                              height: "420px",
                              border: "1px solid #ddd",
                              borderRadius: "6px",
                            }}
                            title={file.fileName}
                          ></iframe>

                          <div className="mt-2">
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
                    })} */}

                    {startup.uploadedFiles.map((file, index) => {
                      // Always force preview through Google Docs Viewer
                      const previewUrl = `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(
                        file.gcsUrl
                      )}`;

                      return (
                        <div key={index} className="mb-4">
                          <p className="fw-semibold">📄 {file.fileName}</p>

                          {/* Preview using Google Docs Viewer */}
                          <iframe
                            src={previewUrl}
                            style={{
                              width: "100%",
                              height: "420px",
                              border: "1px solid #ddd",
                              borderRadius: "6px",
                            }}
                            title={file.fileName}
                          ></iframe>

                          {/* Download Button */}
                          <div className="mt-2">
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
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
};

export default FounderStartups;
