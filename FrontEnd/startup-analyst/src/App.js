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

function App() {
  return (
    <Routes>
      <Route path="/" element={<SignupLP />} />
      <Route path="/signup" element={<Signup />} />
    </Routes>
  );
}

export default App;

