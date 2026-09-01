import React, { useState } from "react";

const API_URL = "http://localhost:8000";

const ImageUploader = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Handle file selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    // Release previous preview URL to avoid memory leaks
    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setSelectedFile(file);
    setPreview(URL.createObjectURL(file));

    // Clear previous prediction
    setResult(null);
    setError(null);
  };

  // Upload image to backend
  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError(null);

    // Clear previous result before new prediction
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
        const errorData = await response.json();
        throw new Error(errorData.detail || "Prediction failed.");
      }

      const data = await response.json();

      setResult(data);

      // Allow uploading the same file again
      const fileInput = document.getElementById("file-upload");
      if (fileInput) {
        fileInput.value = "";
      }
    } catch (err) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  // Reset everything
  const handleReset = () => {
    if (preview) {
      URL.revokeObjectURL(preview);
    }

    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);

    const fileInput = document.getElementById("file-upload");
    if (fileInput) {
      fileInput.value = "";
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Fracture Detection</h1>

      <p style={styles.subtitle}>
        Upload an X-ray image to detect fractures using AI
      </p>

      {/* Upload Section */}

      <div style={styles.uploadSection}>
        <div style={styles.dropZone}>
          <input
            type="file"
            accept="image/*"
            id="file-upload"
            onChange={handleFileChange}
            style={styles.fileInput}
          />

          <label htmlFor="file-upload" style={styles.uploadLabel}>
            <div style={styles.uploadIcon}>+</div>

            <p style={styles.uploadText}>
              {selectedFile ? selectedFile.name : "Click to upload X-ray image"}
            </p>

            <p style={styles.uploadHint}>Supports JPG, PNG, BMP, TIFF</p>
          </label>
        </div>

        {/* Preview */}

        {preview && (
          <div style={styles.previewContainer}>
            <img
              src={preview}
              alt="X-ray Preview"
              style={styles.previewImage}
            />
          </div>
        )}

        {/* Buttons */}

        <div style={styles.buttonGroup}>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || loading}
            style={{
              ...styles.button,
              ...styles.primaryButton,
              opacity: !selectedFile || loading ? 0.5 : 1,
            }}
          >
            {loading ? "Analyzing..." : "Analyze Image"}
          </button>

          {result && (
            <button onClick={handleReset} style={styles.button}>
              Reset
            </button>
          )}
        </div>

        {/* Error */}

        {error && <div style={styles.errorBox}>{error}</div>}
      </div>

      {/* Results */}

      {result && (
        <div style={styles.resultsSection}>
          <h2 style={styles.resultsTitle}>Prediction Result</h2>

          <div style={styles.resultCard}>
            {/* Prediction */}

            <div
              style={{
                ...styles.predictionBanner,
                backgroundColor:
                  result.prediction === "Fracture Detected"
                    ? "#ffebee"
                    : "#e8f5e9",

                borderColor:
                  result.prediction === "Fracture Detected"
                    ? "#f44336"
                    : "#4caf50",
              }}
            >
              <div style={styles.predictionLabel}>
                {result.prediction === "Fracture Detected"
                  ? "FRACTURE DETECTED"
                  : "NO FRACTURE"}
              </div>

              <div style={styles.confidenceScore}>
                Confidence: {result.confidence_percentage}%
              </div>
            </div>

            {/* Confidence Bar */}

            <div style={styles.confidenceBarContainer}>
              <div style={styles.confidenceBarLabel}>Confidence Level</div>

              <div style={styles.confidenceBarTrack}>
                <div
                  style={{
                    ...styles.confidenceBarFill,
                    width: `${result.confidence_percentage}%`,
                    backgroundColor:
                      result.prediction === "Fracture Detected"
                        ? "#f44336"
                        : "#4caf50",
                  }}
                />
              </div>

              <div style={styles.confidenceBarPercent}>
                {result.confidence_percentage}%
              </div>
            </div>

            {/* Class Probabilities */}

            <div style={styles.probabilitiesSection}>
              <h3 style={styles.probTitle}>Class Probabilities</h3>

              <div style={styles.probRow}>
                <span style={styles.probLabel}>Fractured</span>

                <span style={styles.probValue}>
                  {((result.probabilities?.fractured || 0) * 100).toFixed(2)}%
                </span>
              </div>

              <div style={styles.probRow}>
                <span style={styles.probLabel}>No Fractured</span>

                <span style={styles.probValue}>
                  {((result.probabilities?.no_fractured || 0) * 100).toFixed(2)}
                  %
                </span>
              </div>
            </div>

            {/* Heatmap */}

            {result.heatmap_data_url && (
              <div style={styles.heatmapSection}>
                <h3 style={styles.probTitle}>
                  Grad-CAM Heatmap (Model Attention)
                </h3>

                <img
                  src={result.heatmap_data_url}
                  alt="Grad-CAM Heatmap"
                  style={styles.heatmapImage}
                />

                <p style={styles.heatmapCaption}>
                  Red and yellow regions indicate where the AI focused while
                  making its prediction.
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Loading */}

      {loading && <div style={styles.spinner}>Analyzing image...</div>}
    </div>
  );
};
const styles = {
  container: {
    maxWidth: "700px",
    margin: "0 auto",
    padding: "40px 20px",
    fontFamily: "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
  },

  title: {
    textAlign: "center",
    fontSize: "32px",
    color: "#1a1a2e",
    marginBottom: "8px",
  },

  subtitle: {
    textAlign: "center",
    fontSize: "16px",
    color: "#666",
    marginBottom: "32px",
  },

  uploadSection: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "20px",
  },

  dropZone: {
    width: "100%",
    border: "2px dashed #ccc",
    borderRadius: "12px",
    padding: "40px",
    textAlign: "center",
    backgroundColor: "#fafafa",
    transition: "border-color 0.2s",
  },

  fileInput: {
    display: "none",
  },

  uploadLabel: {
    cursor: "pointer",
  },

  uploadIcon: {
    fontSize: "48px",
    color: "#999",
    marginBottom: "12px",
  },

  uploadText: {
    fontSize: "16px",
    color: "#333",
    margin: "0 0 4px 0",
  },

  uploadHint: {
    fontSize: "13px",
    color: "#999",
    margin: "0",
  },

  previewContainer: {
    width: "100%",
    maxWidth: "300px",
    borderRadius: "8px",
    overflow: "hidden",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  },

  previewImage: {
    width: "100%",
    display: "block",
  },

  buttonGroup: {
    display: "flex",
    gap: "12px",
    justifyContent: "center",
    marginTop: "8px",
  },

  button: {
    padding: "12px 32px",
    fontSize: "15px",
    border: "1px solid #ccc",
    borderRadius: "8px",
    backgroundColor: "#fff",
    cursor: "pointer",
    fontWeight: "500",
    transition: "background-color 0.2s",
  },

  primaryButton: {
    backgroundColor: "#1a73e8",
    color: "#fff",
    border: "none",
  },

  errorBox: {
    padding: "12px 16px",
    backgroundColor: "#ffebee",
    color: "#c62828",
    borderRadius: "8px",
    fontSize: "14px",
    width: "100%",
    textAlign: "center",
  },

  resultsSection: {
    marginTop: "40px",
    borderTop: "1px solid #eee",
    paddingTop: "32px",
  },

  resultsTitle: {
    textAlign: "center",
    fontSize: "24px",
    color: "#1a1a2e",
    marginBottom: "24px",
  },

  resultCard: {
    borderRadius: "12px",
    padding: "24px",
    backgroundColor: "#fff",
    boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
  },

  predictionBanner: {
    padding: "20px",
    borderRadius: "8px",
    textAlign: "center",
    borderWidth: "2px",
    borderStyle: "solid",
    marginBottom: "24px",
  },

  predictionLabel: {
    fontSize: "24px",
    fontWeight: "bold",
    marginBottom: "8px",
  },

  confidenceScore: {
    fontSize: "16px",
    color: "#555",
  },

  confidenceBarContainer: {
    marginBottom: "24px",
  },

  confidenceBarLabel: {
    fontSize: "13px",
    color: "#666",
    marginBottom: "6px",
  },

  confidenceBarTrack: {
    height: "10px",
    backgroundColor: "#e0e0e0",
    borderRadius: "5px",
    overflow: "hidden",
  },

  confidenceBarFill: {
    height: "100%",
    borderRadius: "5px",
    transition: "width 0.5s ease",
  },

  confidenceBarPercent: {
    textAlign: "right",
    fontSize: "12px",
    color: "#999",
    marginTop: "4px",
  },

  probabilitiesSection: {
    marginBottom: "24px",
  },

  probTitle: {
    fontSize: "14px",
    color: "#333",
    marginBottom: "12px",
  },

  probRow: {
    display: "flex",
    justifyContent: "space-between",
    padding: "8px 0",
    borderBottom: "1px solid #f0f0f0",
    fontSize: "14px",
  },

  probLabel: {
    color: "#555",
  },

  probValue: {
    fontWeight: "bold",
    color: "#333",
  },

  heatmapSection: {
    marginTop: "24px",
    textAlign: "center",
  },

  heatmapImage: {
    width: "100%",
    maxWidth: "300px",
    borderRadius: "8px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  },

  heatmapCaption: {
    fontSize: "12px",
    color: "#999",
    marginTop: "8px",
  },

  spinner: {
    textAlign: "center",
    padding: "20px",
    color: "#1a73e8",
    fontSize: "16px",
    marginTop: "16px",
  },
};

export default ImageUploader;
