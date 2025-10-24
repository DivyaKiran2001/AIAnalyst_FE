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
function App() {
  return (
    <Routes>
      <Route path="/" element={<SignupLP />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/f-dashboard" element={<Fdashboard/>}/>
      <Route path="/founder-registration" element={<FounderRegistration />} />
      <Route path="/founder-startups" element={<FounderStartups />} />
      <Route path="/founder-requests" element={<FounderRequests />} />
      <Route path="/founder-meetings" element={<FounderMeetings />} />
      <Route path="/founder-dashboard" element={<FounderDashboard/>}/>
     
      <Route path="/investor-home" element={<InvestorHome/>}/>
      <Route path="/interested-meetings" element={<InvestorDashboard/>}/>
      <Route path="/startup-registration" element={<StartupRegistration />} />
       {/* Chat Route */}
      <Route path="/chat" element={<ChatPage />} />
    </Routes>
  );
}

export default App;

