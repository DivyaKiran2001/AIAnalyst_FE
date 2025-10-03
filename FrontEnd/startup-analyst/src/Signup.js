import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import { auth, signUpWithEmail, signInWithGoogle } from "./firebase";
import "bootstrap/dist/css/bootstrap.min.css"; // Importing Bootstrap CSS
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGoogle } from "@fortawesome/free-brands-svg-icons"; // Import Google icon from FontAwesome

const Signup = () => {
  const location = useLocation();
  const role = location.state?.role || ""; // "investor" or "founder"

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  useEffect(() => {
    if (role) {
      console.log("User Role:", role);
    }
  }, [role]);

  const handleEmailSignup = async () => {
    try {
      const result = await signUpWithEmail(email, password);
      const token = await result.user.getIdToken(true);

      await fetch("https://8000-genaihackat-aianalystfe-o07n93pd4xm.ws-us121.gitpod.io/api/auth", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json", 
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ email, password, role }),
      });

      console.log("Signed up:", result.user);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGoogleSignup = async () => {
    try {
      const result = await signInWithGoogle();
      const user = result.user;
      const token = await user.getIdToken();

      await fetch("https://8000-genaihackat-aianalystfe-o07n93pd4xm.ws-us121.gitpod.io/api/auth", {
        method: "POST",
        headers: { 
          "Content-Type": "application/json", 
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ 
          email: user.email,
          password: null,
          role
        }),
      });
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="d-flex justify-content-center align-items-center vh-100 bg-primary">
      <div className="bg-dark p-4 rounded shadow-lg text-white" style={{ width: '100%', maxWidth: '400px' }}>
        <h2 className="text-center mb-3">Create Your Account</h2>
        <p className="text-center mb-4">Sign up to LVX to continue to LVX-web.</p>

        {/* Email Field */}
        <div className="mb-3">
          <input 
            className="form-control" 
            type="email" 
            placeholder="Email address" 
            onChange={(e) => setEmail(e.target.value)} 
          />
        </div>

        {/* Password Field */}
        <div className="mb-3">
          <input 
            className="form-control" 
            type="password" 
            placeholder="Password" 
            onChange={(e) => setPassword(e.target.value)} 
          />
        </div>

        {/* Sign Up Button */}
        <button className="btn btn-lg btn-primary w-100 mb-3" onClick={handleEmailSignup}>
          Continue
        </button>

        <hr className="my-4" />

        {/* Google Sign Up Button with Icon */}
        <button className="btn btn-lg btn-outline-danger w-100 mb-3" onClick={handleGoogleSignup}>
          <FontAwesomeIcon icon={faGoogle} className="me-2" /> Continue with Google
        </button>

       

        {/* Login Prompt */}
        <div className="text-center mt-3">
          Already have an account? <a href="/login" className="text-danger">Log in</a>
        </div>
      </div>
    </div>
  );
};

export default Signup;



// import React, { useState, useEffect } from "react";
// import { useLocation } from "react-router-dom";
// import { auth, signUpWithEmail } from "./firebase";
// import "bootstrap/dist/css/bootstrap.min.css";
// import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
// import { faGoogle } from "@fortawesome/free-brands-svg-icons";
// import {
//   GoogleAuthProvider,
//   signInWithRedirect,
//   getRedirectResult,
// } from "firebase/auth";

// const Signup = () => {
//   const location = useLocation();
//   const role = location.state?.role || ""; // "investor" or "founder"

//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");

//   useEffect(() => {
//     if (role) {
//       console.log("User Role:", role);
//     }

//     // Handle Google sign-in result after redirect
//     getRedirectResult(auth)
//       .then(async (result) => {
//         if (result) {
//           const user = result.user;
//           const token = await user.getIdToken();

//           await fetch("https://8000-genaihackat-aianalystfe-o07n93pd4xm.ws-us121.gitpod.io/api/auth", {
//             method: "POST",
//             headers: {
//               "Content-Type": "application/json",
//               Authorization: `Bearer ${token}`,
//             },
//             body: JSON.stringify({
//               email: user.email,
//               password: null,
//               role,
//             }),
//           });

//           console.log("Google Sign-In Success:", user);
//         }
//       })
//       .catch((error) => {
//         console.error("Google Sign-In Redirect Error:", error);
//       });
//   }, [role]);

//   const handleEmailSignup = async () => {
//     try {
//       const result = await signUpWithEmail(email, password);
//       const token = await result.user.getIdToken(true);

//       await fetch("https://8000-genaihackat-aianalystfe-o07n93pd4xm.ws-us121.gitpod.io/api/auth", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//           Authorization: `Bearer ${token}`,
//         },
//         body: JSON.stringify({ email, password, role }),
//       });

//       console.log("Signed up:", result.user);
//     } catch (err) {
//       console.error(err);
//     }
//   };

//   const handleGoogleSignup = () => {
//     const provider = new GoogleAuthProvider();
//     signInWithRedirect(auth, provider);
//   };

//   return (
//     <div className="d-flex justify-content-center align-items-center vh-100 bg-primary">
//       <div className="bg-dark p-4 rounded shadow-lg text-white" style={{ width: '100%', maxWidth: '400px' }}>
//         <h2 className="text-center mb-3">Create Your Account</h2>
//         <p className="text-center mb-4">Sign up to LVX to continue to LVX-web.</p>

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

//         {/* Sign Up Button */}
//         <button className="btn btn-lg btn-primary w-100 mb-3" onClick={handleEmailSignup}>
//           Continue
//         </button>

//         <hr className="my-4" />

//         {/* Google Sign Up Button with Icon */}
//         <button className="btn btn-lg btn-outline-danger w-100 mb-3" onClick={handleGoogleSignup}>
//           <FontAwesomeIcon icon={faGoogle} className="me-2" /> Continue with Google
//         </button>

//         {/* Login Prompt */}
//         <div className="text-center mt-3">
//           Already have an account? <a href="/login" className="text-danger">Log in</a>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Signup;
