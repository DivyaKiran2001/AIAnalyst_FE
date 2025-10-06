// import React, { useState } from 'react';
// import PhoneInput from 'react-phone-input-2';
// import 'react-phone-input-2/lib/bootstrap.css';

// export default function StartupRegistration() {
//   const [currentStep, setCurrentStep] = useState(1);
//   const [formData, setFormData] = useState({
//     yourName: '',
//     emailId: '',
//     gender: 'Female',
//     phoneNumber: '',
//     linkedinUrl: '',
//     singleFounder: 'Yes',
//     referrer: '',
//     startupName: '',
//     registeredName: '',
//     incorporationMonth: '',
//     incorporationYear: '',
//     pitchDeck: null,
//     about: ''
//   });

//   const [errors, setErrors] = useState({});

//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setFormData(prev => ({
//       ...prev,
//       [name]: value
//     }));
//     if (errors[name]) {
//       setErrors(prev => ({
//         ...prev,
//         [name]: ''
//       }));
//     }
//   };

//   const handleFileChange = (e) => {
//     const file = e.target.files[0];
//     setFormData(prev => ({
//       ...prev,
//       pitchDeck: file
//     }));
//     if (errors.pitchDeck) {
//       setErrors(prev => ({
//         ...prev,
//         pitchDeck: ''
//       }));
//     }
//   };

//   const validatePersonalDetails = () => {
//     const newErrors = {};

//     if (!formData.yourName.trim()) {
//       newErrors.yourName = 'Name is required';
//     }

//     if (!formData.emailId.trim()) {
//       newErrors.emailId = 'Email is required';
//     } else if (!/\S+@\S+\.\S+/.test(formData.emailId)) {
//       newErrors.emailId = 'Email is invalid';
//     }

//     // if (!formData.phoneNumber.trim()) {
//     //   newErrors.phoneNumber = 'Phone number is required';
//     // } else if (!/^\d{10}$/.test(formData.phoneNumber)) {
//     //   newErrors.phoneNumber = 'Phone number must be 10 digits';
//     // }

//     if (!formData.phoneNumber.trim()) {
//   newErrors.phoneNumber = 'Phone number is required';
// } else if (!/^\+\d{10,15}$/.test(formData.phoneNumber)) {
//   newErrors.phoneNumber = 'Enter a valid phone number with country code';
// }


//     if (!formData.linkedinUrl.trim()) {
//       newErrors.linkedinUrl = 'LinkedIn Profile URL is required';
//     } else if (!/^https?:\/\/(www\.)?linkedin\.com\/.+/.test(formData.linkedinUrl)) {
//       newErrors.linkedinUrl = 'Please enter a valid LinkedIn URL';
//     }

//     setErrors(newErrors);
//     return Object.keys(newErrors).length === 0;
//   };

//   const validateStartupDetails = () => {
//     const newErrors = {};

//     if (!formData.startupName.trim()) {
//       newErrors.startupName = 'Startup name is required';
//     }

//     if (!formData.registeredName.trim()) {
//       newErrors.registeredName = 'Registered name is required';
//     }

//     if (!formData.incorporationMonth) {
//       newErrors.incorporationMonth = 'Month is required';
//     }

//     if (!formData.incorporationYear) {
//       newErrors.incorporationYear = 'Year is required';
//     }

//     if (!formData.pitchDeck) {
//       newErrors.pitchDeck = 'Pitch deck is required';
//     }

//     if (!formData.about.trim()) {
//       newErrors.about = 'About section is required';
//     } else if (formData.about.length > 100) {
//       newErrors.about = 'Maximum 100 characters allowed';
//     }

//     setErrors(newErrors);
//     return Object.keys(newErrors).length === 0;
//   };

//   const handleContinue = () => {
//     if (validatePersonalDetails()) {
//       setCurrentStep(2);
//     }
//   };

//   const handleSubmit = (e) => {
//     e.preventDefault();
//     if (validateStartupDetails()) {
//       console.log('Form submitted:', formData);
//       alert('Registration submitted successfully!');
//     }
//   };

//   const months = [
//     'January', 'February', 'March', 'April', 'May', 'June',
//     'July', 'August', 'September', 'October', 'November', 'December'
//   ];

//   const currentYear = new Date().getFullYear();
//   const years = Array.from({ length: 50 }, (_, i) => currentYear - i);

//   return (
//     <>
//       <link
//         href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css"
//         rel="stylesheet"
//       />
//       <style>{`
//         .form-control-filled {
//           background-color: white;
//           color: black !important;
//           border: 1px solid #ddd;
//         }
//         .form-control-filled::placeholder {
//           color: #6c757d;
//         }
//         .step-circle {
//           width: 30px;
//           height: 30px;
//           border-radius: 50%;
//           display: flex;
//           align-items: center;
//           justify-content: center;
//           font-weight: bold;
//         }
//         .step-active {
//           background-color: #4169E1;
//           color: white;
//         }
//         .step-inactive {
//           background-color: #e9ecef;
//           color: #999;
//           border: 1px solid #ddd;
//         }
//         .step-line {
//           height: 3px;
//           background-color: #4169E1;
//           margin-top: 8px;
//         }
//         .form-check-input:checked {
//           background-color: #4169E1;
//           border-color: #4169E1;
//         }
//       `}</style>

//       <div className="min-vh-100 bg-light py-5">
//         <div className="container">
//           <div className="row justify-content-center">
//             <div className="col-lg-10">
//               <div className="card shadow-sm">
//                 <div className="card-body p-5">
//                     <button
//   className="btn btn-outline-secondary mb-4"
//   onClick={() => window.history.back()}
// >
//   ← Back to Dashboard
// </button>

//                   <h1 className="text-center mb-5">Lets Get started</h1>

//                   {/* Step Progress */}
//                   <div className="row mb-5">
//                     <div className="col-6">
//                       <div className="d-flex align-items-center mb-2">
//                         <div className={`step-circle me-2 ${currentStep === 1 ? 'step-active' : 'step-inactive'}`}>
//                           1
//                         </div>
//                         <h5 className={`mb-0 ${currentStep === 1 ? 'text-primary' : 'text-muted'}`}>
//                           Personal Details
//                         </h5>
//                       </div>
//                       {currentStep === 1 && <div className="step-line"></div>}
//                     </div>
//                     <div className="col-6">
//                       <div className="d-flex align-items-center mb-2">
//                         <div className={`step-circle me-2 ${currentStep === 2 ? 'step-active' : 'step-inactive'}`}>
//                           2
//                         </div>
//                         <h5 className={`mb-0 ${currentStep === 2 ? 'text-primary' : 'text-muted'}`}>
//                           Startup Details
//                         </h5>
//                       </div>
//                       {currentStep === 2 && <div className="step-line"></div>}
//                     </div>
//                   </div>

//                   {currentStep === 1 ? (
//                     <div>
//                       <div className="row mb-4">
//                         <div className="col-md-6">
//                           <label className="form-label">Your Name <span className="text-danger">*</span></label>
//                           <input
//                             type="text"
//                             className={`form-control form-control-filled ${errors.yourName ? 'is-invalid' : ''}`}
//                             name="yourName"
//                             value={formData.yourName}
//                             onChange={handleInputChange}
//                           />
//                           {errors.yourName && <div className="invalid-feedback">{errors.yourName}</div>}
//                         </div>
//                         <div className="col-md-6">
//                           <label className="form-label">Email ID <span className="text-danger">*</span></label>
//                           <input
//                             type="email"
//                             className={`form-control form-control-filled ${errors.emailId ? 'is-invalid' : ''}`}
//                             name="emailId"
//                             value={formData.emailId}
//                             onChange={handleInputChange}
//                           />
//                           {errors.emailId && <div className="invalid-feedback">{errors.emailId}</div>}
//                         </div>
//                       </div>

//                       <div className="row mb-4">
//                         <div className="col-md-6">
//                           <label className="form-label">Gender <span className="text-danger">*</span></label>
//                           <div>
//                             <div className="form-check form-check-inline">
//                               <input
//                                 className="form-check-input"
//                                 type="radio"
//                                 name="gender"
//                                 id="male"
//                                 value="Male"
//                                 checked={formData.gender === 'Male'}
//                                 onChange={handleInputChange}
//                               />
//                               <label className="form-check-label" htmlFor="male">Male</label>
//                             </div>
//                             <div className="form-check form-check-inline">
//                               <input
//                                 className="form-check-input"
//                                 type="radio"
//                                 name="gender"
//                                 id="female"
//                                 value="Female"
//                                 checked={formData.gender === 'Female'}
//                                 onChange={handleInputChange}
//                               />
//                               <label className="form-check-label" htmlFor="female">Female</label>
//                             </div>
//                           </div>
//                         </div>
//                         {/* <div className="col-md-6">
//                           <label className="form-label">Phone number <span className="text-danger">*</span></label>
//                           <div className="input-group">
//                             <span className="input-group-text">🇮🇳</span>
//                             <input
//                               type="text"
//                               className={`form-control form-control-filled ${errors.phoneNumber ? 'is-invalid' : ''}`}
//                               name="phoneNumber"
//                               value={formData.phoneNumber}
//                               onChange={handleInputChange}
//                             />
//                             {errors.phoneNumber && <div className="invalid-feedback">{errors.phoneNumber}</div>}
//                           </div>
//                           <small className="text-muted">Please enter the number with respective country code.</small>
//                         </div> */}
//                         <div className="col-md-6">
//   <label className="form-label">Phone number <span className="text-danger">*</span></label>
//   <PhoneInput
//     country={'in'}  // default country India
//     value={formData.phoneNumber}
//     onChange={(phone) => setFormData(prev => ({ ...prev, phoneNumber: phone }))}
//     inputProps={{
//       name: 'phoneNumber',
//       required: true,
//       className: `form-control form-control-filled ${errors.phoneNumber ? 'is-invalid' : ''}`
//     }}
//     enableSearch={true} // allow searching countries
//     placeholder="Enter phone number"
//   />
//   {errors.phoneNumber && <div className="invalid-feedback">{errors.phoneNumber}</div>}
//   <small className="text-muted">Select your country and enter a valid phone number.</small>
// </div>

//                       </div>

//                       <div className="row mb-4">
//                         <div className="col-md-6">
//                           <label className="form-label">LinkedIn Profile URL <span className="text-danger">*</span></label>
//                           <input
//                             type="url"
//                             className={`form-control form-control-filled ${errors.linkedinUrl ? 'is-invalid' : ''}`}
//                             name="linkedinUrl"
//                             value={formData.linkedinUrl}
//                             onChange={handleInputChange}
//                           />
//                           {errors.linkedinUrl && <div className="invalid-feedback">{errors.linkedinUrl}</div>}
//                         </div>
//                         <div className="col-md-6">
//                           <label className="form-label">Choose kind of Referrer</label>
//                           <input
//                             type="text"
//                             className="form-control form-control-filled"
//                             name="referrer"
//                             value={formData.referrer}
//                             onChange={handleInputChange}
//                           />
//                         </div>
//                       </div>

//                       <div className="mb-5">
//                         <label className="form-label">Are you a single Founder?</label>
//                         <div>
//                           <div className="form-check form-check-inline">
//                             <input
//                               className="form-check-input"
//                               type="radio"
//                               name="singleFounder"
//                               id="yes"
//                               value="Yes"
//                               checked={formData.singleFounder === 'Yes'}
//                               onChange={handleInputChange}
//                             />
//                             <label className="form-check-label" htmlFor="yes">Yes</label>
//                           </div>
//                           <div className="form-check form-check-inline">
//                             <input
//                               className="form-check-input"
//                               type="radio"
//                               name="singleFounder"
//                               id="no"
//                               value="No"
//                               checked={formData.singleFounder === 'No'}
//                               onChange={handleInputChange}
//                             />
//                             <label className="form-check-label" htmlFor="no">No</label>
//                           </div>
//                         </div>
//                       </div>

//                       <div className="d-flex justify-content-between border-top pt-4">
//                         <button className="btn btn-outline-secondary" onClick={() => window.history.back()}>
//                           Go back
//                         </button>
//                         <button className="btn btn-primary px-5" onClick={handleContinue}>
//                           Continue to Startup Details &gt;
//                         </button>
//                       </div>
//                     </div>
//                   ) : (
//                     <div>
//                       <div className="row mb-4">
//                         <div className="col-md-6">
//                           <label className="form-label">Name of startup <span className="text-danger">*</span></label>
//                           <input
//                             type="text"
//                             className={`form-control ${errors.startupName ? 'is-invalid' : ''}`}
//                             name="startupName"
//                             value={formData.startupName}
//                             onChange={handleInputChange}
//                           />
//                           {errors.startupName && <div className="invalid-feedback">{errors.startupName}</div>}
//                         </div>
//                         <div className="col-md-6">
//                           <label className="form-label">Registered name of startup <span className="text-danger">*</span></label>
//                           <input
//                             type="text"
//                             className={`form-control ${errors.registeredName ? 'is-invalid' : ''}`}
//                             name="registeredName"
//                             value={formData.registeredName}
//                             onChange={handleInputChange}
//                           />
//                           {errors.registeredName && <div className="invalid-feedback">{errors.registeredName}</div>}
//                         </div>
//                       </div>

//                       <div className="row mb-4">
//                         <div className="col-md-6">
//                           <label className="form-label">Month and year of incorporation <span className="text-danger">*</span></label>
//                           <div className="row g-2">
//                             <div className="col-6">
//                               <select
//                                 className={`form-select ${errors.incorporationMonth ? 'is-invalid' : ''}`}
//                                 name="incorporationMonth"
//                                 value={formData.incorporationMonth}
//                                 onChange={handleInputChange}
//                               >
//                                 <option value="">Month</option>
//                                 {months.map((month, index) => (
//                                   <option key={index} value={month}>{month}</option>
//                                 ))}
//                               </select>
//                             </div>
//                             <div className="col-6">
//                               <select
//                                 className={`form-select ${errors.incorporationYear ? 'is-invalid' : ''}`}
//                                 name="incorporationYear"
//                                 value={formData.incorporationYear}
//                                 onChange={handleInputChange}
//                               >
//                                 <option value="">Year</option>
//                                 {years.map((year) => (
//                                   <option key={year} value={year}>{year}</option>
//                                 ))}
//                               </select>
//                             </div>
//                           </div>
//                           {(errors.incorporationMonth || errors.incorporationYear) && (
//                             <div className="text-danger small mt-1">Month and year are required</div>
//                           )}
//                         </div>
//                         <div className="col-md-6">
//                           <label className="form-label">Please share your pitch deck <span className="text-danger">*</span></label>
//                           <input
//                             type="file"
//                             className={`form-control ${errors.pitchDeck ? 'is-invalid' : ''}`}
//                             onChange={handleFileChange}
//                             accept=".pdf,.ppt,.pptx"
//                           />
//                           {errors.pitchDeck && <div className="invalid-feedback">{errors.pitchDeck}</div>}
//                         </div>
//                       </div>

//                       <div className="mb-5">
//                         <label className="form-label">100 characters to tell us what you are building (About the startup) <span className="text-danger">*</span></label>
//                         <textarea
//                           className={`form-control ${errors.about ? 'is-invalid' : ''}`}
//                           name="about"
//                           rows="3"
//                           maxLength="100"
//                           value={formData.about}
//                           onChange={handleInputChange}
//                         ></textarea>
//                         <small className="text-muted">{formData.about.length}/100 characters</small>
//                         {errors.about && <div className="invalid-feedback">{errors.about}</div>}
//                       </div>

//                       <div className="d-flex justify-content-between border-top pt-4">
//                         <button className="btn btn-outline-secondary" onClick={() => setCurrentStep(1)}>
//                           Go back
//                         </button>
//                         <button className="btn btn-primary px-5" onClick={handleSubmit}>
//                           Submit Registration
//                         </button>
//                       </div>
//                     </div>
//                   )}
//                 </div>
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>
//     </>
//   );
// }

import React, { useState } from 'react';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/bootstrap.css';
import { auth, RecaptchaVerifier, signInWithPhoneNumber } from './firebase';

export default function StartupRegistration() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    yourName: '',
    emailId: '',
    gender: 'Female',
    phoneNumber: '',
    linkedinUrl: '',
    singleFounder: 'Yes',
    referrer: '',
    startupName: '',
    registeredName: '',
    incorporationMonth: '',
    incorporationYear: '',
    pitchDeck: null,
    about: ''
  });

  const [errors, setErrors] = useState({});
  const [otpSent, setOtpSent] = useState(false);
  const [otp, setOtp] = useState('');
  const [confirmationResult, setConfirmationResult] = useState(null);
  const [isVerified, setIsVerified] = useState(false);

  // Handle input change
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
  };

  // Handle file change
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFormData(prev => ({ ...prev, pitchDeck: file }));
    if (errors.pitchDeck) setErrors(prev => ({ ...prev, pitchDeck: '' }));
  };

  // Setup invisible reCAPTCHA
  const setupRecaptcha = () => {
    if (!window.recaptchaVerifier) {
      window.recaptchaVerifier = new RecaptchaVerifier(
        auth,
        'recaptcha-container',
        {
          size: 'invisible',
          callback: (response) => console.log('Invisible reCAPTCHA verified!', response),
          'expired-callback': () => console.log('reCAPTCHA expired.')
        }
      );
    }
  };

  // Send OTP
  const sendOtp = async () => {
    if (!formData.phoneNumber) return alert('Enter a valid phone number');
    try {
      setupRecaptcha();
      const appVerifier = window.recaptchaVerifier;
      const confirmation = await signInWithPhoneNumber(auth, `+${formData.phoneNumber}`, appVerifier);
      setConfirmationResult(confirmation);
      setOtpSent(true);
      alert('OTP sent successfully!');
    } catch (error) {
      console.error(error);
      alert('Failed to send OTP. Check phone number or try again.');
    }
  };

  // Verify OTP
  const verifyOtp = async () => {
    try {
      if (!confirmationResult) return alert('No OTP request found');
      await confirmationResult.confirm(otp);
      setIsVerified(true);
      alert('✅ Phone number verified successfully');
    } catch (error) {
      console.error(error);
      alert('❌ Invalid OTP, please try again.');
    }
  };

  // Validate personal details
  const validatePersonalDetails = () => {
    const newErrors = {};
    if (!formData.yourName.trim()) newErrors.yourName = 'Name is required';
    if (!formData.emailId.trim()) newErrors.emailId = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(formData.emailId)) newErrors.emailId = 'Email is invalid';
    if (!formData.phoneNumber.trim()) newErrors.phoneNumber = 'Phone number is required';
    else if (!/^\d{10,15}$/.test(formData.phoneNumber)) newErrors.phoneNumber = 'Enter a valid phone number';
    if (!isVerified) newErrors.phoneNumber = 'Phone number not verified';
    if (!formData.linkedinUrl.trim()) newErrors.linkedinUrl = 'LinkedIn Profile URL is required';
    else if (!/^https?:\/\/(www\.)?linkedin\.com\/.+/.test(formData.linkedinUrl)) newErrors.linkedinUrl = 'Enter a valid LinkedIn URL';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Validate startup details
  const validateStartupDetails = () => {
    const newErrors = {};
    if (!formData.startupName.trim()) newErrors.startupName = 'Startup name is required';
    if (!formData.registeredName.trim()) newErrors.registeredName = 'Registered name is required';
    if (!formData.incorporationMonth) newErrors.incorporationMonth = 'Month is required';
    if (!formData.incorporationYear) newErrors.incorporationYear = 'Year is required';
    if (!formData.pitchDeck) newErrors.pitchDeck = 'Pitch deck is required';
    if (!formData.about.trim()) newErrors.about = 'About section is required';
    else if (formData.about.length > 100) newErrors.about = 'Maximum 100 characters allowed';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Continue to next step
  const handleContinue = () => {
    if (validatePersonalDetails()) setCurrentStep(2);
  };

  // Submit final registration
  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateStartupDetails()) {
      console.log('Form submitted:', formData);
      alert('Registration submitted successfully!');
    }
  };

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 50 }, (_, i) => currentYear - i);

  return (
    <>
      <link href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css" rel="stylesheet" />
      <style>{`
        .form-control-filled {
          background-color: white;
          color: black !important;
          border: 1px solid #ddd;
        }
        .form-control-filled::placeholder {
          color: #6c757d;
        }
        .step-circle {
          width: 30px; height: 30px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
        }
        .step-active { background-color: #4169E1; color: white; }
        .step-inactive { background-color: #e9ecef; color: #999; border: 1px solid #ddd; }
        .step-line { height: 3px; background-color: #4169E1; margin-top: 8px; }
        .form-check-input:checked { background-color: #4169E1; border-color: #4169E1; }
      `}</style>

      <div className="min-vh-100 bg-light py-5">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-10">
              <div className="card shadow-sm">
                <div className="card-body p-5">
                  <button className="btn btn-outline-secondary mb-4" onClick={() => window.history.back()}>
                    ← Back to Dashboard
                  </button>

                  <h1 className="text-center mb-5">Let's Get Started</h1>

                  {/* Step Progress */}
                  <div className="row mb-5">
                    <div className="col-6">
                      <div className="d-flex align-items-center mb-2">
                        <div className={`step-circle me-2 ${currentStep === 1 ? 'step-active' : 'step-inactive'}`}>1</div>
                        <h5 className={`mb-0 ${currentStep === 1 ? 'text-primary' : 'text-muted'}`}>Personal Details</h5>
                      </div>
                      {currentStep === 1 && <div className="step-line"></div>}
                    </div>
                    <div className="col-6">
                      <div className="d-flex align-items-center mb-2">
                        <div className={`step-circle me-2 ${currentStep === 2 ? 'step-active' : 'step-inactive'}`}>2</div>
                        <h5 className={`mb-0 ${currentStep === 2 ? 'text-primary' : 'text-muted'}`}>Startup Details</h5>
                      </div>
                      {currentStep === 2 && <div className="step-line"></div>}
                    </div>
                  </div>

                  {currentStep === 1 ? (
                    <div>
                      {/* Personal Details */}
                      <div className="row mb-4">
                        <div className="col-md-6">
                          <label className="form-label">Your Name <span className="text-danger">*</span></label>
                          <input type="text" className={`form-control form-control-filled ${errors.yourName ? 'is-invalid' : ''}`}
                            name="yourName" value={formData.yourName} onChange={handleInputChange} />
                          {errors.yourName && <div className="invalid-feedback">{errors.yourName}</div>}
                        </div>

                        <div className="col-md-6">
                          <label className="form-label">Email ID <span className="text-danger">*</span></label>
                          <input type="email" className={`form-control form-control-filled ${errors.emailId ? 'is-invalid' : ''}`}
                            name="emailId" value={formData.emailId} onChange={handleInputChange} />
                          {errors.emailId && <div className="invalid-feedback">{errors.emailId}</div>}
                        </div>
                      </div>

                      <div className="row mb-4">
                        <div className="col-md-6">
                          <label className="form-label">Gender <span className="text-danger">*</span></label>
                          <div>
                            <div className="form-check form-check-inline">
                              <input className="form-check-input" type="radio" name="gender" id="male" value="Male"
                                checked={formData.gender === 'Male'} onChange={handleInputChange} />
                              <label className="form-check-label" htmlFor="male">Male</label>
                            </div>
                            <div className="form-check form-check-inline">
                              <input className="form-check-input" type="radio" name="gender" id="female" value="Female"
                                checked={formData.gender === 'Female'} onChange={handleInputChange} />
                              <label className="form-check-label" htmlFor="female">Female</label>
                            </div>
                          </div>
                        </div>

                        {/* Phone Number with OTP */}
                        <div className="col-md-6">
                          <label className="form-label">Phone Number <span className="text-danger">*</span></label>
                          <PhoneInput
                            country={'in'}
                            value={formData.phoneNumber}
                            onChange={(phone) => setFormData(prev => ({ ...prev, phoneNumber: phone }))}
                            inputProps={{
                              name: 'phoneNumber',
                              required: true,
                              className: `form-control form-control-filled ${errors.phoneNumber ? 'is-invalid' : ''}`
                            }}
                            enableSearch
                            placeholder="Enter phone number"
                          />
                          {errors.phoneNumber && <div className="invalid-feedback">{errors.phoneNumber}</div>}
                          {!otpSent && <button className="btn btn-outline-primary mt-2" onClick={sendOtp}>Send OTP</button>}
                          {otpSent && !isVerified && (
                            <div className="mt-2">
                              <input
                                type="text"
                                className="form-control mb-2"
                                placeholder="Enter OTP"
                                value={otp}
                                onChange={(e) => setOtp(e.target.value)}
                              />
                              <button className="btn btn-success" onClick={verifyOtp}>Verify OTP</button>
                            </div>
                          )}
                          {isVerified && <div className="text-success mt-2">✅ Phone verified</div>}
                          <div id="recaptcha-container"></div>
                        </div>
                      </div>

                      <div className="row mb-4">
                        <div className="col-md-6">
                          <label className="form-label">LinkedIn Profile URL <span className="text-danger">*</span></label>
                          <input type="url" className={`form-control form-control-filled ${errors.linkedinUrl ? 'is-invalid' : ''}`}
                            name="linkedinUrl" value={formData.linkedinUrl} onChange={handleInputChange} />
                          {errors.linkedinUrl && <div className="invalid-feedback">{errors.linkedinUrl}</div>}
                        </div>
                        <div className="col-md-6">
                          <label className="form-label">Referrer</label>
                          <input type="text" className="form-control form-control-filled" name="referrer" value={formData.referrer} onChange={handleInputChange} />
                        </div>
                      </div>

                      <div className="mb-5">
                        <label className="form-label">Are you a single Founder?</label>
                        <div>
                          <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" name="singleFounder" id="yes" value="Yes"
                              checked={formData.singleFounder === 'Yes'} onChange={handleInputChange} />
                            <label className="form-check-label" htmlFor="yes">Yes</label>
                          </div>
                          <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" name="singleFounder" id="no" value="No"
                              checked={formData.singleFounder === 'No'} onChange={handleInputChange} />
                            <label className="form-check-label" htmlFor="no">No</label>
                          </div>
                        </div>
                      </div>

                      <div className="d-flex justify-content-between border-top pt-4">
                        <button className="btn btn-outline-secondary" onClick={() => window.history.back()}>Go back</button>
                        <button className="btn btn-primary px-5" onClick={handleContinue}>Continue &gt;</button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      {/* Startup Details */}
                      <div className="row mb-4">
                        <div className="col-md-6">
                          <label className="form-label">Startup Name <span className="text-danger">*</span></label>
                          <input type="text" className={`form-control ${errors.startupName ? 'is-invalid' : ''}`} name="startupName" value={formData.startupName} onChange={handleInputChange} />
                          {errors.startupName && <div className="invalid-feedback">{errors.startupName}</div>}
                        </div>
                        <div className="col-md-6">
                          <label className="form-label">Registered Name <span className="text-danger">*</span></label>
                          <input type="text" className={`form-control ${errors.registeredName ? 'is-invalid' : ''}`} name="registeredName" value={formData.registeredName} onChange={handleInputChange} />
                          {errors.registeredName && <div className="invalid-feedback">{errors.registeredName}</div>}
                        </div>
                      </div>

                      <div className="row mb-4">
                        <div className="col-md-6">
                          <label className="form-label">Month & Year of Incorporation <span className="text-danger">*</span></label>
                          <div className="row g-2">
                            <div className="col-6">
                              <select className={`form-select ${errors.incorporationMonth ? 'is-invalid' : ''}`}
                                name="incorporationMonth" value={formData.incorporationMonth} onChange={handleInputChange}>
                                <option value="">Month</option>
                                {months.map((month) => <option key={month} value={month}>{month}</option>)}
                              </select>
                            </div>
                            <div className="col-6">
                              <select className={`form-select ${errors.incorporationYear ? 'is-invalid' : ''}`}
                                name="incorporationYear" value={formData.incorporationYear} onChange={handleInputChange}>
                                <option value="">Year</option>
                                {years.map((year) => <option key={year} value={year}>{year}</option>)}
                              </select>
                            </div>
                          </div>
                          {(errors.incorporationMonth || errors.incorporationYear) && <div className="text-danger small mt-1">Month and year are required</div>}
                        </div>

                        <div className="col-md-6">
                          <label className="form-label">Pitch Deck <span className="text-danger">*</span></label>
                          <input type="file" className={`form-control ${errors.pitchDeck ? 'is-invalid' : ''}`} onChange={handleFileChange} accept=".pdf,.ppt,.pptx" />
                          {errors.pitchDeck && <div className="invalid-feedback">{errors.pitchDeck}</div>}
                        </div>
                      </div>

                      <div className="mb-5">
                        <label className="form-label">About Startup (100 chars) <span className="text-danger">*</span></label>
                        <textarea className={`form-control ${errors.about ? 'is-invalid' : ''}`} name="about" rows="3" maxLength="100" value={formData.about} onChange={handleInputChange}></textarea>
                        <small className="text-muted">{formData.about.length}/100 characters</small>
                        {errors.about && <div className="invalid-feedback">{errors.about}</div>}
                      </div>

                      <div className="d-flex justify-content-between border-top pt-4">
                        <button className="btn btn-outline-secondary" onClick={() => setCurrentStep(1)}>Go back</button>
                        <button className="btn btn-primary px-5" onClick={handleSubmit}>Submit Registration</button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
