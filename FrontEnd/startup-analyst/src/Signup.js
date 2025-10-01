import React, { useState } from "react";
import { auth, signUpWithEmail, signInWithGoogle } from "./firebase";

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleEmailSignup = async () => {
    try {
      const result = await signUpWithEmail(email, password);
      const token = await result.user.getIdToken(true);
      console.log(token)
      
      // send to backend
      await fetch("https://8000-genaihackat-aianalystfe-o07n93pd4xm.ws-us121.gitpod.io/api/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ email,password }),
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
    console.log(user)
    const token = await user.getIdToken();

    await fetch("https://8000-genaihackat-aianalystfe-o07n93pd4xm.ws-us121.gitpod.io/api/auth", {
      method: "POST",
      headers: { 
        "Content-Type": "application/json", 
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify({ 
        email: user.email,      // ✅ get email from Google user
        password: null          // optional, can skip for Google signup
      }),
    });
  } catch (error) {
    console.error(error);
  }
};


  return (
    <div>
      <h2>Signup</h2>
      <input type="email" placeholder="Email" onChange={(e) => setEmail(e.target.value)} />
      <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} />
      <button onClick={handleEmailSignup}>Sign Up with Email</button>
      <hr />
      <button onClick={handleGoogleSignup}>Continue with Google</button>
    </div>
  );
};

export default Signup;
