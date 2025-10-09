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
function App() {
  return (
    <Routes>
      <Route path="/" element={<SignupLP />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/founder-dashboard" element={<FounderDashboard/>}/>
      <Route path="/investor-dashboard" element={<InvestorDashboard/>}/>
      <Route path="/startup-registration" element={<StartupRegistration />} />
       {/* Chat Route */}
      <Route path="/chat" element={<ChatPage />} />
    </Routes>
  );
}

export default App;

