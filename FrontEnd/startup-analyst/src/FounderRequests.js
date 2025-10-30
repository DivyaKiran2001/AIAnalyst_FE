// import React, { useEffect, useState } from "react";
// import { useNavigate } from "react-router-dom";
// import "bootstrap/dist/css/bootstrap.min.css";
// import FounderNavbar from "./FounderNavbar";

// const BACKEND_URL = "http://localhost:8000";

// const FounderRequests = () => {
//   const navigate = useNavigate();
//   const [investorRequests, setInvestorRequests] = useState([]);
//   const founderEmail = sessionStorage.getItem("emailId");

//   useEffect(() => {
//     const fetchInvestorRequests = async () => {
//       try {
//         const res = await fetch(
//           `${BACKEND_URL}/api/founder/interested-investors?founderEmail=${founderEmail}`
//         );
//         const data = await res.json();
//         setInvestorRequests(data.investors || []);
//       } catch (err) {
//         console.error("Error fetching investor requests:", err);
//       }
//     };
//     if (founderEmail) fetchInvestorRequests();
//   }, [founderEmail]);

//   const handleChat = (investorEmail) => {
//     const participants = [founderEmail, investorEmail];
//     navigate("/chat", { state: { participants } });
//   };

//   const handleResponse = async (investorEmail, action) => {
//     try {
//       if (action === "accept") {
//         await fetch(`${BACKEND_URL}/api/interests/accept`, {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ founderEmail, investorEmail }),
//         });
//         alert("✅ Interest accepted. You can now chat with the investor.");
//       } else {
//         alert("❌ Request rejected.");
//       }

//       setInvestorRequests((prev) =>
//         prev.map((req) =>
//           req.investorEmail === investorEmail
//             ? { ...req, status: action === "accept" ? "accepted" : "rejected" }
//             : req
//         )
//       );
//     } catch (err) {
//       console.error("Error responding:", err);
//     }
//   };

//   return (
//     <><FounderNavbar></FounderNavbar><div className="container py-5">
//           <h2 className="text-success fw-bold mb-4 text-center">Investor Requests</h2>
//           <div className="card shadow-sm border-0 rounded-4 p-4">
//               {investorRequests.length === 0 ? (
//                   <p className="text-muted">No investor requests yet.</p>
//               ) : (
//                   investorRequests.map((req, index) => (
//                       <div key={index} className="text-start mb-3 border-top pt-2">
//                           <h6 className="fw-bold text-primary">{req.investorEmail}</h6>
//                           <p className="mb-1">
//                               <strong>Startup:</strong> {req.startupName}
//                           </p>
//                           <p className="mb-2">
//                               <strong>Status:</strong>{" "}
//                               <span
//                                   className={req.status === "accepted"
//                                       ? "text-success"
//                                       : req.status === "rejected"
//                                           ? "text-danger"
//                                           : "text-warning"}
//                               >
//                                   {req.status}
//                               </span>
//                           </p>

//                           {req.status === "pending" && (
//                               <div className="d-flex gap-2">
//                                   <button
//                                       className="btn btn-success btn-sm"
//                                       onClick={() => handleResponse(req.investorEmail, "accept")}
//                                   >
//                                       Accept
//                                   </button>
//                                   <button
//                                       className="btn btn-outline-danger btn-sm"
//                                       onClick={() => handleResponse(req.investorEmail, "reject")}
//                                   >
//                                       Reject
//                                   </button>
//                               </div>
//                           )}

//                           {req.status === "accepted" && (
//                               <button
//                                   className="btn btn-outline-primary btn-sm mt-2"
//                                   onClick={() => handleChat(req.investorEmail)}
//                               >
//                                   Chat
//                               </button>
//                           )}
//                       </div>
//                   ))
//               )}
//           </div>
//       </div></>
//   );
// };

// export default FounderRequests;
import React, { useEffect, useState, useRef } from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import FounderNavbar from "./FounderNavbar";
import io from "socket.io-client";

// const BACKEND_URL = "http://localhost:8000";
const BACKEND_URL = "http://localhost:8000";

const socket = io(BACKEND_URL, { transports: ["websocket", "polling"] });

const FounderRequests = () => {
  const [investorRequests, setInvestorRequests] = useState([]);
  const [selectedInvestor, setSelectedInvestor] = useState(null);
  const [selectedStartup, setSelectedStartup] = useState(null);

  const [chatMessages, setChatMessages] = useState([]);
  const [text, setText] = useState("");
  const chatEndRef = useRef(null);
  const founderEmail = sessionStorage.getItem("emailId");

  useEffect(() => {
    const fetchInvestorRequests = async () => {
      try {
        const res = await fetch(
          `${BACKEND_URL}/api/founder/interested-investors?founderEmail=${founderEmail}`
        );
        const data = await res.json();
        setInvestorRequests(data.investors || []);
      } catch (err) {
        console.error("Error fetching investor requests:", err);
      }
    };
    if (founderEmail) fetchInvestorRequests();
  }, [founderEmail]);

  // useEffect(() => {
  //   if (!selectedInvestor) return;
  //   const participants = [founderEmail, selectedInvestor].sort();

  //   socket.emit("join_room", { participants });

  //   fetch(
  //     `${BACKEND_URL}/api/chat/?participants=${participants
  //       .map(encodeURIComponent)
  //       .join("&participants=")}`
  //   )
  //     .then((res) => res.json())
  //     .then((data) => setChatMessages(data.messages || []))
  //     .catch((err) => console.error(err));

  //   // socket.on("receive_message", (msg) => {
  //   //   if (participants.includes(msg.senderId)) {
  //   //     setChatMessages((prev) => [...prev, msg]);
  //   //   }
  //   // });
  //   socket.on("receive_message", (msg) => {
  //     setChatMessages((prev) => [...prev, msg]);
  //   });

  //   return () => {
  //     socket.off("receive_message");
  //   };
  // }, [selectedInvestor, founderEmail]);
  useEffect(() => {
    if (!selectedInvestor || !selectedStartup) return;

    const participants = [founderEmail, selectedInvestor].sort();
    const roomId = `${participants.join("_")}_${selectedStartup}`; // ✅ unique per startup

    socket.emit("join_room", {
      roomId,
      participants,
      startupName: selectedStartup,
    });

    fetch(
      `${BACKEND_URL}/api/chat/?participants=${participants
        .map(encodeURIComponent)
        .join("&participants=")}&startupName=${encodeURIComponent(
        selectedStartup
      )}`
    )
      .then((res) => res.json())
      .then((data) => setChatMessages(data.messages || []))
      .catch((err) => console.error(err));

    socket.on("receive_message", (msg) => {
      if (msg.startupName === selectedStartup) {
        setChatMessages((prev) => [...prev, msg]);
      }
    });

    return () => {
      socket.off("receive_message");
    };
  }, [selectedInvestor, selectedStartup, founderEmail]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleResponse = async (investorEmail, action, startupName) => {
    try {
      if (action === "accept") {
        await fetch(`${BACKEND_URL}/api/interests/accept`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ founderEmail, investorEmail, startupName }),
        });
        alert("✅ Interest accepted. You can now chat with the investor.");
      } else {
        alert("❌ Request rejected.");
      }

      setInvestorRequests((prev) =>
        prev.map((req) =>
          req.investorEmail === investorEmail
            ? { ...req, status: action === "accept" ? "accepted" : "rejected" }
            : req
        )
      );
    } catch (err) {
      console.error("Error responding:", err);
    }
  };

  const sendMessage = () => {
    if (!text.trim() || !selectedInvestor) return;
    const msg = {
      senderId: founderEmail,
      text,
      timestamp: new Date().toISOString(),
      participants: [founderEmail, selectedInvestor].sort(),
      startupName: selectedStartup, // ✅ include startup
    };
    socket.emit("send_message", msg);
    setChatMessages((prev) => [...prev, msg]);
    setText("");
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString("en-US", {
      hour12: true,
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "Asia/Kolkata",
    });
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString("en-US", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      timeZone: "Asia/Kolkata",
    });
  };

  const groupedMessages = chatMessages.reduce((acc, msg) => {
    const date = formatDate(msg.timestamp);
    if (!acc[date]) acc[date] = [];
    acc[date].push(msg);
    return acc;
  }, {});

  const acceptedInvestors = investorRequests.filter(
    (r) => r.status === "accepted"
  );
  const pendingInvestors = investorRequests.filter(
    (r) => r.status === "pending"
  );

  return (
    <>
      <FounderNavbar />
      <div
        style={{
          backgroundColor: "#f0f0f0",
          minHeight: "100vh",
          padding: "2rem 0",
        }}
      >
        <div className="container d-flex" style={{ maxWidth: "1200px" }}>
          {/* Left: Investor Requests */}
          <div
            className="col-4 pe-2"
            style={{ maxHeight: "80vh", overflowY: "auto" }}
          >
            <h4 className="mb-3 text-center" style={{ color: "rgb(18,0,94)" }}>
              Chats
            </h4>
            {/* Accepted investors */}
            {acceptedInvestors.length === 0 ? (
              <p className="text-center text-muted">No accepted investors</p>
            ) : (
              acceptedInvestors.map((req, index) => (
                <div
                  key={index}
                  className={`mb-3 p-3 rounded-4 shadow-sm d-flex justify-content-between align-items-center`}
                  style={{
                    backgroundColor: "#fff",
                    color: "rgb(18,0,94)",
                    cursor: "pointer",
                  }}
                  onClick={() => {
                    setSelectedInvestor(req.investorEmail);
                    setSelectedStartup(req.startupName); // ✅ capture startup name
                  }}
                >
                  <div>
                    <h6 className="mb-1 fw-bold">{req.investorEmail}</h6>
                    <p
                      className="mb-0 text-truncate"
                      style={{ maxWidth: "180px" }}
                    >
                      {req.startupName}
                    </p>
                  </div>
                  <span style={{ color: "rgb(18,0,94)", fontWeight: "bold" }}>
                    Chat
                  </span>
                </div>
              ))
            )}

            {/* Pending investors */}
            {pendingInvestors.length > 0 && (
              <>
                <h5
                  className="mt-4 mb-2 text-center"
                  style={{ color: "rgb(18,0,94)" }}
                >
                  Pending Requests
                </h5>
                {pendingInvestors.map((req, index) => (
                  <div
                    key={index}
                    className={`mb-3 p-3 rounded-4 shadow-sm d-flex justify-content-between align-items-center`}
                    style={{ backgroundColor: "#fff", color: "rgb(18,0,94)" }}
                  >
                    <div>
                      <h6 className="mb-1 fw-bold">{req.investorEmail}</h6>
                      <p
                        className="mb-0 text-truncate"
                        style={{ maxWidth: "180px" }}
                      >
                        {req.startupName}
                      </p>
                    </div>
                    <div className="d-flex gap-1 flex-column">
                      <button
                        className="btn btn-success btn-sm"
                        onClick={() =>
                          handleResponse(
                            req.investorEmail,
                            "accept",
                            req.startupName
                          )
                        }
                      >
                        Accept
                      </button>
                      <button
                        className="btn btn-outline-danger btn-sm"
                        onClick={() =>
                          handleResponse(
                            req.investorEmail,
                            "reject",
                            req.startupName
                          )
                        }
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>

          {/* Right: Chat Window */}
          <div
            className="col-8 ps-2 d-flex flex-column"
            style={{
              maxHeight: "80vh",
              backgroundColor: "#fff",
              borderRadius: "12px",
              padding: "1rem",
            }}
          >
            {selectedInvestor ? (
              <>
                {/* <h5
                  className="text-center mb-3 fw-bold"
                  style={{ color: "rgb(18,0,94)" }}
                >
                  {selectedInvestor}
                </h5> */}
                <h5 className="text-center mb-3 fw-bold">
                  {selectedInvestor} —{" "}
                  <span style={{ color: "#666" }}>{selectedStartup}</span>
                </h5>

                <div
                  style={{
                    flexGrow: 1,
                    overflowY: "auto",
                    padding: "0 0.5rem",
                  }}
                >
                  {Object.keys(groupedMessages).map((date) => (
                    <div key={date} className="mb-3">
                      <div className="text-center my-2">
                        <span className="badge bg-secondary">{date}</span>
                      </div>
                      {/* {groupedMessages[date].map((msg, i) => (
                        <div key={i} className={`d-flex mb-2 ${msg.senderId === founderEmail ? "justify-content-end" : "justify-content-start"}`}>
                          <div
                            className="p-2 rounded-3 shadow-sm"
                            style={{
                              maxWidth: "70%",
                              backgroundColor: msg.senderId === founderEmail ? "#0d6efd" : "#e4e6eb",
                              color: msg.senderId === founderEmail ? "#fff" : "#000"
                            }}
                          >
                            <p className="mb-1">{msg.text}</p>
                            <small className="text-muted float-end">{formatTime(msg.timestamp)}</small>
                          </div>
                        </div>
                      ))} */}

                      {groupedMessages[date].map((msg, i) => (
                        <div
                          key={i}
                          className={`d-flex mb-2 ${
                            msg.senderId === founderEmail
                              ? "justify-content-end"
                              : "justify-content-start"
                          }`}
                        >
                          <div
                            className="p-2 rounded-3 shadow-sm"
                            style={{
                              maxWidth: "70%",
                              backgroundColor:
                                msg.senderId === founderEmail
                                  ? "rgb(18,0,94)"
                                  : "#e4e6eb",
                              color:
                                msg.senderId === founderEmail ? "#fff" : "#000",
                            }}
                          >
                            <p className="mb-1">{msg.text}</p>
                            <small className="text-muted float-end">
                              {formatTime(msg.timestamp)}
                            </small>
                          </div>
                        </div>
                      ))}
                    </div>
                  ))}
                  <div ref={chatEndRef} />
                </div>
                <div className="input-group mt-2">
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Type a message..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                  />
                  <button
                    className="btn"
                    style={{ backgroundColor: "rgb(18,0,94)", color: "#fff" }}
                    onClick={sendMessage}
                  >
                    Send
                  </button>
                </div>
              </>
            ) : (
              <div className="d-flex justify-content-center align-items-center flex-grow-1">
                <p className="text-muted">Select an investor to chat</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default FounderRequests;
