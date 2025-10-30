// import logo from './logo.svg';
// import './App.css';
// import Signup from './Signup';
// import SignupLP from './SignupLP';

// function App() {
//   return (
//   //  <Signup/>
//   <SignupLP/>
//   );
// }

// export default App;

import React from "react";
import { useState } from "react";
import StartupDocumentUploader from "./StartupDocumentUploader";
import StartupQuestionnaire from "./StartupQuestionnaire";
import { Routes, Route } from "react-router-dom";
import SignupLP from "./SignupLP";
import Signup from "./Signup";
import FounderDashboard from "./FounderDashboard";
import InvestorDashboard from "./InvestorDashboard";
import StartupRegistration from "./StartupRegistration";
import ChatPage from "./ChatPage";
import InvestorHome from "./InvestorHome";
import Fdashboard from "./Fdashboard";
import FounderMeetings from "./FounderMeetings";
import FounderRegistration from "./FounderRegistartion";
import FounderNavbar from "./FounderNavbar";
import FounderRequests from "./FounderRequests";
import FounderStartups from "./FounderStartups";
import InvestorDeals from "./InvestorDeals";
import GenerateReport from "./GenerateReport";
function App() {
  const [userEmail, setUserEmail] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUploadComplete = async (email) => {
    // Show spinner while backend prepares voice agent inputs
    setLoading(true);
    setUserEmail(email);

    // If you have an API to check status, call it here
    // await fetch(`/api/prepare-voice-agent?email=${email}`);

    // TEMP: Small spinner delay (2.5 secs)
    setTimeout(() => {
      setLoading(false);
    }, 2500);
  };

  // return (
  //   <>
  //     <Routes>
  //       {/* Landing & Auth */}
  //       <Route path="/" element={<SignupLP />} />
  //       <Route path="/signup" element={<Signup />} />

  //       {/* Founder Pages */}
  //       <Route path="/f-dashboard" element={<Fdashboard />} />
  //       <Route path="/founder-registration" element={<FounderRegistration />} />
  //       <Route path="/founder-startups" element={<FounderStartups />} />
  //       <Route path="/founder-requests" element={<FounderRequests />} />
  //       <Route path="/founder-meetings" element={<FounderMeetings />} />

  //       {/* Investor Pages */}
  //       <Route path="/investor-home" element={<InvestorHome />} />
  //       <Route path="/interested-meetings" element={<InvestorDashboard />} />
  //       <Route path="/startup-registration" element={<StartupRegistration />} />

  //       {/* Chat Page */}
  //       <Route path="/chat" element={<ChatPage />} />

  //       {/* ✅ Upload → Spinner → Voice Agent Flow */}
  //       <Route
  //         path="/upload"
  //         element={
  //           <div
  //             style={{
  //               fontFamily: "Arial, sans-serif",
  //               minHeight: "100vh",
  //               backgroundColor: "#F7F7F7",
  //             }}
  //           >
  //             {!userEmail ? (
  //               <StartupDocumentUploader
  //                 onUploadComplete={handleUploadComplete}
  //               />
  //             ) : loading ? (
  //               <div style={{ textAlign: "center", paddingTop: "120px" }}>
  //                 <div className="spinner" />
  //                 <p
  //                   style={{
  //                     marginTop: "16px",
  //                     fontSize: "18px",
  //                     color: "#333",
  //                   }}
  //                 >
  //                   Preparing your personalized voice questions...
  //                 </p>

  //                 <style>
  //                   {`
  //                   .spinner {
  //                     margin: 20px auto;
  //                     width: 60px;
  //                     height: 60px;
  //                     border: 7px solid #e0e0e0;
  //                     border-top: 7px solid #1A73E8;
  //                     border-radius: 50%;
  //                     animation: spin 1s linear infinite;
  //                   }

  //                   @keyframes spin {
  //                     0% { transform: rotate(0deg); }
  //                     100% { transform: rotate(360deg); }
  //                   }
  //                 `}
  //                 </style>
  //               </div>
  //             ) : (
  //               <StartupQuestionnaire userEmail={userEmail} />
  //             )}
  //           </div>
  //         }
  //       />
  //     </Routes>
  //   </>
  // );

  return (
    <Routes>
      {/* Landing & Auth */}
      <Route path="/" element={<SignupLP />} />
      <Route path="/signup" element={<Signup />} />

      {/* Founder Pages */}
      <Route path="/f-dashboard" element={<Fdashboard />} />
      <Route path="/founder-registration" element={<FounderRegistration />} />
      <Route path="/founder-startups" element={<FounderStartups />} />
      <Route path="/founder-requests" element={<FounderRequests />} />
      <Route path="/founder-meetings" element={<FounderMeetings />} />

      {/* Investor Pages */}
      <Route path="/investor-deals" element={<InvestorDeals />} />
      <Route path="/investor-home" element={<InvestorHome />} />
      <Route path="/interested-meetings" element={<InvestorDashboard />} />
      <Route path="/generate-report" element={<GenerateReport />} />

      {/* Startup Registration */}
      <Route path="/startup-registration" element={<StartupRegistration />} />

      {/* Chat Page */}
      <Route path="/chat" element={<ChatPage />} />
    </Routes>
  );

  // return (
  //   <>
  //     <div
  //       style={{
  //         fontFamily: "Arial, sans-serif",
  //         minHeight: "100vh",
  //         backgroundColor: "#F7F7F7",
  //       }}
  //     >
  //       {!userEmail ? (
  //         // Step 1: Upload Pitch Deck
  //         <StartupDocumentUploader onUploadComplete={handleUploadComplete} />
  //       ) : loading ? (
  //         // Step 2: Spinner (Preparing Voice Agent)
  //         <div style={{ textAlign: "center", paddingTop: "120px" }}>
  //           <div className="spinner" />
  //           <p style={{ marginTop: "16px", fontSize: "18px", color: "#333" }}>
  //             Preparing your personalized voice questions...
  //           </p>

  //           {/* Inline CSS for spinner */}
  //           <style>
  //             {`
  //             .spinner {
  //               margin: 20px auto;
  //               width: 60px;
  //               height: 60px;
  //               border: 7px solid #e0e0e0;
  //               border-top: 7px solid #1A73E8; /* Google Blue */
  //               border-radius: 50%;
  //               animation: spin 1s linear infinite;
  //             }

  //             @keyframes spin {
  //               0% { transform: rotate(0deg); }
  //               100% { transform: rotate(360deg); }
  //             }
  //           `}
  //           </style>
  //         </div>
  //       ) : (
  //         // Step 3: Voice Agent Questionnaire
  //         <StartupQuestionnaire userEmail={userEmail} />
  //       )}
  //     </div>
  //     <></>
  //     <Routes>
  //       <Route path="/" element={<SignupLP />} />
  //       <Route path="/signup" element={<Signup />} />
  //       <Route path="/f-dashboard" element={<Fdashboard />} />
  //       <Route path="/founder-registration" element={<FounderRegistration />} />
  //       <Route path="/founder-startups" element={<FounderStartups />} />
  //       <Route path="/founder-requests" element={<FounderRequests />} />
  //       <Route path="/founder-meetings" element={<FounderMeetings />} />
  //       {/* <Route path="/founder-dashboard" element={<FounderDashboard />} /> */}

  //       <Route path="/investor-home" element={<InvestorHome />} />
  //       <Route path="/interested-meetings" element={<InvestorDashboard />} />
  //       <Route path="/startup-registration" element={<StartupRegistration />} />
  //       {/* Chat Route */}
  //       <Route path="/chat" element={<ChatPage />} />
  //     </Routes>
  //   </>
  // );

  // return (
  //   <Routes>
  //     <Route path="/" element={<SignupLP />} />
  //     <Route path="/signup" element={<Signup />} />
  //     <Route path="/f-dashboard" element={<Fdashboard />} />
  //     <Route path="/founder-registration" element={<FounderRegistration />} />
  //     <Route path="/founder-startups" element={<FounderStartups />} />
  //     <Route path="/founder-requests" element={<FounderRequests />} />
  //     <Route path="/founder-meetings" element={<FounderMeetings />} />
  //     <Route path="/founder-dashboard" element={<FounderDashboard />} />

  //     <Route path="/investor-home" element={<InvestorHome />} />
  //     <Route path="/interested-meetings" element={<InvestorDashboard />} />
  //     <Route path="/startup-registration" element={<StartupRegistration />} />
  //     {/* Chat Route */}
  //     <Route path="/chat" element={<ChatPage />} />
  //   </Routes>
  // );
}

export default App;
