

import React, { useEffect, useState, useRef } from "react";
import { useLocation } from "react-router-dom";
import io from "socket.io-client";

const socket = io("https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io", {
  transports: ["websocket", "polling"]
});

const ChatPage = () => {
  const location = useLocation();
  const participants = location.state?.participants || [];
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const senderId = sessionStorage.getItem("emailId");
  const chatEndRef = useRef(null);

  // Auto-scroll on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (!participants.length) return;

    socket.emit("join_room", { participants });
    console.log(Intl.DateTimeFormat().resolvedOptions());


    // Fetch chat history
    fetch(`https://8000-divyakiran2-aianalystfe-trzzh46bbrz.ws-us121.gitpod.io/api/chat/?participants=${participants.map(encodeURIComponent).join("&participants=")}`)
      .then(res => res.json())
      .then(data => setMessages(data.messages || []))
      .catch(err => console.error(err));

    socket.on("receive_message", (msg) => {
      setMessages(prev => [...prev, msg]);
    });

    return () => {
      socket.off("receive_message");
    };
  }, [participants]);

  const sendMessage = () => {
    if (!text.trim()) return;
    const msg = { senderId, text, timestamp: new Date().toISOString(), participants };
    socket.emit("send_message", msg);
    setMessages(prev => [...prev, msg]); // Optimistic UI
    setText("");
  };

  // Helpers
  // const formatTime = (timestamp) => new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  // const formatDate = (timestamp) => new Date(timestamp).toLocaleDateString();

  const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour12: true,
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "Asia/Kolkata" // Forces India Standard Time
  });
};

const formatDate = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleDateString("en-US", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    timeZone: "Asia/Kolkata"
  });
};

  // Group messages by date
  const groupedMessages = messages.reduce((acc, msg) => {
    console.log(msg.timestamp); 
console.log(new Date(msg.timestamp).toLocaleTimeString("en-IN", { hour12: true, hour: "2-digit", minute: "2-digit", timeZone: "Asia/Calcutta" }));

    const date = formatDate(msg.timestamp);
    if (!acc[date]) acc[date] = [];
    acc[date].push(msg);
    return acc;
  }, {});

  return (
    <div className="container mt-4" style={{ maxWidth: "600px" }}>
      <h3 className="text-center mb-3">Chat</h3>

      {/* Chat Area */}
      <div className="border rounded p-3 mb-3" style={{ height: "500px", overflowY: "auto", backgroundColor: "#f0f2f5" }}>
        {Object.keys(groupedMessages).map((date) => (
          <div key={date} className="mb-3">
            {/* Date Separator */}
            <div className="text-center my-3">
              <span className="badge bg-secondary">{date}</span>
            </div>

            {groupedMessages[date].map((msg, i) => (
              <div
                key={i}
                className={`d-flex mb-2 ${msg.senderId === senderId ? "justify-content-end" : "justify-content-start"}`}
              >
                <div
                  className={`p-2 rounded-3 shadow-sm`}
                  style={{
                    maxWidth: "75%",
                    backgroundColor: msg.senderId === senderId ? "#0d6efd" : "#e4e6eb",
                    color: msg.senderId === senderId ? "white" : "black"
                  }}
                >
                  <p className="mb-1">{msg.text}</p>
                  <small className="text-muted float-end">{formatTime(msg.timestamp)}</small>
                </div>
              </div>
            ))}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-group">
        <input
          type="text"
          className="form-control"
          placeholder="Type a message..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button className="btn btn-primary" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
