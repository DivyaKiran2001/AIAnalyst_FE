import React, { useState } from "react";
import PhoneInput from "react-phone-input-2";
import "react-phone-input-2/lib/bootstrap.css";
import axios from "axios";
import { getAuth } from "firebase/auth";
import { useNavigate } from "react-router-dom";
import FounderNavbar from "./FounderNavbar";
import StartupDocumentUploader from "./StartupDocumentUploader";
import StartupQuestionnaire from "./StartupQuestionnaire";

export default function StartupRegistration() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    yourName: "",
    emailId: "",
    gender: "Female",
    phoneNumber: "",
    linkedinUrl: "",
    singleFounder: "Yes",
    referrer: "",
    startupName: "",
    registeredName: "",
    incorporationMonth: "",
    incorporationYear: "",
    about: "",
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const auth = getAuth();
  const user = auth.currentUser;

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validatePersonalDetails = () => {
    const newErrors = {};
    if (!formData.yourName.trim()) newErrors.yourName = "Name is required";
    if (!formData.emailId.trim()) newErrors.emailId = "Email is required";
    else if (!/\S+@\S+\.\S+/.test(formData.emailId))
      newErrors.emailId = "Email is invalid";
    if (!formData.phoneNumber.trim())
      newErrors.phoneNumber = "Phone number is required";
    else if (!/^\d{10,15}$/.test(formData.phoneNumber))
      newErrors.phoneNumber = "Enter a valid phone number";
    if (!formData.linkedinUrl.trim())
      newErrors.linkedinUrl = "LinkedIn Profile URL is required";
    else if (
      !/^https?:\/\/(www\.)?linkedin\.com\/.+/.test(formData.linkedinUrl)
    )
      newErrors.linkedinUrl = "Enter a valid LinkedIn URL";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStartupDetails = () => {
    const newErrors = {};
    if (!formData.startupName.trim())
      newErrors.startupName = "Startup name is required";

    if (!formData.registeredName.trim())
      newErrors.registeredName = "Registered name is required";
    if (!formData.incorporationMonth)
      newErrors.incorporationMonth = "Month is required";
    if (!formData.incorporationYear)
      newErrors.incorporationYear = "Year is required";
    if (!formData.about.trim()) newErrors.about = "About section is required";
    else if (formData.about.length > 100)
      newErrors.about = "Maximum 100 characters allowed";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleContinue = () => {
    if (validatePersonalDetails()) setCurrentStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!user) return alert("❌ User not logged in");
    if (!validateStartupDetails()) return;

    setIsSubmitting(true);
    try {
      const token = await user.getIdToken();

      await axios.post(
        "http://localhost:8000/api/founder-details",
        {
          yourName: formData.yourName,
          emailId: formData.emailId,
          gender: formData.gender,
          phoneNumber: formData.phoneNumber,
          linkedinUrl: formData.linkedinUrl,
          singleFounder: formData.singleFounder,
          referrer: formData.referrer || null,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      await axios.post(
        "http://localhost:8000/api/startup-details",
        {
          startupName: formData.startupName,
          registeredName: formData.registeredName,
          incorporationMonth: formData.incorporationMonth,
          incorporationYear: formData.incorporationYear,
          about: formData.about,
          emailId: formData.emailId,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // ✅ Store startupName AFTER successful API calls
      sessionStorage.setItem("startupName", formData.startupName);
      // Move to Step 3 (File Upload)
      setCurrentStep(3);

      alert("✅ Founder & Startup details submitted successfully!");
      // navigate("/f-dashboard");
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "❌ Failed to submit details");
    } finally {
      setIsSubmitting(false);
    }
  };

  const months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 50 }, (_, i) => currentYear - i);

  return (
    <>
      <FounderNavbar />
      <div
        style={{
          backgroundColor: "#f0f0f0",
          minHeight: "100vh",
          padding: "3rem 1rem",
        }}
      >
        <h1 className="text-center mb-5" style={{ color: "rgb(18,0,94)" }}>
          Start Your Fund Raising Journey
        </h1>
        <div className="d-flex justify-content-center">
          <div className="col-12 col-lg-10 d-flex">
            {/* Vertical Stepper with headers + subheaders */}
            <div className="d-flex flex-column me-4 align-items-start">
              {[1, 2, 3, 4].map((step) => (
                <div
                  key={step}
                  className="d-flex flex-column mb-5 position-relative"
                >
                  <div className="d-flex align-items-center mb-2">
                    <div
                      className="rounded-circle border border-2 d-flex justify-content-center align-items-center"
                      style={{
                        width: "40px",
                        height: "40px",
                        backgroundColor:
                          currentStep === step ? "rgb(18,0,94)" : "#fff",
                        color: currentStep === step ? "#fff" : "rgb(18,0,94)",
                        fontWeight: "bold",
                        borderColor: "rgb(18,0,94)",
                        zIndex: 1,
                      }}
                    >
                      {step}
                    </div>
                    <div className="ms-3">
                      <div
                        style={{
                          fontWeight: currentStep === step ? "bold" : "normal",
                          color: currentStep === step ? "rgb(18,0,94)" : "gray",
                        }}
                      >
                        {step === 1
                          ? "Personal Details"
                          : step === 2
                          ? "Startup Details"
                          : step === 3
                          ? "Files"
                          : "Voice Agent"}
                      </div>
                      <div
                        style={{
                          fontSize: "0.85rem",
                          color: "gray",
                          marginTop: "2px",
                        }}
                      >
                        {step === 1
                          ? "Tell us about yourself"
                          : step === 2
                          ? "Tell us about your startup"
                          : step === 3
                          ? "Upload pitch deck files"
                          : "Answer questions via voice"}
                      </div>
                    </div>
                  </div>
                  {step < 4 && (
                    <div
                      style={{
                        position: "absolute",
                        top: "50px",
                        left: "20px",
                        width: "2px",
                        height: "80px",
                        backgroundColor: "#e0e0e0",
                        zIndex: 0,
                      }}
                    ></div>
                  )}
                </div>
              ))}
            </div>

            {/* Form */}
            <div className="flex-grow-1 card bg-white shadow rounded-4 p-5">
              <form>
                {currentStep === 1 && (
                  <>
                    {/* Personal Details */}
                    <div className="row mb-3">
                      <div className="col-md-6">
                        <label
                          className="form-label fw-bold"
                          style={{ color: "rgb(18,0,94)" }}
                        >
                          Your Name *
                        </label>
                        <input
                          type="text"
                          className={`form-control ${
                            errors.yourName ? "is-invalid" : ""
                          }`}
                          name="yourName"
                          value={formData.yourName}
                          onChange={handleInputChange}
                          placeholder="Enter your name"
                        />
                        {errors.yourName && (
                          <div className="invalid-feedback">
                            {errors.yourName}
                          </div>
                        )}
                      </div>
                      <div className="col-md-6">
                        <label
                          className="form-label fw-bold"
                          style={{ color: "rgb(18,0,94)" }}
                        >
                          Email *
                        </label>
                        <input
                          type="email"
                          className={`form-control ${
                            errors.emailId ? "is-invalid" : ""
                          }`}
                          name="emailId"
                          value={formData.emailId}
                          onChange={handleInputChange}
                          placeholder="Enter your email"
                        />
                        {errors.emailId && (
                          <div className="invalid-feedback">
                            {errors.emailId}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="row mb-3">
                      <div className="col-md-6">
                        <label
                          className="form-label fw-bold"
                          style={{ color: "rgb(18,0,94)" }}
                        >
                          Gender
                        </label>
                        <div className="d-flex">
                          {["Male", "Female"].map((g) => (
                            <div className="form-check me-4" key={g}>
                              <input
                                className="form-check-input"
                                type="radio"
                                name="gender"
                                value={g}
                                checked={formData.gender === g}
                                onChange={handleInputChange}
                                style={{ borderColor: "rgb(18,0,94)" }}
                              />
                              <label className="form-check-label">{g}</label>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div className="col-md-6">
                        <label
                          className="form-label fw-bold"
                          style={{ color: "rgb(18,0,94)" }}
                        >
                          Phone Number *
                        </label>
                        <PhoneInput
                          country="in"
                          value={formData.phoneNumber}
                          onChange={(phone) =>
                            setFormData((prev) => ({
                              ...prev,
                              phoneNumber: phone,
                            }))
                          }
                          inputProps={{
                            name: "phoneNumber",
                            required: true,
                            className: `form-control ${
                              errors.phoneNumber ? "is-invalid" : ""
                            }`,
                          }}
                          enableSearch
                          placeholder="Enter phone number"
                        />
                        {errors.phoneNumber && (
                          <div className="invalid-feedback">
                            {errors.phoneNumber}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="row mb-3">
                      <div className="col-md-6">
                        <label
                          className="form-label fw-bold"
                          style={{ color: "rgb(18,0,94)" }}
                        >
                          LinkedIn Profile URL *
                        </label>
                        <input
                          type="url"
                          className={`form-control ${
                            errors.linkedinUrl ? "is-invalid" : ""
                          }`}
                          name="linkedinUrl"
                          value={formData.linkedinUrl}
                          onChange={handleInputChange}
                          placeholder="Enter LinkedIn URL"
                        />
                        {errors.linkedinUrl && (
                          <div className="invalid-feedback">
                            {errors.linkedinUrl}
                          </div>
                        )}
                      </div>
                      <div className="col-md-6">
                        <label
                          className="form-label fw-bold"
                          style={{ color: "rgb(18,0,94)" }}
                        >
                          Referrer
                        </label>
                        <input
                          type="text"
                          className="form-control"
                          name="referrer"
                          value={formData.referrer}
                          onChange={handleInputChange}
                          placeholder="Enter referrer name"
                        />
                      </div>
                    </div>

                    <div className="mb-4">
                      <label
                        className="form-label fw-bold"
                        style={{ color: "rgb(18,0,94)" }}
                      >
                        Single Founder? *
                      </label>
                      <div className="d-flex">
                        {["Yes", "No"].map((opt) => (
                          <div className="form-check me-4" key={opt}>
                            <input
                              className="form-check-input"
                              type="radio"
                              name="singleFounder"
                              value={opt}
                              checked={formData.singleFounder === opt}
                              onChange={handleInputChange}
                              style={{ borderColor: "rgb(18,0,94)" }}
                            />
                            <label className="form-check-label">{opt}</label>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="d-flex justify-content-end mt-4 pt-3 border-top">
                      <button
                        type="button"
                        className="btn px-4"
                        onClick={handleContinue}
                        style={{
                          backgroundColor: "rgb(18,0,94)",
                          color: "white",
                          fontWeight: "bold",
                        }}
                      >
                        Continue to Startup Details →
                      </button>
                    </div>
                  </>
                )}
                {currentStep === 2 && (
                  <>
                    {/* Startup Details */}
                    <div className="row mb-3">
                      <div className="col-md-6">
                        <label
                          className="form-label fw-bold"
                          style={{ color: "rgb(18,0,94)" }}
                        >
                          Startup Name *
                        </label>
                        <input
                          type="text"
                          className={`form-control ${
                            errors.startupName ? "is-invalid" : ""
                          }`}
                          name="startupName"
                          value={formData.startupName}
                          onChange={handleInputChange}
                          placeholder="Enter startup name"
                        />
                        {errors.startupName && (
                          <div className="invalid-feedback">
                            {errors.startupName}
                          </div>
                        )}
                      </div>
                      <div className="col-md-6">
                        <label
                          className="form-label fw-bold"
                          style={{ color: "rgb(18,0,94)" }}
                        >
                          Registered Name *
                        </label>
                        <input
                          type="text"
                          className={`form-control ${
                            errors.registeredName ? "is-invalid" : ""
                          }`}
                          name="registeredName"
                          value={formData.registeredName}
                          onChange={handleInputChange}
                          placeholder="Enter registered name"
                        />
                        {errors.registeredName && (
                          <div className="invalid-feedback">
                            {errors.registeredName}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="row mb-3">
                      <div className="col-md-6">
                        <label
                          className="form-label fw-bold"
                          style={{ color: "rgb(18,0,94)" }}
                        >
                          Month & Year of Incorporation *
                        </label>
                        <div className="row g-2">
                          <div className="col-6">
                            <select
                              className={`form-select ${
                                errors.incorporationMonth ? "is-invalid" : ""
                              }`}
                              name="incorporationMonth"
                              value={formData.incorporationMonth}
                              onChange={handleInputChange}
                            >
                              <option value="">Month</option>
                              {months.map((m) => (
                                <option key={m} value={m}>
                                  {m}
                                </option>
                              ))}
                            </select>
                            {errors.incorporationMonth && (
                              <div className="invalid-feedback">
                                {errors.incorporationMonth}
                              </div>
                            )}
                          </div>
                          <div className="col-6">
                            <select
                              className={`form-select ${
                                errors.incorporationYear ? "is-invalid" : ""
                              }`}
                              name="incorporationYear"
                              value={formData.incorporationYear}
                              onChange={handleInputChange}
                            >
                              <option value="">Year</option>
                              {years.map((y) => (
                                <option key={y} value={y}>
                                  {y}
                                </option>
                              ))}
                            </select>
                            {errors.incorporationYear && (
                              <div className="invalid-feedback">
                                {errors.incorporationYear}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="mb-4">
                      <label
                        className="form-label fw-bold"
                        style={{ color: "rgb(18,0,94)" }}
                      >
                        About Startup (100 chars) *
                      </label>
                      <textarea
                        className={`form-control ${
                          errors.about ? "is-invalid" : ""
                        }`}
                        name="about"
                        rows="3"
                        maxLength="100"
                        value={formData.about}
                        onChange={handleInputChange}
                        placeholder="Describe your startup"
                      ></textarea>
                      <small className="text-muted">
                        {formData.about.length}/100 characters
                      </small>
                      {errors.about && (
                        <div className="invalid-feedback">{errors.about}</div>
                      )}
                    </div>

                    <div className="d-flex justify-content-between mt-4 pt-3 border-top">
                      <button
                        type="button"
                        className="btn btn-outline-secondary px-4"
                        onClick={() => setCurrentStep(1)}
                      >
                        ← Go Back
                      </button>
                      <button
                        type="button"
                        className="btn px-4"
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        style={{
                          backgroundColor: "rgb(18,0,94)",
                          color: "white",
                          fontWeight: "bold",
                        }}
                      >
                        {isSubmitting ? "Submitting..." : "Continue →"}
                      </button>
                    </div>
                  </>
                )}
              </form>
              {currentStep === 3 && (
                <StartupDocumentUploader
                  emailId={formData.emailId}
                  startupName={formData.startupName}
                  // onUploadComplete={() => {
                  //   alert("✅ Files uploaded successfully!");
                  //   // navigate("/f-dashboard"); // ✅ navigate AFTER upload done
                  // }}
                  onUploadComplete={() => setCurrentStep(4)}
                />
              )}
              {/* Step 4: Questionnaire */}
              {currentStep === 4 && (
                <StartupQuestionnaire
                  userEmail={formData.emailId}
                  onComplete={() => {
                    // ✅ After questionnaire done, auto-navigate or show final message
                    alert("✅ Registration & voice verification completed!");
                    navigate("/f-dashboard");
                  }}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
