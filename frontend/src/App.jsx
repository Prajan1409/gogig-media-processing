import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "https://gogig-media-processing.onrender.com";

function App() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // =========================================================
  // FILE SELECTION
  // =========================================================

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) return;

    setFile(selectedFile);
    setResult(null);

    const url = URL.createObjectURL(selectedFile);
    setPreviewUrl(url);
  };

  // =========================================================
  // CLEAN PREVIEW URL
  // =========================================================

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  // =========================================================
  // CHECK PROCESSING STATUS
  // =========================================================

  const checkProcessingStatus = async (processingId) => {
    try {
      const response = await fetch(
        `${API_URL}/images/${processingId}/status`
      );

      const statusData = await response.json();

      if (!response.ok) {
        throw new Error(
          statusData.detail ||
            "Unable to check processing status"
        );
      }

      // COMPLETED
      if (statusData.status === "completed") {
        const resultResponse = await fetch(
          `${API_URL}/images/${processingId}/results`
        );

        const resultData = await resultResponse.json();

        if (!resultResponse.ok) {
          throw new Error(
            resultData.detail ||
              "Unable to fetch analysis results"
          );
        }

        setResult(resultData);
        setLoading(false);

        return;
      }

      // FAILED
      if (statusData.status === "failed") {
        setResult({
          error:
            statusData.failure_reason ||
            "Image processing failed"
        });

        setLoading(false);

        return;
      }

      // STILL PROCESSING
      setResult({
        processing_id: processingId,
        status: statusData.status,
        filename: file?.name
      });

      setTimeout(() => {
        checkProcessingStatus(processingId);
      }, 1000);

    } catch (error) {
      setResult({
        error: error.message
      });

      setLoading(false);
    }
  };

  // =========================================================
  // UPLOAD IMAGE
  // =========================================================

  const uploadImage = async () => {
    if (!file) return;

    setLoading(true);
    setResult(null);

    const formData = new FormData();

    formData.append("file", file);

    try {
      const response = await fetch(
        `${API_URL}/images`,
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Upload failed"
        );
      }

      setResult(data);

      checkProcessingStatus(
        data.processing_id
      );

    } catch (error) {
      setResult({
        error: error.message
      });

      setLoading(false);
    }
  };

  // =========================================================
  // RESET
  // =========================================================

  const resetAnalysis = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    setFile(null);
    setPreviewUrl(null);
    setResult(null);
    setLoading(false);
  };

  // =========================================================
  // ACTUAL BACKEND ANALYSIS DATA
  // =========================================================

  const analysis = result?.analysis;

  const blurAnalysis =
    analysis?.blur_analysis || {};

  const brightnessAnalysis =
    analysis?.brightness_analysis || {};

  const duplicateDetection =
    analysis?.duplicate_detection || {};

  const dimensionValidation =
    analysis?.dimension_validation || {};

  const ocrAnalysis =
    analysis?.ocr || {};

  const photoAnalysis =
    analysis?.photo_of_photo || {};

  const overallAnalysis =
    analysis?.overall || {};

  // =========================================================
  // STATUS CLASS
  // =========================================================

  const getStatusClass = (value) => {
    if (!value) {
      return "neutral";
    }

    const text =
      String(value).toLowerCase();

    if (
      text.includes("good") ||
      text.includes("sharp") ||
      text.includes("normal") ||
      text.includes("valid") ||
      text.includes("original") ||
      text.includes("success") ||
      text === "completed" ||
      text === "unique"
    ) {
      return "success";
    }

    if (
      text.includes("duplicate") ||
      text.includes("moderate") ||
      text.includes("acceptable") ||
      text.includes("possible") ||
      text.includes("warning")
    ) {
      return "warning";
    }

    if (
      text.includes("poor") ||
      text.includes("blurry") ||
      text.includes("dark") ||
      text.includes("bright") ||
      text.includes("failed") ||
      text.includes("error")
    ) {
      return "danger";
    }

    return "neutral";
  };

  // =========================================================
  // DUPLICATE STATUS
  // =========================================================

  const getDuplicateStatus = () => {
    const isDuplicate =
      duplicateDetection.is_duplicate === true;

    return {
      label: isDuplicate
        ? "Duplicate"
        : "Unique",

      className: isDuplicate
        ? "warning"
        : "success"
    };
  };

  const duplicateStatus =
    getDuplicateStatus();

  // =========================================================
  // OCR TEXT
  // =========================================================

  const getOCRText = () => {
    if (!ocrAnalysis) {
      return "No OCR result available";
    }

    if (ocrAnalysis.text) {
      return ocrAnalysis.text;
    }

    return (
      ocrAnalysis.message ||
      "No text detected"
    );
  };

  // =========================================================
  // RENDER
  // =========================================================

  return (
    <div className="app">

      {/* =====================================================
          NAVBAR
      ===================================================== */}

      <nav className="navbar">

        <div className="brand">

          {/* ACTUAL GOGIG LOGO */}

          <div className="brand-icon">
            <img
              src="/gogig-logo.png"
              alt="gOGig logo"
            />
          </div>

          <div>

            <h2>
              gOGig
            </h2>

            <span>
              Intelligent Media Processing
            </span>

          </div>

        </div>


        <div className="nav-right">

          <div className="nav-link active">
            Analyze
          </div>

          <div className="nav-status">

            <span className="status-dot"></span>

            API Online

          </div>

        </div>

      </nav>


      {/* =====================================================
          MAIN
      ===================================================== */}

      <main>

        {/* ===================================================
            HERO
        =================================================== */}

        <section className="hero">

          <div className="hero-topline">

            <span className="hero-label">
              gOGig / MEDIA ANALYSIS
            </span>

            <span className="hero-version">
              v1.0
            </span>

          </div>


          <h1>

            Intelligent
            <span>
              {" "}Media Analysis
            </span>

          </h1>


          <p>

            Upload an image and let gOGig
            automatically evaluate image quality,
            dimensions, OCR, duplicates and
            photo authenticity signals.

          </p>

        </section>


        {/* ===================================================
            WORKSPACE
        =================================================== */}

        <section className="workspace">


          {/* =================================================
              SOURCE IMAGE PANEL
          ================================================= */}

          <div className="source-panel">


            <div className="panel-heading">

              <div>

                <span className="eyebrow">
                  SOURCE IMAGE
                </span>

                <h2>
                  Upload & Analyze
                </h2>

              </div>

              <span className="panel-number">
                01
              </span>

            </div>


            {/* =================================================
                UPLOAD AREA
            ================================================= */}

            {!file ? (

              <label className="upload-zone">

                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                />

                <div className="upload-symbol">
                  ↑
                </div>

                <h3>
                  Drop your image here
                </h3>

                <p>
                  or click to browse from your computer
                </p>

                <span className="file-types">
                  JPG · JPEG · PNG · WEBP
                </span>

              </label>

            ) : (

              <div className="image-preview-wrapper">

                <div className="image-preview">

                  <img
                    src={previewUrl}
                    alt="Selected upload"
                  />

                  <div className="preview-overlay">

                    <span>
                      READY FOR ANALYSIS
                    </span>

                  </div>

                </div>


                <div className="selected-file">

                  <div>

                    <span>
                      SELECTED FILE
                    </span>

                    <strong>
                      {file.name}
                    </strong>

                  </div>


                  <span>

                    {(
                      file.size /
                      1024 /
                      1024
                    ).toFixed(2)} MB

                  </span>

                </div>

              </div>

            )}


            {/* =================================================
                BUTTONS
            ================================================= */}

            {file && (

              <div className="upload-actions">

                <button
                  className="analyze-button"
                  onClick={uploadImage}
                  disabled={loading}
                >

                  {loading ? (

                    <>

                      <span className="spinner"></span>

                      Processing...

                    </>

                  ) : (

                    <>

                      Analyze Image

                      <span>
                        →
                      </span>

                    </>

                  )}

                </button>


                <button
                  className="reset-button"
                  onClick={resetAnalysis}
                  disabled={loading}
                >
                  Change Image
                </button>

              </div>

            )}


            {/* =================================================
                ISSUE REPORT
            ================================================= */}

            {file && (

              <div className="issue-report">

                <div className="issue-report-header">

                  <div>

                    <span className="issue-eyebrow">
                      ISSUE REPORT
                    </span>

                    <h3>

                      {analysis
                        ? "Analysis Findings"
                        : "Awaiting Analysis"}

                    </h3>

                  </div>


                  {analysis && (

                    <span
                      className={`issue-count ${
                        overallAnalysis.issue_count > 0
                          ? "warning"
                          : "success"
                      }`}
                    >

                      {overallAnalysis.issue_count || 0}

                      {" "}

                      {overallAnalysis.issue_count === 1
                        ? "ISSUE"
                        : "ISSUES"}

                    </span>

                  )}

                </div>


                {/* BEFORE ANALYSIS */}

                {!analysis &&
                  !loading && (

                  <div className="issue-empty">

                    <div className="issue-status-icon neutral">
                      ◇
                    </div>

                    <div>

                      <strong>
                        No findings yet
                      </strong>

                      <p>
                        Run image analysis to identify
                        potential issues.
                      </p>

                    </div>

                  </div>

                )}


                {/* PROCESSING */}

                {loading && (

                  <div className="issue-empty">

                    <div className="issue-status-icon processing">

                      <span className="mini-spinner"></span>

                    </div>

                    <div>

                      <strong>
                        Analysis in progress
                      </strong>

                      <p>
                        Checking image quality,
                        duplicates and authenticity signals.
                      </p>

                    </div>

                  </div>

                )}


                {/* NO ISSUES */}

                {analysis &&
                  overallAnalysis.issue_count === 0 && (

                  <div className="issue-clear">

                    <div className="issue-status-icon success">
                      ✓
                    </div>

                    <div>

                      <strong>
                        No major issues detected
                      </strong>

                      <p>
                        {overallAnalysis.message ||
                          "Image passed the main quality checks."}
                      </p>

                    </div>

                  </div>

                )}


                {/* ISSUES FOUND */}

                {analysis &&
                  overallAnalysis.issue_count > 0 && (

                  <div className="issue-findings">

                    {overallAnalysis.issue_details?.map(
                      (issue, index) => (

                      <div
                        className="issue-finding"
                        key={index}
                      >

                        <div
                          className={`issue-status-icon ${
                            issue.severity === "error"
                              ? "danger"
                              : issue.severity === "warning"
                              ? "warning"
                              : "neutral"
                          }`}
                        >
                          !
                        </div>


                        <div className="issue-finding-content">

                          <div className="issue-finding-top">

                            <strong>
                              {issue.message}
                            </strong>

                            <span
                              className={`issue-severity ${
                                issue.severity
                              }`}
                            >
                              {issue.severity}
                            </span>

                          </div>


                          {issue.duplicate_file && (

                            <p>
                              Matched file:{" "}

                              <strong>
                                {issue.duplicate_file}
                              </strong>

                            </p>

                          )}

                        </div>

                      </div>

                    ))}


                    <div className="issue-recommendation">

                      <span>
                        RECOMMENDATION
                      </span>

                      <strong>
                        {overallAnalysis.recommendation ||
                          "Manual review recommended"}
                      </strong>

                    </div>

                  </div>

                )}

              </div>

            )}

          </div>


          {/* =================================================
              ANALYSIS PANEL
          ================================================= */}

          <div className="analysis-panel">


            <div className="panel-heading">

              <div>

                <span className="eyebrow">
                  HEURISTIC SUMMARY
                </span>

                <h2>
                  Analysis Results
                </h2>

              </div>

              <span className="panel-number">
                02
              </span>

            </div>


            {/* EMPTY STATE */}

            {!result && (

              <div className="empty-state">

                <div className="empty-symbol">
                  ◇
                </div>

                <h3>
                  Awaiting image
                </h3>

                <p>
                  Upload an image and start the analysis
                  to see your results here.
                </p>

              </div>

            )}


            {/* ERROR */}

            {result?.error && (

              <div className="error-box">

                <div className="result-icon">
                  !
                </div>

                <div>

                  <strong>
                    Processing Error
                  </strong>

                  <p>
                    {result.error}
                  </p>

                </div>

              </div>

            )}


            {/* RESULTS */}

            {result &&
              !result.error && (

              <div className="results-content">


                {/* PROCESSING */}

                {result.status !== "completed" && (

                  <div className="processing-card">

                    <div className="processing-spinner">
                      <span></span>
                    </div>

                    <div>

                      <span className="eyebrow">
                        PROCESSING
                      </span>

                      <h3>
                        {result.status === "processing"
                          ? "Analyzing image..."
                          : "Image queued"}
                      </h3>

                      <p>
                        gOGig is running the media
                        analysis pipeline.
                      </p>

                    </div>

                  </div>

                )}


                {/* COMPLETED */}

                {result.status === "completed" &&
                  analysis && (

                  <>


                    {/* SUMMARY */}

                    <div className="summary-banner">

                      <div className="summary-indicator">
                        ✓
                      </div>

                      <div>

                        <span>
                          ANALYSIS COMPLETE
                        </span>

                        <strong>

                          {analysis.image?.width}
                          {" × "}
                          {analysis.image?.height}px

                          {" · "}

                          {analysis.image?.format}

                          {" · "}

                          {blurAnalysis.status ||
                            "analyzed"}

                        </strong>

                      </div>

                    </div>


                    {/* CHECK GRID */}

                    <div className="check-grid">


                      {/* BLUR */}

                      <div className="check-card">

                        <span className="check-label">
                          BLUR
                        </span>

                        <strong>

                          {blurAnalysis.score ??
                            "N/A"}

                        </strong>

                        <div className="check-bottom">

                          <span
                            className={`check-status ${getStatusClass(
                              blurAnalysis.status
                            )}`}
                          >

                            {blurAnalysis.status ||
                              "Unknown"}

                          </span>

                          <span className="check-description">
                            Laplacian variance
                          </span>

                        </div>

                      </div>


                      {/* BRIGHTNESS */}

                      <div className="check-card">

                        <span className="check-label">
                          BRIGHTNESS
                        </span>

                        <strong>

                          {brightnessAnalysis.score ??
                            "N/A"}

                        </strong>

                        <div className="check-bottom">

                          <span
                            className={`check-status ${getStatusClass(
                              brightnessAnalysis.status
                            )}`}
                          >

                            {brightnessAnalysis.status ||
                              "Unknown"}

                          </span>

                          <span className="check-description">
                            Mean intensity
                          </span>

                        </div>

                      </div>


                      {/* DIMENSIONS */}

                      <div className="check-card">

                        <span className="check-label">
                          DIMENSIONS
                        </span>

                        <strong>

                          {analysis.image?.width}
                          {" × "}
                          {analysis.image?.height}

                        </strong>

                        <div className="check-bottom">

                          <span
                            className={`check-status ${getStatusClass(
                              dimensionValidation.status
                            )}`}
                          >

                            {dimensionValidation.status ||
                              "Valid"}

                          </span>

                          <span className="check-description">
                            Image size
                          </span>

                        </div>

                      </div>


                      {/* DUPLICATE */}

                      <div className="check-card">

                        <span className="check-label">
                          DUPLICATE CHECK
                        </span>

                        <strong>

                          {duplicateStatus.label}

                        </strong>

                        <div className="check-bottom">

                          <span
                            className={`check-status ${duplicateStatus.className}`}
                          >

                            {duplicateStatus.label}

                          </span>

                          <span className="check-description">
                            File comparison
                          </span>

                        </div>


                        {duplicateDetection.is_duplicate &&
                          duplicateDetection.duplicate_file && (

                          <div className="duplicate-file">

                            {duplicateDetection.duplicate_file}

                          </div>

                        )}

                      </div>


                      {/* OCR */}

                      <div className="check-card">

                        <span className="check-label">
                          OCR EXTRACT
                        </span>

                        <strong>

                          {ocrAnalysis.detected
                            ? "Detected"
                            : "No text"}

                        </strong>

                        <div className="check-bottom">

                          <span
                            className={`check-status ${
                              ocrAnalysis.detected
                                ? "success"
                                : "warning"
                            }`}
                          >

                            {ocrAnalysis.character_count ??
                              0} chars

                          </span>

                          <span className="check-description">
                            Text recognition
                          </span>

                        </div>

                      </div>


                      {/* PHOTO CHECK */}

                      <div className="check-card">

                        <span className="check-label">
                          PHOTO CHECK
                        </span>

                        <strong>

                          {photoAnalysis.status ||
                            "Unknown"}

                        </strong>

                        <div className="check-bottom">

                          <span
                            className={`check-status ${getStatusClass(
                              photoAnalysis.status
                            )}`}
                          >
                            Heuristic
                          </span>

                          <span className="check-description">
                            Authenticity signal
                          </span>

                        </div>

                      </div>

                    </div>


                    {/* OCR EXTRACTION */}

                    <section className="ocr-section">

                      <div className="section-title">

                        <div>

                          <span className="eyebrow">
                            TEXT RECOGNITION
                          </span>

                          <h3>
                            OCR Extraction
                          </h3>

                        </div>

                        <span className="ocr-count">

                          {ocrAnalysis.character_count ??
                            0} characters

                        </span>

                      </div>


                      <div className="ocr-box">

                        {getOCRText()}

                      </div>

                    </section>


                    {/* IMAGE DETAILS */}

                    <section className="details-section">

                      <div className="section-title">

                        <div>

                          <span className="eyebrow">
                            IMAGE DETAILS
                          </span>

                          <h3>
                            Processing Information
                          </h3>

                        </div>

                      </div>


                      <div className="details-grid">


                        <div>

                          <span>
                            FILE FORMAT
                          </span>

                          <strong>

                            {analysis.image?.format ||
                              "N/A"}

                          </strong>

                        </div>


                        <div>

                          <span>
                            ASPECT RATIO
                          </span>

                          <strong>

                            {analysis.image?.aspect_ratio ??
                              "N/A"}

                          </strong>

                        </div>


                        <div>

                          <span>
                            PROCESSING ID
                          </span>

                          <strong>

                            {result.processing_id ||
                              "N/A"}

                          </strong>

                        </div>


                        <div>

                          <span>
                            PROCESSED AT
                          </span>

                          <strong>

                            {analysis.processed_at
                              ? new Date(
                                  analysis.processed_at
                                ).toLocaleString()
                              : "N/A"}

                          </strong>

                        </div>

                      </div>

                    </section>

                  </>

                )}

              </div>

            )}

          </div>

        </section>


        {/* ===================================================
            FEATURE STRIP
        =================================================== */}

        <section className="feature-strip">


          <div className="feature-item">

            <span>
              01
            </span>

            <div>

              <h3>
                Image Quality
              </h3>

              <p>
                Sharpness and brightness evaluation
              </p>

            </div>

          </div>


          <div className="feature-item">

            <span>
              02
            </span>

            <div>

              <h3>
                Intelligent OCR
              </h3>

              <p>
                Automatically extracts visible text
              </p>

            </div>

          </div>


          <div className="feature-item">

            <span>
              03
            </span>

            <div>

              <h3>
                Duplicate Detection
              </h3>

              <p>
                Identifies previously processed images
              </p>

            </div>

          </div>


          <div className="feature-item">

            <span>
              04
            </span>

            <div>

              <h3>
                Async Processing
              </h3>

              <p>
                Background analysis through FastAPI
              </p>

            </div>

          </div>


        </section>

      </main>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer>

        <span>
          gOGig · Intelligent Media Processing
        </span>

        <span>
          React · FastAPI · MongoDB
        </span>

      </footer>

    </div>
  );
}

export default App;