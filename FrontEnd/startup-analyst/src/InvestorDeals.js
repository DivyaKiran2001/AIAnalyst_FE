import React, { useEffect, useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import InvestorNavbar from "./InvestorNavbar";
import { Modal } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { FaFilePdf, FaDownload, FaChartLine } from "react-icons/fa";
import DealsFilter from "./DealsFilter";

const BACKEND_URL = "https://final-be-753168549263.us-central1.run.app";

const InvestorDeals = () => {
  const [startups, setStartups] = useState([]);
  const [filteredStartups, setFilteredStartups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [selectedSector, setSelectedSector] = useState("");
  const [selectedWeightage, setSelectedWeightage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchStartups = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/startups`);
        const data = await res.json();
        setStartups(data);
        setFilteredStartups(data);
      } catch (err) {
        console.error("Error fetching startups:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchStartups();
  }, []);
  console.log(filteredStartups);

  //   // Filter and sort startups based on selections
  //   useEffect(() => {
  //     let result = [...startups];

  //     // Filter by sector
  //     if (selectedSector) {
  //       result = result.filter((startup) => {
  //         const startupSector =
  //           startup.first_memo?.investment_memo?.executive_summary?.sector;
  //         return startupSector === selectedSector;
  //       });
  //     }

  //     // Sort by weightage
  //     if (selectedWeightage) {
  //       result.sort((a, b) => {
  //         let scoreA, scoreB;

  //         switch (selectedWeightage) {
  //           case "financials":
  //             scoreA =
  //               parseFloat(
  //                 a.first_memo?.investment_memo?.financial_highlights?.score
  //               ) || 0;
  //             scoreB =
  //               parseFloat(
  //                 b.first_memo?.investment_memo?.financial_highlights?.score
  //               ) || 0;
  //             break;
  //           case "team":
  //             scoreA =
  //               parseFloat(
  //                 a.first_memo?.investment_memo?.team_highlights?.score
  //               ) || 0;
  //             scoreB =
  //               parseFloat(
  //                 b.first_memo?.investment_memo?.team_highlights?.score
  //               ) || 0;
  //             break;
  //           case "market":
  //             const confidenceA =
  //               a.first_memo?.investment_memo?.market_highlights
  //                 ?.validation_confidence || "0%";
  //             const confidenceB =
  //               b.first_memo?.investment_memo?.market_highlights
  //                 ?.validation_confidence || "0%";
  //             scoreA = parseFloat(confidenceA.replace("%", "")) || 0;
  //             scoreB = parseFloat(confidenceB.replace("%", "")) || 0;
  //             break;
  //           default:
  //             return 0;
  //         }

  //         return scoreB - scoreA; // Descending order (highest first)
  //       });
  //     }

  //     setFilteredStartups(result);
  //   }, [selectedSector, selectedWeightage, startups]);
  useEffect(() => {
    let result = [...startups];
    console.log("Result", result);

    // Safely parse first_memo if it's a JSON string
    const parseMemo = (memo) => {
      try {
        return typeof memo === "string" ? JSON.parse(memo) : memo;
      } catch (error) {
        console.error("Error parsing first_memo:", error);
        return null;
      }
    };

    // Filter by sector
    if (selectedSector) {
      result = result.filter((startup) => {
        const parsedMemo = parseMemo(startup?.bigqueryData?.first_memo);
        const startupSector =
          parsedMemo?.investment_memo?.executive_summary?.sector;
        return startupSector === selectedSector;
      });
    }

    // Sort by selected weightage
    if (selectedWeightage) {
      result.sort((a, b) => {
        const memoA = parseMemo(a?.bigqueryData?.first_memo);
        const memoB = parseMemo(b?.bigqueryData?.first_memo);

        let scoreA = 0;
        let scoreB = 0;

        switch (selectedWeightage) {
          case "financials":
            scoreA =
              parseFloat(memoA?.investment_memo?.financial_highlights?.score) ||
              0;
            scoreB =
              parseFloat(memoB?.investment_memo?.financial_highlights?.score) ||
              0;
            break;

          case "team":
            scoreA =
              parseFloat(memoA?.investment_memo?.team_highlights?.score) || 0;
            scoreB =
              parseFloat(memoB?.investment_memo?.team_highlights?.score) || 0;
            break;

          case "market":
            const confidenceA =
              memoA?.investment_memo?.market_highlights
                ?.validation_confidence || "0%";
            const confidenceB =
              memoB?.investment_memo?.market_highlights
                ?.validation_confidence || "0%";
            scoreA = parseFloat(confidenceA.replace("%", "")) || 0;
            scoreB = parseFloat(confidenceB.replace("%", "")) || 0;
            break;

          default:
            return 0;
        }

        return scoreB - scoreA; // Descending order
      });
    }

    setFilteredStartups(result);
  }, [selectedSector, selectedWeightage, startups]);

  //   const handleGenerateReport = (startup) => {
  //     navigate("/generate-report", { state: { startup } });
  //   };

  // ✅ Send selected startup’s identifying info
  const handleGenerateReport = (startup) => {
    navigate("/generate-report", {
      state: {
        emailId: startup.emailId,
        startupName: startup.startupName,
      },
    });
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

      <div
        className="d-flex justify-content-center"
        style={{
          backgroundColor: "#f0f2f5",
          minHeight: "100vh",
          padding: "40px 0",
        }}
      >
        <div style={{ width: "90%", maxWidth: "850px" }}>
          <h2
            className="fw-bold text-center mb-5"
            style={{ color: "rgb(18,0,94)" }}
          >
            🚀 Discover Promising Startup Deals
          </h2>

          {/* Add the Filter Component */}
          <DealsFilter
            selectedSector={selectedSector}
            setSelectedSector={setSelectedSector}
            selectedWeightage={selectedWeightage}
            setSelectedWeightage={setSelectedWeightage}
          />
          {loading ? (
            <p className="text-center text-muted">Loading startups...</p>
          ) : filteredStartups.length === 0 ? (
            <p className="text-center text-muted">
              No startup deals available yet.
            </p>
          ) : (
            filteredStartups.map((startup, index) => (
              <div
                key={index}
                className="card shadow-sm border-0 mb-5 rounded-4"
                style={{
                  backgroundColor: "white",
                  overflow: "hidden",
                  transition: "all 0.3s ease-in-out",
                }}
              >
                {/* Header - Like a Facebook post */}
                <div className="d-flex align-items-center p-3 border-bottom">
                  <img
                    src={`https://ui-avatars.com/api/?name=${startup.startupName}&background=18,0,94&color=fff`}
                    alt="Startup Avatar"
                    className="rounded-circle me-3"
                    width="55"
                    height="55"
                  />
                  <div>
                    <h5
                      className="fw-bold mb-0"
                      style={{ color: "rgb(18,0,94)" }}
                    >
                      {startup.startupName}
                    </h5>
                    {(() => {
                      try {
                        // Parse the JSON string inside first_memo
                        const memo =
                          typeof startup?.bigqueryData?.first_memo === "string"
                            ? JSON.parse(startup.bigqueryData.first_memo)
                            : startup?.bigqueryData?.first_memo;

                        const sector =
                          memo?.investment_memo?.executive_summary?.sector;

                        return (
                          sector && (
                            <p className="mb-1">
                              <strong>Sector:</strong> {sector}
                            </p>
                          )
                        );
                      } catch (err) {
                        console.error("Error parsing first_memo:", err);
                        return null;
                      }
                    })()}

                    {/* {startup?.bigqueryData.first_memo?.investment_memo
                      ?.executive_summary?.sector && (
                      <p className="mb-1">
                        <strong>Sector:</strong>{" "}
                        {
                          startup?.bigqueryData.first_memo?.investment_memo
                            ?.executive_summary?.sector
                        }
                      </p>
                    )} */}
                    <small className="text-muted">
                      Founded in {startup.incorporationMonth}{" "}
                      {startup.incorporationYear}
                    </small>
                  </div>
                </div>

                {/* Body */}
                <div className="card-body" style={{ color: "#333" }}>
                  <p className="fw-semibold mb-2">
                    <strong>Registered Name:</strong> {startup.registeredName}
                  </p>
                  <p className="mb-3">{startup.about}</p>

                  {/* Pitch Decks Section */}
                  {startup.uploadedFiles &&
                    startup.uploadedFiles.length > 0 && (
                      <div className="mt-3">
                        <h6 className="fw-bold mb-3 text-secondary">
                          <FaFilePdf className="me-2 text-danger" />
                          Pitch Decks & Documents
                        </h6>

                        {startup.uploadedFiles.map((file, i) => {
                          const previewLink = `https://docs.google.com/gview?embedded=true&url=${encodeURIComponent(
                            file.gcsUrl
                          )}`;
                          return (
                            <div
                              key={i}
                              className="mb-3 border rounded-3 p-3"
                              style={{
                                backgroundColor: "#fafafa",
                              }}
                            >
                              <div className="d-flex justify-content-between align-items-center mb-2">
                                <span className="fw-semibold text-dark">
                                  📄 {file.fileName}
                                </span>
                                <div className="d-flex gap-2">
                                  <button
                                    className="btn btn-sm"
                                    style={{
                                      backgroundColor: "rgb(18,0,94)",
                                      color: "white",
                                      fontWeight: "bold",
                                      borderRadius: "8px",
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
                                      borderRadius: "8px",
                                    }}
                                  >
                                    <FaDownload className="me-1" /> Download
                                  </a>
                                </div>
                              </div>

                              <iframe
                                src={previewLink}
                                style={{
                                  width: "100%",
                                  height: "400px",
                                  border: "1px solid #ddd",
                                  borderRadius: "6px",
                                }}
                                title={file.fileName}
                              ></iframe>
                            </div>
                          );
                        })}
                      </div>
                    )}
                </div>

                {/* Footer / Action Buttons */}
                <div
                  className="card-footer bg-white border-top text-center"
                  style={{
                    padding: "16px 0",
                  }}
                >
                  <button
                    className="btn btn-lg px-4"
                    style={{
                      backgroundColor: "rgb(18,0,94)",
                      color: "white",
                      fontWeight: "bold",
                      borderRadius: "12px",
                    }}
                    onClick={() => handleGenerateReport(startup)}
                  >
                    <FaChartLine className="me-2" />
                    Generate Investment Report
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
};

export default InvestorDeals;
