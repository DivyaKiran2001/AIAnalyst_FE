import React, { useState, useEffect, useRef } from "react";
import io from "socket.io-client";

const SOCKET_SERVER_URL = "http://127.0.0.1:8000/"; // backend

const StartupQuestionnaire = ({ userEmail }) => {
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]); // chat history
  const [finalJson, setFinalJson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    const newSocket = io(SOCKET_SERVER_URL, {
      auth: { user_email: userEmail },
    });
    setSocket(newSocket);

    newSocket.on("connect", () => {
      console.log("Connected to backend:", newSocket.id);
    });

    newSocket.on("new_question", (data) => {
      console.log("📩 New Question:", data);
      setLoading(false);
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: data.text, key: data.key },
      ]);
      speakQuestion(data.text);
    });

    // newSocket.on("final_json", (filledJson) => {
    //   console.log("✅ Final JSON:", filledJson);
    //   setFinalJson(filledJson);
    //   setMessages((prev) => [
    //     ...prev,
    //     { from: "bot", text: "✅ All questions answered!" },
    //   ]);
    // });
    newSocket.on("final_json", (data) => {
      console.log("✅ Final status:", data);
      setFinalJson(data);
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "✅ Startup details updated successfully!" },
      ]);
      setTimeout(() => {
        navigate("/f-dashboard");
      }, 2000);
    });

    return () => {
      newSocket.disconnect();
    };
  }, [userEmail]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Speak question (TTS)
  const speakQuestion = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(utterance);
  };

  // Start listening (voice → text)
  const startListening = () => {
    if (
      !("webkitSpeechRecognition" in window || "SpeechRecognition" in window)
    ) {
      alert("Speech Recognition API not supported.");
      return;
    }
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      submitAnswer(transcript);
    };

    recognition.start();
  };

  // Submit answer
  const submitAnswer = (answer) => {
    if (!socket) return;
    const lastQuestion = messages.findLast((m) => m.from === "bot" && m.key);
    if (!lastQuestion) return;
    const startupName = sessionStorage.getItem("startupName"); // ✅ get startupName

    // Add user message
    setMessages((prev) => [...prev, { from: "user", text: answer }]);

    // Send to backend
    socket.emit("answer", {
      answer,
      user_email: userEmail,
      key: lastQuestion.key,
      startup_name: startupName,
    });
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: "0 auto",
        fontFamily: "Arial, sans-serif",
        display: "flex",
        flexDirection: "column",
        height: "80vh",
        border: "1px solid #ccc",
        borderRadius: 8,
        overflow: "hidden",
      }}
    >
      {/* Header */}
      <div style={{ padding: 10, background: "#007bff", color: "white" }}>
        <h3 style={{ margin: 0 }}>Startup Questionnaire</h3>
      </div>

      {/* Chat Window */}
      <div
        style={{
          flex: 1,
          padding: 15,
          overflowY: "auto",
          background: "#f9f9f9",
        }}
      >
        {loading && (
          <div style={{ textAlign: "center", padding: 20 }}>
            <div className="spinner"></div>
            <p>
              I noticed some important details are missing from your startup
              profile. I’m just preparing a few quick questions to complete your
              information — this will only take a moment!
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: "flex",
              justifyContent: msg.from === "user" ? "flex-end" : "flex-start",
              marginBottom: 10,
            }}
          >
            <div
              style={{
                padding: "10px 15px",
                borderRadius: 20,
                background: msg.from === "user" ? "#007bff" : "#e0e0e0",
                color: msg.from === "user" ? "white" : "black",
                maxWidth: "70%",
              }}
            >
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={chatEndRef}></div>
      </div>

      {/* Input */}
      {!finalJson && !loading && (
        <div style={{ padding: 10, display: "flex", gap: 10 }}>
          <input
            type="text"
            placeholder="Type your answer..."
            onKeyDown={(e) => {
              if (e.key === "Enter" && e.target.value.trim()) {
                submitAnswer(e.target.value);
                e.target.value = "";
              }
            }}
            style={{
              flex: 1,
              padding: 10,
              borderRadius: 20,
              border: "1px solid #ccc",
            }}
          />
          <button
            onClick={startListening}
            style={{
              borderRadius: "50%",
              width: 45,
              height: 45,
              border: "none",
              background: listening ? "red" : "#007bff",
              color: "white",
              cursor: "pointer",
            }}
          >
            🎤
          </button>
        </div>
      )}

      {/* Final JSON display */}
      {/*finalJson && (
        <div style={{ padding: 10, background: "#f1f1f1", maxHeight: "200px", overflow: "auto" }}>
          <h4>Final Startup Data</h4>
          <pre style={{ textAlign: "left" }}>
            {JSON.stringify(finalJson, null, 2)}
          </pre>
        </div>
      )*/}
      {finalJson && (
        <div
          style={{ padding: 20, textAlign: "center", background: "#e6ffe6" }}
        >
          <h3>✅ Startup details updated successfully!</h3>
        </div>
      )}
    </div>
  );
};

export default StartupQuestionnaire;
