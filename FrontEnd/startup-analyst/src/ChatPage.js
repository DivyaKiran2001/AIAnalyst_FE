import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import io from "socket.io-client";

const socket = io("http://localhost:8000"); // replace with backend URL

const ChatPage = () => {
  const location = useLocation();
  const { participants } = location.state;
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const senderId = localStorage.getItem("userEmail");

  useEffect(() => {
    socket.emit("join_room", { participants });

    // fetch chat history
    fetch(`http://localhost:8000/api/chat/?participants=${participants.join("&participants=")}`)
      .then(res => res.json())
      .then(data => setMessages(data.messages));

    socket.on("receive_message", (msg) => {
      setMessages(prev => [...prev, msg]);
    });

    return () => {
      socket.off("receive_message");
    };
  }, [participants]);

  const sendMessage = () => {
    if (!text) return;
    socket.emit("send_message", { senderId, text, participants });
    setText("");
  };

  return (
    <div className="container mt-5">
      <h3>Chat</h3>
      <div className="border p-3 mb-3" style={{ height: "400px", overflowY: "scroll" }}>
        {messages.map((msg, i) => (
          <div key={i} className={`mb-2 ${msg.senderId === senderId ? "text-end" : "text-start"}`}>
            <span className="badge bg-primary">{msg.senderId}</span>
            <p>{msg.text}</p>
            <small>{new Date(msg.timestamp).toLocaleString()}</small>
          </div>
        ))}
      </div>
      <div className="d-flex">
        <input className="form-control me-2" value={text} onChange={e => setText(e.target.value)} placeholder="Type a message..." />
        <button className="btn btn-success" onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
};

export default ChatPage;
