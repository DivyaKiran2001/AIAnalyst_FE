


import React, { useState } from 'react';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/bootstrap.css';
import axios from 'axios';
import { getAuth } from 'firebase/auth';
import { useNavigate } from "react-router-dom";


export default function StartupRegistration() {
  const navigate = useNavigate();
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
 
    about: ''
  });

  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const auth = getAuth();
  const user = auth.currentUser;

  // Input change
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
  };

  // File change
  // const handleFileChange = (e) => {
  //   const file = e.target.files[0];
  //   setFormData(prev => ({ ...prev, pitchDeck: file }));
  //   if (errors.pitchDeck) setErrors(prev => ({ ...prev, pitchDeck: '' }));
  // };

  // Personal details validation
  const validatePersonalDetails = () => {
    const newErrors = {};
    if (!formData.yourName.trim()) newErrors.yourName = 'Name is required';
    if (!formData.emailId.trim()) newErrors.emailId = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(formData.emailId)) newErrors.emailId = 'Email is invalid';
    if (!formData.phoneNumber.trim()) newErrors.phoneNumber = 'Phone number is required';
    else if (!/^\d{10,15}$/.test(formData.phoneNumber)) newErrors.phoneNumber = 'Enter a valid phone number';
    if (!formData.linkedinUrl.trim()) newErrors.linkedinUrl = 'LinkedIn Profile URL is required';
    else if (!/^https?:\/\/(www\.)?linkedin\.com\/.+/.test(formData.linkedinUrl)) newErrors.linkedinUrl = 'Enter a valid LinkedIn URL';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Startup details validation
  const validateStartupDetails = () => {
    const newErrors = {};
    if (!formData.startupName.trim()) newErrors.startupName = 'Startup name is required';
    if (!formData.registeredName.trim()) newErrors.registeredName = 'Registered name is required';
    if (!formData.incorporationMonth) newErrors.incorporationMonth = 'Month is required';
    if (!formData.incorporationYear) newErrors.incorporationYear = 'Year is required';
    // if (!formData.pitchDeck) newErrors.pitchDeck = 'Pitch deck is required';
    if (!formData.about.trim()) newErrors.about = 'About section is required';
    else if (formData.about.length > 200) newErrors.about = 'Maximum 200 characters allowed';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleContinue = () => {
    if (validatePersonalDetails()) setCurrentStep(2);
  };

  // Submit registration to backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) return alert('❌ User not logged in');
    if (!validateStartupDetails()) return;

    setIsSubmitting(true);

    try {
      const token = await user.getIdToken();

      // Founder details
      const founderPayload = {
        yourName: formData.yourName,
        emailId: formData.emailId,
        gender: formData.gender,
        phoneNumber: formData.phoneNumber,
        linkedinUrl: formData.linkedinUrl,
        singleFounder: formData.singleFounder,
        referrer: formData.referrer || null
      };

      await axios.post('https://8000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev/api/founder-details', founderPayload, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Startup details with email included
      // const startupFormData = new FormData();
      // startupFormData.append('emailId', formData.emailId);
      // startupFormData.append('startupName', formData.startupName);
      // startupFormData.append('registeredName', formData.registeredName);
      // startupFormData.append('incorporationMonth', formData.incorporationMonth);
      // startupFormData.append('incorporationYear', formData.incorporationYear);
      // startupFormData.append('about', formData.about);
      // startupFormData.append('pitchDeck', formData.pitchDeck);

      // await axios.post('https://8000-genaihackat-aianalystfe-hgc0ltv9os0.ws-us121.gitpod.io/api/startup-details', startupFormData, {
      //   headers: {
      //     Authorization: `Bearer ${token}`,
      //     'Content-Type': 'multipart/form-data'
      //   }
      // });
      const startupData = {
  startupName: formData.startupName,
  registeredName: formData.registeredName,
  incorporationMonth: formData.incorporationMonth,
  incorporationYear: formData.incorporationYear,
  about: formData.about,
 
};

await axios.post(
  'https://8000-firebase-aianalystfe-1760591860192.cluster-nulpgqge5rgw6rwqiydysl6ocy.cloudworkstations.dev/api/startup-details',
  startupData,
  {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
);


      alert('✅ Founder & Startup details submitted successfully!');
      // setCurrentStep(1);
      // setFormData({
      //   yourName: '',
      //   emailId: '',
      //   gender: 'Female',
      //   phoneNumber: '',
      //   linkedinUrl: '',
      //   singleFounder: 'Yes',
      //   referrer: '',
      //   startupName: '',
      //   registeredName: '',
      //   incorporationMonth: '',
      //   incorporationYear: '',
      //   about: ''
      // });
       navigate("/founder-dashboard");
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || '❌ Failed to submit details');
    } finally {
      setIsSubmitting(false);
    }
  };

  const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 50 }, (_, i) => currentYear - i);

  return (
    <div className="min-vh-100 bg-light py-5">
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-lg-10">
            <div className="card shadow-sm">
              <div className="card-body p-5">
                <button className="btn btn-outline-secondary mb-4" onClick={() => window.history.back()}>← Back to Dashboard</button>
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
                    <div className="row mb-4">
                      <div className="col-md-6">
                        <label className="form-label">Your Name <span className="text-danger">*</span></label>
                        <input type="text" className={`form-control ${errors.yourName ? 'is-invalid' : ''}`} name="yourName" value={formData.yourName} onChange={handleInputChange} />
                        {errors.yourName && <div className="invalid-feedback">{errors.yourName}</div>}
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Email ID <span className="text-danger">*</span></label>
                        <input type="email" className={`form-control ${errors.emailId ? 'is-invalid' : ''}`} name="emailId" value={formData.emailId} onChange={handleInputChange} />
                        {errors.emailId && <div className="invalid-feedback">{errors.emailId}</div>}
                      </div>
                    </div>

                    <div className="row mb-4">
                      <div className="col-md-6">
                        <label className="form-label">Gender <span className="text-danger">*</span></label>
                        <div>
                          <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" name="gender" value="Male" checked={formData.gender === 'Male'} onChange={handleInputChange} />
                            <label className="form-check-label">Male</label>
                          </div>
                          <div className="form-check form-check-inline">
                            <input className="form-check-input" type="radio" name="gender" value="Female" checked={formData.gender === 'Female'} onChange={handleInputChange} />
                            <label className="form-check-label">Female</label>
                          </div>
                        </div>
                      </div>

                      <div className="col-md-6">
                        <label className="form-label">Phone Number <span className="text-danger">*</span></label>
                        <PhoneInput
                          country="in"
                          value={formData.phoneNumber}
                          onChange={(phone) => setFormData(prev => ({ ...prev, phoneNumber: phone }))}
                          inputProps={{ name: 'phoneNumber', required: true, className: `form-control ${errors.phoneNumber ? 'is-invalid' : ''}` }}
                          enableSearch
                          placeholder="Enter phone number"
                        />
                        {errors.phoneNumber && <div className="invalid-feedback">{errors.phoneNumber}</div>}
                      </div>
                    </div>

                    <div className="row mb-4">
                      <div className="col-md-6">
                        <label className="form-label">LinkedIn Profile URL <span className="text-danger">*</span></label>
                        <input type="url" className={`form-control ${errors.linkedinUrl ? 'is-invalid' : ''}`} name="linkedinUrl" value={formData.linkedinUrl} onChange={handleInputChange} />
                        {errors.linkedinUrl && <div className="invalid-feedback">{errors.linkedinUrl}</div>}
                      </div>
                      <div className="col-md-6">
                        <label className="form-label">Referrer</label>
                        <input type="text" className="form-control" name="referrer" value={formData.referrer} onChange={handleInputChange} />
                      </div>
                    </div>

                    <div className="mb-4">
                      <label className="form-label">Single Founder?</label>
                      <div>
                        <div className="form-check form-check-inline">
                          <input className="form-check-input" type="radio" name="singleFounder" value="Yes" checked={formData.singleFounder === 'Yes'} onChange={handleInputChange} />
                          <label className="form-check-label">Yes</label>
                        </div>
                        <div className="form-check form-check-inline">
                          <input className="form-check-input" type="radio" name="singleFounder" value="No" checked={formData.singleFounder === 'No'} onChange={handleInputChange} />
                          <label className="form-check-label">No</label>
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
                            <select className={`form-select ${errors.incorporationMonth ? 'is-invalid' : ''}`} name="incorporationMonth" value={formData.incorporationMonth} onChange={handleInputChange}>
                              <option value="">Month</option>
                              {months.map(m => <option key={m} value={m}>{m}</option>)}
                            </select>
                          </div>
                          <div className="col-6">
                            <select className={`form-select ${errors.incorporationYear ? 'is-invalid' : ''}`} name="incorporationYear" value={formData.incorporationYear} onChange={handleInputChange}>
                              <option value="">Year</option>
                              {years.map(y => <option key={y} value={y}>{y}</option>)}
                            </select>
                          </div>
                        </div>
                      </div>
{/* 
                      <div className="col-md-6">
                        <label className="form-label">Pitch Deck <span className="text-danger">*</span></label>
                        <input type="file" className={`form-control ${errors.pitchDeck ? 'is-invalid' : ''}`} onChange={handleFileChange} accept=".pdf,.ppt,.pptx" />
                        {errors.pitchDeck && <div className="invalid-feedback">{errors.pitchDeck}</div>}
                      </div> */}
                    </div>

                    <div className="mb-5">
                      <label className="form-label">About Startup (100 chars) <span className="text-danger">*</span></label>
                      <textarea className={`form-control ${errors.about ? 'is-invalid' : ''}`} name="about" rows="3" maxLength="100" value={formData.about} onChange={handleInputChange}></textarea>
                      <small className="text-muted">{formData.about.length}/100 characters</small>
                      {errors.about && <div className="invalid-feedback">{errors.about}</div>}
                    </div>

                    <div className="d-flex justify-content-between border-top pt-4">
                      <button className="btn btn-outline-secondary" onClick={() => setCurrentStep(1)}>Go back</button>
                      <button className="btn btn-primary px-5" onClick={handleSubmit} disabled={isSubmitting}>
                        {isSubmitting ? 'Submitting...' : 'Submit Registration'}
                      </button>
                    </div>
                  </div>
                )}

              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
