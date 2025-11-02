// import React, { useCallback, useState } from "react";
// import { useDropzone } from "react-dropzone";
// import axios from "axios";

// export default function StartupDocumentUploader({
//   emailId,
//   startupName,
//   onUploadComplete,
// }) {
//   const [files, setFiles] = useState([]);
//   const [uploading, setUploading] = useState(false);

//   const [progress, setProgress] = useState(0);
//   const [error, setError] = useState(null);

//   const onDrop = useCallback((acceptedFiles) => {
//     setFiles((prev) => {
//       const map = new Map(prev.map((f) => [f.name + f.size, f]));
//       acceptedFiles.forEach((f) => map.set(f.name + f.size, f));
//       return Array.from(map.values());
//     });
//   }, []);

//   const { getRootProps, getInputProps, isDragActive } = useDropzone({
//     onDrop,
//     accept: {
//       "application/pdf": [".pdf"],
//       "application/vnd.ms-powerpoint": [".ppt", ".pptx"],
//     },
//     multiple: true,
//   });

//   const handleUpload = async () => {
//     if (!files.length) return setError("Please select at least one file.");
//     if (!emailId || !startupName)
//       return setError(
//         "Missing startup name or email. Please go back and complete Step 1 & 2."
//       );

//     setUploading(true);
//     setProgress(0);
//     setError(null);

//     try {
//       const formData = new FormData();
//       files.forEach((f) => formData.append("files", f));
//       formData.append("emailId", emailId);
//       formData.append("startupName", startupName);
//       console.log(formData);

//       await axios.post("https://final-be-753168549263.us-central1.run.app/upload-and-analyze", formData, {
//         headers: { "Content-Type": "multipart/form-data" },
//         onUploadProgress: (p) =>
//           setProgress(Math.round((p.loaded * 100) / (p.total || 1))),
//       });

//       onUploadComplete(emailId);
//     } catch (err) {
//       setError(err?.response?.data?.detail || err.message || "Upload failed");
//     } finally {
//       setUploading(false);
//     }
//   };

//   return (
//     <div className="p-4">
//       <h4 style={{ color: "rgb(18,0,94)", fontWeight: "bold" }}>
//         Upload Pitch Deck & Supporting Documents
//       </h4>
//       <p className="text-muted mb-3">
//         Accepted formats: <strong>PDF</strong>, <strong>PPT</strong>,{" "}
//         <strong>PPTX</strong>
//       </p>

//       {/* Drag & Drop Box */}
//       <div
//         {...getRootProps()}
//         className="border border-2 rounded p-5 text-center mb-3"
//         style={{
//           borderStyle: "dashed",
//           borderColor: "rgb(18,0,94)",
//           backgroundColor: "#fafafa",
//           cursor: "pointer",
//         }}
//       >
//         <input {...getInputProps()} />
//         <p className="m-0" style={{ color: "rgb(18,0,94)" }}>
//           {isDragActive
//             ? "Drop the files here..."
//             : "Drag & drop files here or click to browse"}
//         </p>
//       </div>

//       {/* File List */}
//       {files.length > 0 && (
//         <ul className="list-group mb-3">
//           {files.map((f, i) => (
//             <li
//               key={f.name + f.size + i}
//               className="list-group-item d-flex justify-content-between"
//             >
//               {f.name}
//               <span className="text-muted">
//                 {(f.size / 1024).toFixed(2)} KB
//               </span>
//             </li>
//           ))}
//         </ul>
//       )}

//       {/* Error Message */}
//       {error && <div className="alert alert-danger py-2">{error}</div>}

//       {/* Upload Button & Progress */}
//       <button
//         className="btn px-4"
//         onClick={handleUpload}
//         disabled={uploading || !files.length}
//         style={{
//           backgroundColor: "rgb(18,0,94)",
//           color: "white",
//           fontWeight: "bold",
//         }}
//       >
//         {uploading ? `Uploading... ${progress}%` : "Upload & Analyze"}
//       </button>

//       {uploading && (
//         <div className="progress mt-2" style={{ height: "6px" }}>
//           <div
//             className="progress-bar"
//             role="progressbar"
//             style={{ width: `${progress}%`, backgroundColor: "rgb(18,0,94)" }}
//           ></div>
//         </div>
//       )}
//     </div>
//   );
// }

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";

export default function StartupDocumentUploader({
  emailId,
  startupName,
  onUploadComplete, // callback to move to next step
}) {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false); // spinner before questionnaire
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prev) => {
      const map = new Map(prev.map((f) => [f.name + f.size, f]));
      acceptedFiles.forEach((f) => map.set(f.name + f.size, f));
      return Array.from(map.values());
    });
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.ms-powerpoint": [".ppt", ".pptx"],
    },
    multiple: true,
  });

  const handleUpload = async () => {
    if (!files.length) return setError("Please select at least one file.");
    if (!emailId || !startupName)
      return setError(
        "Missing startup name or email. Please complete Step 1 & 2."
      );

    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      files.forEach((f) => formData.append("files", f));
      formData.append("emailId", emailId);
      formData.append("startupName", startupName);

      await axios.post(
        "https://final-be-753168549263.us-central1.run.app/upload-and-analyze",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
          onUploadProgress: (p) =>
            setProgress(Math.round((p.loaded * 100) / (p.total || 1))),
        }
      );

      // Show spinner before moving to Step 4
      setLoading(true);
      setTimeout(() => {
        setLoading(false);
        onUploadComplete(); // move to questionnaire
      }, 2500); // simulate 2.5s preparation delay
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  // Render
  if (loading) {
    return (
      <div style={{ textAlign: "center", paddingTop: "120px" }}>
        <div className="spinner" />
        <p
          style={{
            marginTop: "16px",
            fontSize: "18px",
            color: "#333",
          }}
        >
          Preparing your personalized voice questions...
        </p>
        <style>
          {`
            .spinner {
              margin: 20px auto;
              width: 60px;
              height: 60px;
              border: 7px solid #e0e0e0;
              border-top: 7px solid #1A73E8;
              border-radius: 50%;
              animation: spin 1s linear infinite;
            }
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  return (
    <div className="p-4">
      <h4 style={{ color: "rgb(18,0,94)", fontWeight: "bold" }}>
        Upload Pitch Deck & Supporting Documents
      </h4>
      <p className="text-muted mb-3">
        Accepted formats: <strong>PDF</strong>, <strong>PPT</strong>,{" "}
        <strong>PPTX</strong>
      </p>

      <div
        {...getRootProps()}
        className="border border-2 rounded p-5 text-center mb-3"
        style={{
          borderStyle: "dashed",
          borderColor: "rgb(18,0,94)",
          backgroundColor: "#fafafa",
          cursor: "pointer",
        }}
      >
        <input {...getInputProps()} />
        <p className="m-0" style={{ color: "rgb(18,0,94)" }}>
          {isDragActive
            ? "Drop the files here..."
            : "Drag & drop files here or click to browse"}
        </p>
      </div>

      {files.length > 0 && (
        <ul className="list-group mb-3">
          {files.map((f, i) => (
            <li
              key={f.name + f.size + i}
              className="list-group-item d-flex justify-content-between"
            >
              {f.name}
              <span className="text-muted">
                {(f.size / 1024).toFixed(2)} KB
              </span>
            </li>
          ))}
        </ul>
      )}

      {error && <div className="alert alert-danger py-2">{error}</div>}

      <button
        className="btn px-4"
        onClick={handleUpload}
        disabled={uploading || !files.length}
        style={{
          backgroundColor: "rgb(18,0,94)",
          color: "white",
          fontWeight: "bold",
        }}
      >
        {uploading ? `Uploading... ${progress}%` : "Upload & Analyze"}
      </button>

      {uploading && (
        <div className="progress mt-2" style={{ height: "6px" }}>
          <div
            className="progress-bar"
            role="progressbar"
            style={{ width: `${progress}%`, backgroundColor: "rgb(18,0,94)" }}
          ></div>
        </div>
      )}
    </div>
  );
}
