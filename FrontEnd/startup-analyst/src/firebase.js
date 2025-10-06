import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth, GoogleAuthProvider, signInWithPopup, createUserWithEmailAndPassword, signInWithEmailAndPassword ,RecaptchaVerifier, signInWithPhoneNumber,sendEmailVerification} from "firebase/auth";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyAQ4BEc8RRnrGLg2oS-cA4aGUEGiCctYPo",
  authDomain: "aianalyst-61509.firebaseapp.com",
  projectId: "aianalyst-61509",
  storageBucket: "aianalyst-61509.firebasestorage.app",
  messagingSenderId: "78713256065",
  appId: "1:78713256065:web:bc01b58174b50e79d9b580",
  measurementId: "G-FQK8LZ09K5"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
  prompt: "consent", // Forces Google to show consent every time
});


// helpers
export const signUpWithEmail = (email, password) => createUserWithEmailAndPassword(auth, email, password);
export const loginInWithEmail = (email, password) => signInWithEmailAndPassword(auth, email, password);
export const signInWithGoogle = () => signInWithPopup(auth, googleProvider);

// Send email verification
const sendVerificationEmail = (user) => sendEmailVerification(user, {
  url: "https://3000-genaihackat-aianalystfe-hgc0ltv9os0.ws-us121.gitpod.io/signup" // Redirect after verification
});

// Google auth using redirect
// export const signInWithGoogle = () =>
//   signInWithRedirect(auth, googleProvider);

export { RecaptchaVerifier, signInWithPhoneNumber,sendVerificationEmail };