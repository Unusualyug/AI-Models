// import React, { useState } from "react";

// export default function FractureDetector({ model }) {
//   const [selectedFile, setSelectedFile] = useState(null);
//   const [preview, setPreview] = useState(null);
//   const [result, setResult] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);

//   const API_URL = "http://localhost:8000";

//   const handleFileChange = (e) => {
//     const file = e.target.files[0];
//     if (file) {
//       setSelectedFile(file);
//       setPreview(URL.createObjectURL(file));
//       setResult(null);
//       setError(null);
//     }
//   };

//   const handleUpload = async () => {
//     if (!selectedFile) {
//       setError("Please select an image first.");
//       return;
//     }

//     setLoading(true);
//     setError(null);
//     setResult(null);

//     const formData = new FormData();
//     formData.append("file", selectedFile);
//     formData.append("include_heatmap", "true");

//     try {
//       const response = await fetch(`${API_URL}/predict`, {
//         method: "POST",
//         body: formData,
//         cache: "no-store",
//       });

//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || "Prediction failed.");
//       }

//       const data = await response.json();
//       setResult(data);

//       const fileInput = document.getElementById("file-upload");
//       if (fileInput) fileInput.value = "";
//     } catch (err) {
//       setError(err.message);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 pt-24 pb-20 px-4">
//       <div className="max-w-4xl mx-auto">
//         <h1 className="text-4xl font-bold text-white text-center mb-8">
//           {model?.name || "Fracture Detection"}
//         </h1>
//         <p className="text-blue-200 text-center mb-10 text-lg">
//           Upload an X-ray image to detect fractures using AI
//         </p>

//         {/* Upload Section */}
//         <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 mb-8">
//           <input
//             id="file-upload"
//             type="file"
//             accept="image/*"
//             onChange={handleFileChange}
//             className="hidden"
//           />
//           <label
//             htmlFor="file-upload"
//             className="block border-2 border-dashed border-blue-400/50 rounded-xl p-12 text-center cursor-pointer hover:border-blue-400 hover:bg-blue-500/5 transition-all"
//           >
//             {preview ? (
//               <div>
//                 <img
//                   src={preview}
//                   alt="Preview"
//                   className="max-h-64 mx-auto rounded-lg mb-4"
//                 />
//                 <p className="text-blue-200">Click to change image</p>
//               </div>
//             ) : (
//               <div>
//                 <div className="text-5xl mb-4">🩻</div>
//                 <p className="text-white text-lg font-semibold">
//                   Click to upload X-ray image
//                 </p>
//                 <p className="text-blue-300 text-sm mt-2">
//                   Supports JPG, PNG, BMP
//                 </p>
//               </div>
//             )}
//           </label>

//           {selectedFile && (
//             <button
//               onClick={handleUpload}
//               disabled={loading}
//               className="w-full mt-6 py-4 bg-gradient-to-r from-blue-500 to-cyan-500
//                             text-white rounded-xl font-bold text-lg hover:from-blue-600 hover:to-cyan-600
//                             transition-all disabled:opacity-50 disabled:cursor-not-allowed"
//             >
//               {loading ? (
//                 <span>Analyzing... Please wait</span>
//               ) : (
//                 <span>Analyze Image</span>
//               )}
//             </button>
//           )}

//           {error && (
//             <div className="mt-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
//               <p className="text-red-300">{error}</p>
//             </div>
//           )}
//         </div>

//         {/* Result Section */}
//         {result && (
//           <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
//             <div className="text-center mb-6">
//               <div
//                 className={`inline-block px-6 py-3 rounded-full text-2xl font-bold mb-4
//                                 ${
//                                   result.prediction === "Fracture Detected"
//                                     ? "bg-red-500/20 text-red-400 border border-red-500/50"
//                                     : "bg-green-500/20 text-green-400 border border-green-500/50"
//                                 }`}
//               >
//                 {result.prediction}
//               </div>
//               <p className="text-blue-200 text-lg">
//                 Confidence:{" "}
//                 <span className="text-white font-bold">
//                   {result.confidence_percentage}%
//                 </span>
//               </p>
//             </div>

//             {/* Probabilities */}
//             <div className="space-y-3">
//               {result.probabilities &&
//                 Object.entries(result.probabilities).map(([key, value]) => (
//                   <div key={key} className="flex items-center">
//                     <span className="text-blue-200 w-36 capitalize">
//                       {key.replace("_", " ")}
//                     </span>
//                     <div className="flex-1 bg-white/10 rounded-full h-3 mx-2">
//                       <div
//                         className={`h-3 rounded-full ${key === "fractured" ? "bg-red-500" : "bg-green-500"}`}
//                         style={{ width: `${value * 100}%` }}
//                       />
//                     </div>
//                     <span className="text-white font-mono w-20 text-right">
//                       {(value * 100).toFixed(1)}%
//                     </span>
//                   </div>
//                 ))}
//             </div>

//             {/* Heatmap */}
//             {result.heatmap_data_url && (
//               <div className="mt-8">
//                 <h3 className="text-white font-semibold text-lg mb-4">
//                   Grad-CAM Heatmap
//                 </h3>
//                 <img
//                   src={result.heatmap_data_url}
//                   alt="Heatmap"
//                   className="max-w-full rounded-lg border border-white/20"
//                 />
//               </div>
//             )}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// import React, { useEffect, useMemo, useState } from "react";

// export default function FractureDetector({ model }) {
//   const [selectedFile, setSelectedFile] = useState(null);
//   const [preview, setPreview] = useState(null);
//   const [result, setResult] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);
//   const [animatedConfidence, setAnimatedConfidence] = useState(0);

//   const API_URL = "http://localhost:8000";

//   const handleFileChange = (e) => {
//     const file = e.target.files?.[0];
//     if (!file) return;

//     setSelectedFile(file);
//     setPreview(URL.createObjectURL(file));
//     setResult(null);
//     setError(null);
//   };

//   const handleUpload = async () => {
//     if (!selectedFile) {
//       setError("Please select an image first.");
//       return;
//     }

//     setLoading(true);
//     setError(null);
//     setResult(null);

//     const formData = new FormData();
//     formData.append("file", selectedFile);
//     formData.append("include_heatmap", "true");

//     try {
//       const response = await fetch(`${API_URL}/predict`, {
//         method: "POST",
//         body: formData,
//         cache: "no-store",
//       });

//       if (!response.ok) {
//         let detail = "Prediction failed.";
//         try {
//           const errorData = await response.json();
//           detail = errorData.detail || detail;
//         } catch {
//           // Keep the default message when the server does not return JSON.
//         }
//         throw new Error(detail);
//       }

//       const data = await response.json();
//       setResult(data);

//       const fileInput = document.getElementById("file-upload");
//       if (fileInput) fileInput.value = "";
//     } catch (err) {
//       setError(err.message || "Unable to connect to the prediction server.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   const probabilities = useMemo(() => {
//     if (!result?.probabilities) return [];

//     return Object.entries(result.probabilities).map(([key, value]) => ({
//       key,
//       label: key.replaceAll("_", " "),
//       value: Number(value) || 0,
//       percentage: ((Number(value) || 0) * 100).toFixed(1),
//     }));
//   }, [result]);

//   const confidence = Number(result?.confidence) || 0;

//   useEffect(() => {
//     if (!result) {
//       setAnimatedConfidence(0);
//       return;
//     }

//     setAnimatedConfidence(0);
//     const timer = setTimeout(() => setAnimatedConfidence(confidence), 120);
//     return () => clearTimeout(timer);
//   }, [result, confidence]);
//   const confidencePercentage =
//     result?.confidence_percentage ?? (confidence * 100).toFixed(2);
//   const isFracture = result?.prediction === "Fracture Detected";

//   return (
//     <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#1e40af_0%,_#0f172a_48%,_#020617_100%)] pt-24 pb-20 px-4 text-white">
//       <div className="max-w-6xl mx-auto">
//         <div className="text-center mb-10">
//           <p className="text-cyan-300 uppercase tracking-[0.25em] text-xs font-bold mb-3">
//             MedVision AI Diagnostics
//           </p>
//           <h1 className="text-4xl md:text-5xl font-black tracking-tight">
//             {model?.name || "Fracture Detection"}
//           </h1>
//           <p className="text-blue-200 mt-4 text-lg">
//             Upload an X-ray image for an AI-assisted fracture screening result.
//           </p>
//         </div>

//         <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-8 items-start">
//           {/* Upload panel */}
//           <section className="rounded-3xl border border-white/15 bg-white/[0.08] backdrop-blur-xl p-6 md:p-8 shadow-2xl shadow-blue-950/30">
//             <div className="flex items-center justify-between mb-6">
//               <div>
//                 <p className="text-white font-bold text-xl">Upload X-ray</p>
//                 <p className="text-blue-200 text-sm mt-1">
//                   JPG, PNG, or BMP images
//                 </p>
//               </div>
//               <div className="h-11 w-11 rounded-2xl bg-cyan-400/15 border border-cyan-300/20 flex items-center justify-center text-2xl">
//                 🩻
//               </div>
//             </div>

//             <input
//               id="file-upload"
//               type="file"
//               accept="image/*"
//               onChange={handleFileChange}
//               className="hidden"
//             />

//             <label
//               htmlFor="file-upload"
//               className="min-h-[330px] border-2 border-dashed border-cyan-300/30 rounded-2xl flex items-center justify-center text-center cursor-pointer hover:border-cyan-300/70 hover:bg-cyan-300/5 transition-all p-6"
//             >
//               {preview ? (
//                 <div>
//                   <img
//                     src={preview}
//                     alt="Selected X-ray preview"
//                     className="max-h-72 max-w-full mx-auto rounded-xl object-contain shadow-xl"
//                   />
//                   <p className="text-cyan-200 text-sm mt-4">
//                     Click to choose another image
//                   </p>
//                 </div>
//               ) : (
//                 <div>
//                   <div className="text-6xl mb-5">📤</div>
//                   <p className="text-white text-lg font-bold">
//                     Click to upload an X-ray
//                   </p>
//                   <p className="text-blue-300 text-sm mt-2">
//                     Drag and drop is also supported by your browser
//                   </p>
//                 </div>
//               )}
//             </label>

//             {selectedFile && (
//               <button
//                 onClick={handleUpload}
//                 disabled={loading}
//                 className="w-full mt-6 py-4 rounded-2xl bg-gradient-to-r from-blue-500 via-cyan-500 to-teal-400 font-extrabold text-lg shadow-lg shadow-cyan-500/20 hover:brightness-110 transition disabled:opacity-50 disabled:cursor-not-allowed"
//               >
//                 {loading ? "Analyzing image..." : "Analyze Image"}
//               </button>
//             )}

//             {error && (
//               <div className="mt-5 rounded-xl border border-red-400/40 bg-red-500/15 px-4 py-3 text-red-200 text-sm">
//                 {error}
//               </div>
//             )}
//           </section>

//           {/* Result panel */}
//           {result ? (
//             <section className="result-enter rounded-3xl border border-white/15 bg-white/[0.08] backdrop-blur-xl p-6 md:p-8 shadow-2xl shadow-blue-950/30">
//               <style>{`
//                 @keyframes resultEnter {
//                   from { opacity: 0; transform: translateY(28px) scale(0.97); }
//                   to { opacity: 1; transform: translateY(0) scale(1); }
//                 }
//                 @keyframes ringPulse {
//                   0%, 100% { box-shadow: 0 0 0 0 rgba(34, 211, 238, 0); }
//                   50% { box-shadow: 0 0 0 12px rgba(34, 211, 238, 0.10); }
//                 }
//                 .result-enter { animation: resultEnter 650ms cubic-bezier(.22, 1, .36, 1) both; }
//                 .ring-pulse { animation: ringPulse 2.2s ease-in-out 700ms 2; }
//                 @media (prefers-reduced-motion: reduce) {
//                   .result-enter, .ring-pulse { animation: none; }
//                 }
//               `}</style>
//               <div className="flex items-center justify-between mb-6">
//                 <div>
//                   <p className="text-white font-bold text-xl">
//                     Analysis Summary
//                   </p>
//                   <p className="text-blue-200 text-sm mt-1">
//                     AI classification confidence
//                   </p>
//                 </div>
//                 <span className="text-xs px-3 py-1 rounded-full bg-white/10 text-cyan-200 border border-white/10">
//                   ResNet50
//                 </span>
//               </div>

//               <div className="flex flex-col sm:flex-row items-center gap-7 rounded-2xl bg-slate-950/25 p-5 mb-7">
//                 <div
//                   className={`ring-pulse relative h-40 w-40 rounded-full grid place-items-center ${isFracture ? "text-red-400" : "text-emerald-400"}`}
//                   style={{
//                     background: `conic-gradient(currentColor ${Math.min(animatedConfidence * 100, 100)}%, rgba(255,255,255,0.12) 0)`,
//                   }}
//                 >
//                   <div className="h-32 w-32 rounded-full bg-slate-900/95 grid place-items-center text-center">
//                     <div>
//                       <p className="text-3xl font-black">
//                         {confidencePercentage}%
//                       </p>
//                       <p className="text-[11px] uppercase tracking-wider text-blue-200 mt-1">
//                         Confidence
//                       </p>
//                     </div>
//                   </div>
//                 </div>

//                 <div className="text-center sm:text-left">
//                   <p className="text-xs uppercase tracking-[0.2em] text-blue-300 mb-2">
//                     Prediction
//                   </p>
//                   <h2
//                     className={`text-3xl font-black ${isFracture ? "text-red-300" : "text-emerald-300"}`}
//                   >
//                     {result.prediction}
//                   </h2>
//                   <p className="text-blue-200 text-sm mt-3">
//                     Review the heatmap below as an explanation of the model
//                     focus area.
//                   </p>
//                 </div>
//               </div>

//               <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-7">
//                 {probabilities.map(({ key, label, value, percentage }) => (
//                   <div
//                     key={key}
//                     className={`rounded-2xl p-4 border ${key === "fractured" ? "border-red-400/25 bg-red-400/10" : "border-emerald-400/25 bg-emerald-400/10"}`}
//                   >
//                     <div className="flex items-center justify-between mb-3">
//                       <span className="capitalize text-blue-100 font-semibold">
//                         {label}
//                       </span>
//                       <span className="font-black text-white">
//                         {percentage}%
//                       </span>
//                     </div>
//                     <div className="h-2 rounded-full bg-white/10 overflow-hidden">
//                       <div
//                         className={`h-full rounded-full transition-[width] duration-1000 ease-out ${key === "fractured" ? "bg-gradient-to-r from-red-500 to-orange-300" : "bg-gradient-to-r from-emerald-500 to-cyan-300"}`}
//                         style={{
//                           width: `${Math.min(animatedConfidence === 0 ? 0 : value * 100, 100)}%`,
//                         }}
//                       />
//                     </div>
//                   </div>
//                 ))}
//               </div>

//               {result.heatmap_data_url && (
//                 <div>
//                   <div className="flex items-center justify-between mb-4">
//                     <h3 className="text-white font-bold text-lg">
//                       Grad-CAM Explanation
//                     </h3>
//                     <span className="text-xs text-amber-200 bg-amber-400/10 border border-amber-300/20 rounded-full px-3 py-1">
//                       Areas of focus
//                     </span>
//                   </div>
//                   <div className="rounded-2xl border border-white/15 bg-black/20 p-3">
//                     <img
//                       src={result.heatmap_data_url}
//                       alt="Grad-CAM heatmap showing model focus"
//                       className="w-full max-h-80 object-contain rounded-xl"
//                     />
//                   </div>
//                 </div>
//               )}
//             </section>
//           ) : (
//             <section className="hidden lg:flex min-h-[520px] rounded-3xl border border-white/10 bg-white/[0.04] items-center justify-center text-center p-10">
//               <div>
//                 <div className="text-6xl mb-5">◉</div>
//                 <h2 className="text-2xl font-bold text-white">
//                   Your analysis will appear here
//                 </h2>
//                 <p className="text-blue-200 max-w-sm mt-3">
//                   Upload an X-ray to view the prediction, confidence
//                   distribution, and Grad-CAM explanation.
//                 </p>
//               </div>
//             </section>
//           )}
//         </div>

//         <p className="text-center text-blue-300/70 text-xs mt-8">
//           This tool is intended for research and educational assistance and does
//           not replace professional medical diagnosis.
//         </p>
//       </div>
//     </div>
//   );
// }

/*
  Replace your existing:
  frontend/src/components/models/FractureDetector.jsx
  with this file.

  This version uses Tailwind CSS only; no chart library is required.
*/

import React, { useEffect, useMemo, useState } from "react";

export default function FractureDetector({ model }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [animatedConfidence, setAnimatedConfidence] = useState(0);

  const API_URL = "http://localhost:8000";

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", selectedFile);
    formData.append("include_heatmap", "true");

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        body: formData,
        cache: "no-store",
      });

      if (!response.ok) {
        let detail = "Prediction failed.";
        try {
          const errorData = await response.json();
          detail = errorData.detail || detail;
        } catch {
          // Keep the default message when the server does not return JSON.
        }
        throw new Error(detail);
      }

      const data = await response.json();
      setResult(data);

      const fileInput = document.getElementById("file-upload");
      if (fileInput) fileInput.value = "";
    } catch (err) {
      setError(err.message || "Unable to connect to the prediction server.");
    } finally {
      setLoading(false);
    }
  };

  const probabilities = useMemo(() => {
    if (!result?.probabilities) return [];

    return Object.entries(result.probabilities).map(([key, value]) => ({
      key,
      label: key.replaceAll("_", " "),
      value: Number(value) || 0,
      percentage: ((Number(value) || 0) * 100).toFixed(1),
    }));
  }, [result]);

  const confidence = Number(result?.confidence) || 0;

  useEffect(() => {
    if (!result) {
      setAnimatedConfidence(0);
      return;
    }

    setAnimatedConfidence(0);
    const timer = setTimeout(() => setAnimatedConfidence(confidence), 120);
    return () => clearTimeout(timer);
  }, [result, confidence]);
  const confidencePercentage =
    result?.confidence_percentage ?? (confidence * 100).toFixed(2);
  const isFracture =
    result?.class_name === "fracture" ||
    result?.prediction === "Fracture Detected";
  const isUncertain = Boolean(result?.review_required);

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#1e40af_0%,_#0f172a_48%,_#020617_100%)] pt-24 pb-20 px-4 text-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-10">
          <p className="text-cyan-300 uppercase tracking-[0.25em] text-xs font-bold mb-3">
            MedVision AI Diagnostics
          </p>
          <h1 className="text-4xl md:text-5xl font-black tracking-tight">
            {model?.name || "Fracture Detection"}
          </h1>
          <p className="text-blue-200 mt-4 text-lg">
            Upload an X-ray image for an AI-assisted fracture screening result.
          </p>
          <div className="max-w-3xl mx-auto mt-5 rounded-xl border border-amber-300/30 bg-amber-400/10 px-4 py-3 text-left text-sm text-amber-100">
            <strong>Research prototype:</strong> This tool is not a medical
            diagnosis. A qualified radiologist or doctor must review every X-ray
            and result.
          </div>
        </div>

        <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-8 items-start">
          {/* Upload panel */}
          <section className="rounded-3xl border border-white/15 bg-white/[0.08] backdrop-blur-xl p-6 md:p-8 shadow-2xl shadow-blue-950/30">
            <div className="flex items-center justify-between mb-6">
              <div>
                <p className="text-white font-bold text-xl">Upload X-ray</p>
                <p className="text-blue-200 text-sm mt-1">
                  JPG, PNG, or BMP images
                </p>
              </div>
              <div className="h-11 w-11 rounded-2xl bg-cyan-400/15 border border-cyan-300/20 flex items-center justify-center text-2xl">
                🩻
              </div>
            </div>

            <input
              id="file-upload"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />

            <label
              htmlFor="file-upload"
              className="min-h-[330px] border-2 border-dashed border-cyan-300/30 rounded-2xl flex items-center justify-center text-center cursor-pointer hover:border-cyan-300/70 hover:bg-cyan-300/5 transition-all p-6"
            >
              {preview ? (
                <div>
                  <img
                    src={preview}
                    alt="Selected X-ray preview"
                    className="max-h-72 max-w-full mx-auto rounded-xl object-contain shadow-xl"
                  />
                  <p className="text-cyan-200 text-sm mt-4">
                    Click to choose another image
                  </p>
                </div>
              ) : (
                <div>
                  <div className="text-6xl mb-5">📤</div>
                  <p className="text-white text-lg font-bold">
                    Click to upload an X-ray
                  </p>
                  <p className="text-blue-300 text-sm mt-2">
                    Drag and drop is also supported by your browser
                  </p>
                </div>
              )}
            </label>

            {selectedFile && (
              <button
                onClick={handleUpload}
                disabled={loading}
                className="w-full mt-6 py-4 rounded-2xl bg-gradient-to-r from-blue-500 via-cyan-500 to-teal-400 font-extrabold text-lg shadow-lg shadow-cyan-500/20 hover:brightness-110 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Analyzing image..." : "Analyze Image"}
              </button>
            )}

            {error && (
              <div className="mt-5 rounded-xl border border-red-400/40 bg-red-500/15 px-4 py-3 text-red-200 text-sm">
                {error}
              </div>
            )}
          </section>

          {/* Result panel */}
          {result ? (
            <section className="result-enter rounded-3xl border border-white/15 bg-white/[0.08] backdrop-blur-xl p-6 md:p-8 shadow-2xl shadow-blue-950/30">
              <style>{`
                @keyframes resultEnter {
                  from { opacity: 0; transform: translateY(28px) scale(0.97); }
                  to { opacity: 1; transform: translateY(0) scale(1); }
                }
                @keyframes ringPulse {
                  0%, 100% { box-shadow: 0 0 0 0 rgba(34, 211, 238, 0); }
                  50% { box-shadow: 0 0 0 12px rgba(34, 211, 238, 0.10); }
                }
                .result-enter { animation: resultEnter 650ms cubic-bezier(.22, 1, .36, 1) both; }
                .ring-pulse { animation: ringPulse 2.2s ease-in-out 700ms 2; }
                @media (prefers-reduced-motion: reduce) {
                  .result-enter, .ring-pulse { animation: none; }
                }
              `}</style>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-white font-bold text-xl">
                    Analysis Summary
                  </p>
                  <p className="text-blue-200 text-sm mt-1">
                    AI classification confidence
                  </p>
                </div>
                <span className="text-xs px-3 py-1 rounded-full bg-white/10 text-cyan-200 border border-white/10">
                  ResNet50
                </span>
              </div>

              <div className="flex flex-col sm:flex-row items-center gap-7 rounded-2xl bg-slate-950/25 p-5 mb-7">
                <div
                  className={`ring-pulse relative h-40 w-40 rounded-full grid place-items-center ${isFracture ? "text-red-400" : "text-emerald-400"}`}
                  style={{
                    background: `conic-gradient(currentColor ${Math.min(animatedConfidence * 100, 100)}%, rgba(255,255,255,0.12) 0)`,
                  }}
                >
                  <div className="h-32 w-32 rounded-full bg-slate-900/95 grid place-items-center text-center">
                    <div>
                      <p className="text-3xl font-black">
                        {confidencePercentage}%
                      </p>
                      <p className="text-[11px] uppercase tracking-wider text-blue-200 mt-1">
                        Confidence
                      </p>
                    </div>
                  </div>
                </div>

                <div className="text-center sm:text-left">
                  <p className="text-xs uppercase tracking-[0.2em] text-blue-300 mb-2">
                    Prediction
                  </p>
                  <h2
                    className={`text-3xl font-black ${isUncertain ? "text-amber-300" : isFracture ? "text-red-300" : "text-emerald-300"}`}
                  >
                    {isUncertain
                      ? "Uncertain Result"
                      : result.display_prediction || result.prediction}
                  </h2>
                  <p className="text-blue-200 text-sm mt-3">
                    Review the heatmap below as an explanation of the model
                    focus area.
                  </p>
                  <div
                    className={`mt-4 rounded-xl border px-4 py-3 text-sm ${isUncertain ? "border-amber-300/30 bg-amber-400/10 text-amber-100" : "border-red-300/20 bg-red-400/10 text-red-100"}`}
                  >
                    <strong>
                      {isUncertain
                        ? "Professional review required: "
                        : "Important: "}
                    </strong>
                    {result.review_message ||
                      "This is an experimental AI prediction and must not replace professional medical interpretation."}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-7">
                {probabilities.map(({ key, label, value, percentage }) => (
                  <div
                    key={key}
                    className={`rounded-2xl p-4 border ${key === "fractured" ? "border-red-400/25 bg-red-400/10" : "border-emerald-400/25 bg-emerald-400/10"}`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="capitalize text-blue-100 font-semibold">
                        {label}
                      </span>
                      <span className="font-black text-white">
                        {percentage}%
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-white/10 overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-[width] duration-1000 ease-out ${key === "fractured" ? "bg-gradient-to-r from-red-500 to-orange-300" : "bg-gradient-to-r from-emerald-500 to-cyan-300"}`}
                        style={{
                          width: `${Math.min(animatedConfidence === 0 ? 0 : value * 100, 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {result.heatmap_data_url && (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-white font-bold text-lg">
                      Grad-CAM Explanation
                    </h3>
                    <span className="text-xs text-amber-200 bg-amber-400/10 border border-amber-300/20 rounded-full px-3 py-1">
                      Areas of focus
                    </span>
                  </div>
                  <div className="rounded-2xl border border-white/15 bg-black/20 p-3">
                    <img
                      src={result.heatmap_data_url}
                      alt="Grad-CAM heatmap showing model focus"
                      className="w-full max-h-80 object-contain rounded-xl"
                    />
                  </div>
                </div>
              )}
            </section>
          ) : (
            <section className="hidden lg:flex min-h-[520px] rounded-3xl border border-white/10 bg-white/[0.04] items-center justify-center text-center p-10">
              <div>
                <div className="text-6xl mb-5">◉</div>
                <h2 className="text-2xl font-bold text-white">
                  Your analysis will appear here
                </h2>
                <p className="text-blue-200 max-w-sm mt-3">
                  Upload an X-ray to view the prediction, confidence
                  distribution, and Grad-CAM explanation.
                </p>
              </div>
            </section>
          )}
        </div>

        <p className="text-center text-amber-200/80 text-xs mt-8">
          Research and educational assistance only. Never use this result alone
          for diagnosis or treatment decisions.
        </p>
      </div>
    </div>
  );
}

/*
  Replace your existing:
  frontend/src/components/models/FractureDetector.jsx
  with this file.

  This version uses Tailwind CSS only; no chart library is required.
*/
