// import React, { useState } from "react";
// import { useNavigate, useLocation } from "react-router-dom";
// import { auth, signUpWithEmail, signInWithGoogle,loginInWithEmail } from "./firebase";
// import "bootstrap/dist/css/bootstrap.min.css";
// import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import { faGoogle } from "@fortawesome/free-brands-svg-icons";

// const AuthPage = () => {
//   const location = useLocation();
//   const role = location.state?.role || ""; // passed from previous page
//   const navigate = useNavigate();

//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [isLogin, setIsLogin] = useState(false); // toggle between login/signup

//   const handleEmailAuth = async () => {
//     try {
//       let result;
//       if (isLogin) {
//         // Firebase login
//         result = await loginInWithEmail(email, password);
//       } else {
//         // Firebase signup
//         result = await signUpWithEmail(email, password);
//       }

//       const token = await result.user.getIdToken(true);

//       const res = await fetch("https://8000-genaihackat-aianalystfe-hgc0ltv9os0.ws-us121.gitpod.io/api/auth", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           Authorization: `Bearer ${token}`,
//         },
//         body: JSON.stringify({
//           email,
//           password: isLogin ? null : password,
//           role,
//         }),
//       });

//       const data = await res.json();

//       console.log("Auth success:", data);

//       // Redirect based on role
//       if (data.user.role === "founder") navigate("/founder-dashboard");
//       else if (data.user.role === "investor") navigate("/investor-dashboard");

//     } catch (err) {
//       console.error(err);
//       alert(err.message);
//     }
//   };

//   const handleGoogleAuth = async () => {
//     try {
//       const result = await signInWithGoogle();
//       const user = result.user;
//       const token = await user.getIdToken();

//       const res = await fetch("https://8000-genaihackat-aianalystfe-hgc0ltv9os0.ws-us121.gitpod.io/api/auth", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           Authorization: `Bearer ${token}`,
//         },
//         body: JSON.stringify({
//           email: user.email,
//           password: null,
//           role,
//         }),
//       });

//       const data = await res.json();

//       // Redirect based on role
//       if (data.user.role === "founder") navigate("/founder-dashboard");
//       else if (data.user.role === "investor") navigate("/investor-dashboard");

//     } catch (error) {
//       console.error(error);
//       alert(error.message);
//     }
//   };

//   return (
//     <div className="d-flex justify-content-center align-items-center vh-100 bg-primary">
//       <div className="bg-dark p-4 rounded shadow-lg text-white" style={{ width: '100%', maxWidth: '400px' }}>
//         <h2 className="text-center mb-3">{isLogin ? "Log In" : "Create Your Account"}</h2>
//         <p className="text-center mb-4">{isLogin ? "Welcome back!" : "Sign up to LVX to continue to LVX-web."}</p>

//         {/* Email Field */}
//         <div className="mb-3">
//           <input
//             className="form-control"
//             type="email"
//             placeholder="Email address"
//             onChange={(e) => setEmail(e.target.value)}
//           />
//         </div>

//         {/* Password Field */}
//         <div className="mb-3">
//           <input
//             className="form-control"
//             type="password"
//             placeholder="Password"
//             onChange={(e) => setPassword(e.target.value)}
//           />
//         </div>

//         {/* Email Signup/Login Button */}
//         <button className="btn btn-lg btn-primary w-100 mb-3" onClick={handleEmailAuth}>
//           {isLogin ? "Log In" : "Continue"}
//         </button>

//         <hr className="my-4" />

//         {/* Google Signup/Login Button */}
//         <button className="btn btn-lg btn-outline-danger w-100 mb-3" onClick={handleGoogleAuth}>
//           <FontAwesomeIcon icon={faGoogle} className="me-2" /> Continue with Google
//         </button>

//         <div className="text-center mt-3">
//           {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
//           <span className="text-danger" style={{ cursor: "pointer" }} onClick={() => setIsLogin(!isLogin)}>
//             {isLogin ? "Sign Up" : "Log In"}
//           </span>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default AuthPage;

import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  auth,
  signUpWithEmail,
  loginInWithEmail,
  signInWithGoogle,
  sendVerificationEmail,
} from "./firebase";
import "bootstrap/dist/css/bootstrap.min.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGoogle } from "@fortawesome/free-brands-svg-icons";

const AuthPage = () => {
  const location = useLocation();
  // const role = location.state?.role || "";
  // passed from previous page
  const role =
    location.state?.role || sessionStorage.getItem("selectedRole") || "";

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLogin, setIsLogin] = useState(false); // toggle between login/signup

  // -------------------- EMAIL SIGNUP / LOGIN --------------------
  const handleEmailAuth = async () => {
    try {
      // ✅ Save role in sessionStorage before doing anything
      sessionStorage.setItem("selectedRole", role);
      let result;

      if (isLogin) {
        // LOGIN

        result = await loginInWithEmail(email, password);

        if (!result.user.emailVerified) {
          alert("Please verify your email before logging in.");
          return;
        }
      } else {
        // SIGNUP
        result = await signUpWithEmail(email, password);

        // Send verification email
        await sendVerificationEmail(result.user, {
          url: "https://3000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev/signup", // redirect after verification
        });

        alert(
          `Verification email sent to ${email}. Please verify before logging in.`
        );

        // Optionally, you can prevent auto-login until verified
        return;
      }

      const token = await result.user.getIdToken(true);

      const res = await fetch(
        "https://final-be-753168549263.us-central1.run.app/api/auth",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            email,
            password,
            role,
          }),
        }
      );

      const data = await res.json();
      sessionStorage.setItem("emailId", data.user.email);

      // Redirect based on role
      if (data.user.role === "founder") navigate("/founder-registration");
      else if (data.user.role === "investor") navigate("/investor-deals");
    } catch (err) {
      console.error(err);
      alert(err.message);
    }
  };

  // -------------------- GOOGLE LOGIN --------------------
  const handleGoogleAuth = async () => {
    try {
      const result = await signInWithGoogle(auth);
      const user = result.user;

      const token = await user.getIdToken(true);

      const res = await fetch(
        "https://final-be-753168549263.us-central1.run.app/api/auth",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            email: user.email,
            password: null,
            role,
          }),
        }
      );

      const data = await res.json();
      // ✅ Store user details before navigating
      sessionStorage.setItem("emailId", data.user.email);

      // Redirect based on role
      if (data.user.role === "founder") navigate("/founder-registration");
      else if (data.user.role === "investor") navigate("/investor-deals");
    } catch (error) {
      console.error(error);
      alert(error.message);
    }
  };

  return (
    <div
      className="d-flex justify-content-center align-items-center vh-100"
      style={{
        backgroundImage: "url('/images/bg.jpg')",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
      }}
    >
      <div
        className="bg-light p-4 rounded shadow-lg"
        style={{ width: "100%", maxWidth: "400px" }}
      >
        {/* ✅ Logo Section */}
        <div className="text-center mb-4">
          <img
            src="https://d1y839zkxnw8vi.cloudfront.net/public/LVX_Final_logo/LV_Primary_RAW.svg"
            alt="LVX Logo"
            style={{ width: "120px", height: "auto" }}
          />
        </div>
        <h2 className="text-center mb-3">
          {isLogin ? "Log In" : "Create Your Account"}
        </h2>
        <p className="text-center mb-4">
          {isLogin ? "Welcome back!" : "Sign up to continue to LVX-web."}
        </p>

        {/* Email Field */}
        <div className="mb-3">
          <input
            className="form-control"
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        {/* Password Field */}
        <div className="mb-3">
          <input
            className="form-control"
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {/* Email Auth Button */}
        <button
          className="btn btn-lg btn-primary w-100 mb-3"
          onClick={handleEmailAuth}
        >
          {isLogin ? "Log In" : "Continue"}
        </button>

        <hr className="my-4" />

        {/* Google Login Button */}
        <button
          className="btn btn-lg btn-outline-danger w-100 mb-3"
          onClick={handleGoogleAuth}
        >
          <FontAwesomeIcon icon={faGoogle} className="me-2" /> Continue with
          Google
        </button>

        {/* Toggle Login/Signup */}
        <div className="text-center mt-3">
          {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
          <span
            className="text-danger"
            style={{ cursor: "pointer" }}
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? "Sign Up" : "Log In"}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AuthPage;
