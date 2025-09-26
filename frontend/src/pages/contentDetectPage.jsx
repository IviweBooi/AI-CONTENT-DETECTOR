import { useState, useRef, useEffect } from 'react'
import detectIcon from '../assets/icons/detect.svg'
import { analyzeText, analyzeFile, submitFeedback, trackScan, exportReport, getAvailableExportFormats, downloadBlob, getUserScans } from '../services/api'
import { useAuth } from '../contexts/AuthContext'


export default function ContentDetectPage() {
  // Firebase hooks
  const { user, isAuthenticated } = useAuth()

  // UI state
  const [activeTab, setActiveTab] = useState('text') // which tab is active: 'text' | 'file'
  const [text, setText] = useState('') // user input text
  const MIN_CHARS = 150 // minimum characters for better analysis accuracy
  const MAX_CHARS = 2000 // max characters allowed (optimized for RoBERTa's 512 token limit)
  const [limitNotice, setLimitNotice] = useState('') // warning/notice when approaching/reaching limit
  const [isAnalyzing, setIsAnalyzing] = useState(false) // loading state during analysis
  const [isLoadingFile, setIsLoadingFile] = useState(false) // loading state during file upload/processing
  const [result, setResult] = useState(null) // analysis result object or null
  const [analysisTime, setAnalysisTime] = useState(null) // elapsed analysis time string, e.g. "1.2s"
  const [isDragging, setIsDragging] = useState(false) // drag-over visual state for file drop
  const [fileName, setFileName] = useState('') // selected file name (for preview)
  const [fileError, setFileError] = useState('') // instant feedback for unsupported files
  const [uploadProgress, setUploadProgress] = useState(0) // file upload progress
  const fileInputRef = useRef(null) // hidden file input ref

  // Daily submission limit (client-side demo)
  const DAILY_LIMIT = 100
  const STORAGE_KEY = 'aicd_daily_counter'
  const [submissionsUsed, setSubmissionsUsed] = useState(0)

  // Scan history state
  const [scanHistory, setScanHistory] = useState([])
  const [expandedHistoryItems, setExpandedHistoryItems] = useState(new Set())
  const [isLoadingHistory, setIsLoadingHistory] = useState(false)
  const [submissionMsg, setSubmissionMsg] = useState('')

  // Feedback modal state
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackType, setFeedbackType] = useState('');
  const [feedbackComment, setFeedbackComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  // Export dialog state
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [availableFormats, setAvailableFormats] = useState(['pdf', 'json', 'csv']);
  const [selectedFormat, setSelectedFormat] = useState('pdf');
  const [reportTitle, setReportTitle] = useState('AI Content Detection Report');
  const [isExporting, setIsExporting] = useState(false);

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!feedbackType || isSubmitting) return;
    
    setIsSubmitting(true);
    
    try {
      // Add a minimum delay to show the submitting state
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Call the API service to submit feedback
      const response = await submitFeedback({
        type: feedbackType,
        comment: feedbackComment,
        resultId: result ? 'result-' + Date.now() : undefined // In a real app, each result would have a unique ID
      });
      
      if (!response.success) {
        console.error('Failed to submit feedback:', response.error);
      }
      
      setFeedbackType('');
      setFeedbackComment('');
      setShowFeedbackModal(false);
      setSuccessMessage('Thank you for your feedback! We appreciate your input.');
      setShowSuccessMessage(true);
      
      // Hide success message after 5 seconds
      setTimeout(() => {
        setShowSuccessMessage(false);
      }, 5000);
    } catch (error) {
      console.error('Error submitting feedback:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Set up a light intersection observer for small reveal animations.
  useEffect(() => {
    const els = document.querySelectorAll('[data-reveal]')
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('in') })
    }, { threshold: 0.12 })
    els.forEach((el) => io.observe(el))
    return () => io.disconnect()
  }, [])

  // Initialize/reset daily counter at midnight UTC
  useEffect(() => {
    function getUtcDateKey() { return new Date().toISOString().slice(0, 10) }
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      const today = getUtcDateKey()
      if (raw) {
        const data = JSON.parse(raw)
        if (data && data.date === today && Number.isFinite(data.used)) {
          setSubmissionsUsed(Math.max(0, Math.min(DAILY_LIMIT, Number(data.used))))
        } else {
          localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, used: 0 }))
          setSubmissionsUsed(0)
        }
      } else {
        localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, used: 0 }))
        setSubmissionsUsed(0)
      }
    } catch {
      // Fail silently in demo
      setSubmissionsUsed(0)
    }
  }, [])

  // Load available export formats on component mount
  useEffect(() => {
    const loadExportFormats = async () => {
      try {
        const response = await getAvailableExportFormats();
        if (response.success && response.data.formats) {
          setAvailableFormats(response.data.formats);
          setSelectedFormat(response.data.default || response.data.formats[0] || 'pdf');
        }
      } catch (error) {
        console.error('Failed to load export formats:', error);
        // Keep default formats as fallback
      }
    };
    loadExportFormats();
  }, []);

  // Load scan history for authenticated users only
  useEffect(() => {
    const loadScanHistory = async () => {
      if (!user?.uid) {
        setScanHistory([]);
        return;
      }

      setIsLoadingHistory(true);
      try {
        const response = await getUserScans(user.uid);
        
        if (response.success && response.data?.scans) {
          setScanHistory(response.data.scans);
        } else {
          setScanHistory([]);
        }
      } catch (error) {
        console.error('Failed to load scan history:', error);
        setScanHistory([]);
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadScanHistory();
  }, [user?.uid, isAuthenticated]);

  // Toggle expansion of history items
  const toggleHistoryItemExpansion = (index) => {
    const newExpanded = new Set(expandedHistoryItems)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedHistoryItems(newExpanded)
  }

  // Derived UI values
  const uiCharCount = text.length
  const uiCanAnalyze = text.trim().length >= MIN_CHARS && 
    (activeTab === 'text' || (activeTab === 'file' && fileName && !fileError))
  const remainingSubmissions = Math.max(0, DAILY_LIMIT - submissionsUsed)

  // Trigger hidden file picker programmatically
  function onPickFile() { fileInputRef.current?.click() }

  // Handle incoming file (from drop or picker) with quick extension validation.
  // Use the API service for file analysis instead of local extraction
  async function analyzeUploadedFile(file) {
    if (!file) return null;
    
    setIsAnalyzing(true);
    setResult(null);
    const startTime = performance.now();
    
    try {
      // Call the API service to analyze the file
      const response = await analyzeFile(file);
      
      if (!response.success) {
        throw new Error(response.error || 'File analysis failed');
      }
      
      const elapsed = ((performance.now() - startTime) / 1000).toFixed(1);
      setAnalysisTime(elapsed + 's');
      
      // Track file scan with metadata
      trackScan({
        contentType: 'file',
        contentLength: file.size,
        fileName: file.name,
        userId: user?.uid || null
      });
      
      return response.data;
    } catch (error) {
      console.error('File analysis error:', error);
      setSubmissionMsg('An error occurred analyzing the file. Please try again.');
      return null;
    } finally {
      setIsLoadingFile(false);
    }
  }

  async function handleFile(file) {
    if (!file) return
    
    const name = file.name || ''
    const lower = name.toLowerCase()
    
    // Size limit: 10MB
    if (file.size > 10 * 1024 * 1024) {
      setFileName('')
      setText('')
      setFileError('File too large. Maximum size is 10MB.')
      return
    }
    
    // Supported extensions for quick validation
    const isTxt = lower.endsWith('.txt')
    const isDocx = lower.endsWith('.docx')
    const isPdf = lower.endsWith('.pdf')

    // Reject unsupported types immediately
    if (!(isTxt || isDocx || isPdf)) {
      setFileName('')
      setText('')
      setFileError('Unsupported file format. Supported: TXT, DOCX, PDF.')
      return
    }

    setFileName(name)
    setFileError('')
    
    // Daily limit check
    if (remainingSubmissions <= 0) {
      setSubmissionMsg('Daily limit exceeded. Try again tomorrow.')
      return
    }
    
    setIsLoadingFile(true)
    setUploadProgress(0)
    const startTime = performance.now()
    
    try {
      // Direct backend upload (Firebase Storage disabled)
      setUploadProgress(50) // Show progress for direct upload
      
      // Upload file to backend and get extracted content
      const response = await analyzeFile(file, null) // No fileUrl needed
      
      if (!response.success) {
        throw new Error(response.error || 'File upload failed')
      }
      
      const elapsed = ((performance.now() - startTime) / 1000).toFixed(1)
      setAnalysisTime(elapsed + 's')
      
      // Extract text content from backend response
      if (response.data && response.data.text && typeof response.data.text === 'string' && response.data.text.trim()) {
        const fileContent = response.data.text
        
        if (fileContent.length > MAX_CHARS) {
          setLimitNotice(`Input truncated to ${MAX_CHARS.toLocaleString()} characters.`)
          setText(fileContent.slice(0, MAX_CHARS))
        } else if (fileContent.length > Math.floor(MAX_CHARS * 0.9)) {
          setLimitNotice(`Approaching limit: ${fileContent.length.toLocaleString()}/${MAX_CHARS.toLocaleString()}`)
          setText(fileContent)
        } else {
          setLimitNotice('')
          setText(fileContent)
        }
        
        // Clear any previous analysis results
        setResult(null)
        
        // Switch to text tab to show extracted content
        setActiveTab('text')
      } else {
        const debugInfo = response.data ? 
          `Response data: ${JSON.stringify(response.data)}` : 
          'No response data received';
        throw new Error(`No text content extracted from file. ${debugInfo}`);
      }
      
      // Track scan with file metadata
      trackScan({
        contentType: 'file',
        contentLength: file.size,
        fileName: file.name,
        userId: user?.uid || null
      })
      
      // Increment submission counter
      setSubmissionsUsed((prev) => {
        const next = Math.min(DAILY_LIMIT, prev + 1)
        try {
          const today = new Date().toISOString().slice(0, 10)
          localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, used: next }))
        } catch (error) {
          console.warn('Failed to update local storage:', error);
        }
        const rem = Math.max(0, DAILY_LIMIT - next)
        setSubmissionMsg(`${rem}/${DAILY_LIMIT} daily submissions remaining.`)
        return next
      })
    } catch (error) {
      console.error('Error processing file:', error)
      
      // Provide more informative error messages based on error type
      let errorMessage = 'Error processing file. Please try another file.'
      
      if (error.message.includes('No text content extracted') || error.message.includes('No readable text found')) {
        errorMessage = 'Unable to extract text from this file. The file may be too complex, corrupted, or contain mostly images/graphics. Please try a simpler text-based file (TXT, simple DOCX, or text-heavy PDF).'
      } else if (error.message.includes('PDF parsing error')) {
        errorMessage = 'PDF file is too complex or corrupted to process. Please try a simpler PDF with more text content, or convert it to a plain text file (.txt).'
      } else if (error.message.includes('DOCX parsing error')) {
        errorMessage = 'Word document is too complex or corrupted to process. Please try a simpler DOCX file with plain text, or save it as a text file (.txt).'
      } else if (error.message.includes('TXT parsing error')) {
        errorMessage = 'Text file has encoding issues or is corrupted. Please try saving the file with UTF-8 encoding or use a different text file.'
      } else if (error.message.includes('File upload failed') || error.message.includes('failed')) {
        errorMessage = 'File upload failed. The file may be too complex to process or contain unsupported formatting. Please try a simpler file with plain text content.'
      } else if (error.message.includes('timeout') || error.message.includes('Timeout')) {
        errorMessage = 'File processing timed out. The file may be too large or complex. Please try a smaller, simpler file.'
      } else if (error.message.includes('format') || error.message.includes('Format') || error.message.includes('Unsupported')) {
        errorMessage = 'Unsupported file format or complex formatting detected. Please try a plain text file (.txt) or a simple document without complex layouts.'
      }
      
      setFileError(errorMessage)
      setFileName('')
      setText('')
    } finally {
      setIsLoadingFile(false)
    }
  }

  function onFileChosen(e) { handleFile(e.target.files?.[0]) }

  // Drag & Drop handlers
  function onDrop(e) {
    e.preventDefault(); e.stopPropagation(); setIsDragging(false)
    const file = e.dataTransfer?.files?.[0]
    handleFile(file)
  }
  function onDragOver(e) { e.preventDefault(); e.stopPropagation(); setIsDragging(true) }
  function onDragLeave(e) { e.preventDefault(); e.stopPropagation(); setIsDragging(false) }

  // Perform analysis using the API service
  async function analyze() {
    if (!text.trim()) return
    // Daily limit check (client-side demo)
    if (remainingSubmissions <= 0) {
      setSubmissionMsg('Daily limit exceeded. Try again tomorrow.')
      return
    }
    // Inform current remaining before processing
    setSubmissionMsg(`You have ${remainingSubmissions}/${DAILY_LIMIT} submissions remaining today.`)
    setIsAnalyzing(true)
    const startTime = performance.now()
    
    try {
      // Call the API service to analyze the text
      const response = await analyzeText(text)
      
      if (!response.success) {
        throw new Error(response.error || 'Analysis failed')
      }
      
      setResult(response.data)
      const elapsed = ((performance.now() - startTime) / 1000).toFixed(1)
      setAnalysisTime(elapsed + 's')
      
      // Track scan with content metadata and results
      trackScan({
        content_type: 'text',
        content_length: text.length,
        userId: user?.uid || null,
        prediction: response.data?.prediction || 0,
        confidence: response.data?.confidence || 0,
        timestamp: new Date().toISOString(),
        analysis_time: elapsed
      })
      
      // On successful submission, increment and persist counters
      setSubmissionsUsed((prev) => {
        const next = Math.min(DAILY_LIMIT, prev + 1)
        try {
          const today = new Date().toISOString().slice(0, 10)
          localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, used: next }))
        } catch (error) {
          console.warn('Failed to update local storage:', error);
        }
        const rem = Math.max(0, DAILY_LIMIT - next)
        setSubmissionMsg(`${rem}/${DAILY_LIMIT} daily submissions remaining.`)
        return next
      })
    } catch (error) {
      console.error('Analysis error:', error)
      setSubmissionMsg('An error occurred during analysis. Please try again.')
    } finally {
      setIsAnalyzing(false)
    }
  }

  // This function is now handled by the API service in generateFlaggedSections


  // UI handlers
  function showExportOptions() {
    if (!result) {
      alert('No results to export.');
      return;
    }
    setShowExportDialog(true);
  }

  function closeExportDialog() {
    setShowExportDialog(false);
    setReportTitle('AI Content Detection Report');
  }



  async function handleExportConfirm() {
    if (!result || !text) {
      alert('No results to export.');
      return;
    }
    
    setIsExporting(true);
    
    try {
      // Use the API service to export results
      const response = await exportReport(result, text, selectedFormat, reportTitle);
      
      if (!response.success) {
        throw new Error(response.error || 'Export failed');
      }
      
      // Download the file
      downloadBlob(response.blob, response.filename);
      
      // Close dialog and show success
      setShowExportDialog(false);
      setSuccessMessage('Report exported successfully!');
      setShowSuccessMessage(true);
      
      // Hide success message after 3 seconds
      setTimeout(() => {
        setShowSuccessMessage(false);
      }, 3000);
    } catch (error) {
      console.error('Error exporting report:', error);
      alert('Failed to export report. Please try again.');
    } finally {
      setIsExporting(false);
    }
  }
  const provideFeedback = () => setShowFeedbackModal(true);
  
  // Increment scan counter for analytics
  function incrementScan() {
    // This function now uses the API service
    trackScan({
      contentType: 'unknown',
      userId: user?.uid || null
    })
    // Keeping for backward compatibility
  }

  return (
    <section id="detector" className="detector-section" data-reveal>
      <div className="container">
        <div className="section-header">
          <h2>AI Content Detector</h2>
          <p>Paste your text or upload a file to analyze content authenticity</p>
        </div>

        <div className="detector-container">
          {/* Input Panel */}
          <div className="input-panel glass-card">
            <div className="input-tabs">
              <button className={`tab-btn ${activeTab === 'text' ? 'active' : ''}`} onClick={() => setActiveTab('text')}>
                <i className="fa-solid fa-keyboard" aria-hidden="true"></i>
                <span>Text Input</span>
              </button>
              <button className={`tab-btn ${activeTab === 'file' ? 'active' : ''}`} onClick={() => setActiveTab('file')}>
                <i className="fa-solid fa-upload" aria-hidden="true"></i>
                <span>File Upload</span>
              </button>
            </div>

            {/* Text Input Tab */}
            <div className={`tab-content ${activeTab === 'text' ? 'active' : ''}`} id="text-tab">
              <div className="text-input-container">
                {text && (
                  <button 
                    type="button" 
                    className="clear-text-btn"
                    onClick={() => {
                      setText('');
                      setLimitNotice('');
                    }}
                    aria-label="Clear text"
                    title="Clear text"
                  >
                    <i className="fa-solid fa-trash" aria-hidden="true"></i>
                  </button>
                )}
                <textarea
                  id="content-input"
                  className="text-input"
                  placeholder="Paste or type your content here for AI detection analysis..."
                  rows={12}
                  value={text}
                  onChange={(e) => {
                    let v = e.target.value
                    if (v.length > MAX_CHARS) {
                      v = v.slice(0, MAX_CHARS)
                      setLimitNotice(`Character limit reached (${MAX_CHARS.toLocaleString()}).`)
                    } else if (v.length > Math.floor(MAX_CHARS * 0.9)) {
                      setLimitNotice(`Approaching limit: ${v.length.toLocaleString()}/${MAX_CHARS.toLocaleString()}`)
                    } else {
                      setLimitNotice('')
                    }
                    // set text to the truncated value
                    setText(v)
                  }}
                />
              </div>
              <div className="input-info">
                <span id="char-count" className={text.length >= MIN_CHARS ? 'char-ok' : ''}>
                  {text.length.toLocaleString()} / {MAX_CHARS.toLocaleString()} characters
                </span>
                <span className={`min-chars ${text.length >= MIN_CHARS ? 'ok' : ''}`}>
                  Minimum {MIN_CHARS} characters required for accurate analysis
                </span>
                {limitNotice && <span className="char-warning">{limitNotice}</span>}
              </div>
            </div>

            {/* File Upload Tab */}
            <div className={`tab-content ${activeTab === 'file' ? 'active' : ''}`} id="file-tab">
              <div className="file-upload-container">
                <div
                  className={`upload-area ${isDragging ? 'drag' : ''}`}
                  onDrop={onDrop}
                  onDragOver={onDragOver}
                  onDragLeave={onDragLeave}
                  onClick={onPickFile}
                >
                  <div className="upload-icon" aria-hidden>
                    <i className="fa-solid fa-cloud-arrow-up"></i>
                  </div>
                  <h3>Drop your file here</h3>
                  <p>or <span className="upload-link">browse files</span></p>
                  <input ref={fileInputRef} type="file" id="file-input" accept=".txt,.docx,.pdf" hidden onChange={onFileChosen} />
                  <div className="supported-formats">Supported: TXT, DOCX, PDF (max 10MB)</div>
                  {fileError && (
                    <div className="file-error" role="alert" aria-live="polite">{fileError}</div>
                  )}
                </div>

              </div>
              {fileName && (
                <div className="uploaded-file">
                  <div className="file-info">
                    <i className="fa-solid fa-file-lines" aria-hidden="true"></i>
                    <span className="file-name">{fileName}</span>
                    <button 
                      className="clear-file-btn"
                      onClick={() => { setFileName(''); setText(''); setFileError('') }}
                      aria-label="Remove file"
                      title="Remove file"
                    >
                      <i className="fa-solid fa-times" aria-hidden="true"></i>
                    </button>
                  </div>
                </div>
              )}
            </div>

            <button 
              className="btn btn-primary analyze-button" 
              onClick={analyze} 
              disabled={text.length < MIN_CHARS || isAnalyzing || isLoadingFile || remainingSubmissions === 0}
            >
              <img src={detectIcon} alt="detect" height="20" />
              <span>
                {isLoadingFile ? 'Loading File…' : isAnalyzing ? 'Analyzing…' : 'Analyze'}
              </span>
              {(isAnalyzing || isLoadingFile) && <span className="loading-spinner" />}
            </button>
            {submissionMsg && (
              <div className={`${remainingSubmissions === 0 ? 'limit-error' : 'limit-info'}`} role="status" aria-live="polite">{submissionMsg}</div>
            )}
          </div>

          {/* Results Panel (always rendered) */}
          <div className="results-panel glass-card" id="results-panel">
            {!result ? (
              <div className="results-empty">
                <div>
                  <i className="fa-solid fa-chart-line" aria-hidden="true" style={{ fontSize: '28px' }}></i>
                  <div className="hint">Results will appear here after you analyze.</div>
                </div>
              </div>
            ) : (
              <>
                <div className="results-header">
                  <h3>Detection Results</h3>
                  <div className="analysis-time">Analyzed in <span id="analysis-time">{analysisTime}</span></div>
                </div>

                <div className="confidence-score">
                  <div className="score-circle" style={{ '--p': `${Math.round((result.ai_probability || 0) * 100)}%` }}>
                    <div className="score-content">
                      <div className="score-values">
                        <div className="ai-percentage">{Math.round((result.ai_probability || 0) * 100)}% AI</div>
                        <div className="human-percentage">{Math.round((1 - (result.ai_probability || 0)) * 100)}% Human</div>
                      </div>
                      <div className="score-label">Content Detection</div>
                    </div>
                  </div>
                  <div className="score-interpretation" id="score-interpretation">
                    <div className="interpretation-text">{result.classification || ((result.ai_probability || 0) >= 0.51 ? 'Likely AI‑generated' : 'Likely human‑written')}</div>
                    <div className="interpretation-desc">Risk Level: {result.risk_level || 'Unknown'}</div>
                    <div className="confidence-info">Model Confidence: {Math.round((result.confidence || result.analysis?.model_confidence || 0) * 100)}%</div>
                  </div>
                </div>



                {/* Enhanced Feedback Messages */}
                {result.feedback_messages && result.feedback_messages.length > 0 && (
                  <div className="feedback-section">
                    <h4>Analysis Feedback</h4>
                    <div className="feedback-messages">
                      {result.feedback_messages.map((message, index) => (
                        <div key={index} className="feedback-message">
                          <span dangerouslySetInnerHTML={{ __html: message }} />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Recommendations */}
                {result.recommendations && result.recommendations.length > 0 && (
                  <div className="recommendations-section">
                    <h4>Recommendations</h4>
                    <div className="recommendations-list">
                      {result.recommendations.map((recommendation, index) => (
                        <div key={index} className="recommendation-item">
                          <span dangerouslySetInnerHTML={{ __html: recommendation }} />
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="content-highlights" id="content-highlights">
                  <h4>Flagged Sections</h4>
                  <div className="highlighted-content">
                    {result.flagged_sections && result.flagged_sections.length > 0 ? (
                      result.flagged_sections.map((section, index) => (
                        <div key={index} className="flagged-section">
                          <span className="flagged-text">{section.text}</span>
                          {section.reasons && (
                            <div className="flag-reasons">
                              <small>Reasons: {section.reasons.join(', ')}</small>
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <p className="no-flags">No specific sections flagged for review.</p>
                    )}
                  </div>
                </div>

                <div className="results-actions">
                  <button className="btn btn-ghost" onClick={showExportOptions}>
                    <i className="fa-solid fa-download" aria-hidden="true"></i>
                    <span>Export Report</span>
                  </button>
                  <button className="btn btn-ghost" onClick={provideFeedback}>
                    <i className="fa-solid fa-comment-dots" aria-hidden="true"></i>
                    <span>Provide Feedback</span>
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Success Message */}
      {showSuccessMessage && (
        <div className="success-message">
          <div className="success-message-content">
            <i className="fa-solid fa-check-circle"></i>
            <span>{successMessage}</span>
          </div>
        </div>
      )}

      {/* Feedback Modal */}
      {showFeedbackModal && (
        <div className="feedback-modal">
          <div className="feedback-modal-content">
            <div className="feedback-modal-header">
              <h3>Provide Feedback</h3>
              <button 
                type="button" 
                onClick={() => setShowFeedbackModal(false)}
                className="feedback-close-btn"
                aria-label="Close feedback modal"
              >
                &times;
              </button>
            </div>
            
            <form onSubmit={handleFeedbackSubmit} className="feedback-modal-body">
              <div className="feedback-options">
                <p className="text-gray-700 mb-3">How accurate was the content detection?</p>
                {['Accurate', 'Partially Accurate', 'Inaccurate'].map((option) => (
                  <label key={option} className="feedback-option">
                    <input
                      type="radio"
                      name="feedbackType"
                      value={option}
                      checked={feedbackType === option}
                      onChange={() => setFeedbackType(option)}
                    />
                    <span>{option}</span>
                  </label>
                ))}
              </div>

              <div>
                <label htmlFor="feedbackComment" className="block text-gray-700 mb-2">
                  Additional comments (optional)
                </label>
                <textarea
                  id="feedbackComment"
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                  className="feedback-comments"
                  rows="4"
                  placeholder="Please provide more details about your feedback..."
                />
              </div>

              <div className="feedback-modal-actions">
                <button
                  type="button"
                  onClick={() => setShowFeedbackModal(false)}
                  className="feedback-cancel-btn"
                  disabled={isSubmitting}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="feedback-submit-btn"
                  disabled={!feedbackType || isSubmitting}
                >
                  {!isSubmitting && (
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M2 21L23 12L2 3V10L17 12L2 14V21Z" fill="currentColor"/>
                    </svg>
                  )}
                  {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Export Dialog Modal */}
      {showExportDialog && (
        <div className="feedback-modal">
          <div className="feedback-modal-content export-dialog">
            <div className="feedback-modal-header">
              <h3>Export Report</h3>
              <button 
                type="button" 
                onClick={closeExportDialog}
                className="feedback-close-btn"
                aria-label="Close export dialog"
              >
                &times;
              </button>
            </div>
            
            <div className="feedback-modal-body">
              <div className="export-form-group">
                <label htmlFor="reportTitle">
                  Report Title
                </label>
                <input
                  id="reportTitle"
                  type="text"
                  value={reportTitle}
                  onChange={(e) => setReportTitle(e.target.value)}
                  placeholder="Enter report title"
                />
              </div>

              <div className="export-form-group">
                <label htmlFor="exportFormat">
                  Export Format
                </label>
                <select
                  id="exportFormat"
                  value={selectedFormat}
                  onChange={(e) => setSelectedFormat(e.target.value)}
                >
                  {availableFormats.map(format => (
                    <option key={format} value={format}>
                      {format.toUpperCase()} - {format === 'pdf' ? 'Professional Report' : format === 'json' ? 'Structured Data' : 'Spreadsheet Data'}
                    </option>
                  ))}
                </select>
              </div>

              <div className="export-format-info">
                <p>
                  {selectedFormat === 'pdf' && '📄 Professional PDF report with charts and detailed analysis'}
                  {selectedFormat === 'json' && '📊 Structured JSON data for programmatic use'}
                  {selectedFormat === 'csv' && '📈 CSV format for spreadsheet analysis'}
                </p>
              </div>

              <div className="feedback-modal-actions">
                <button
                  type="button"
                  onClick={closeExportDialog}
                  className="feedback-cancel-btn"
                  disabled={isExporting}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleExportConfirm}
                  className="feedback-submit-btn"
                  disabled={isExporting || !reportTitle.trim()}
                >
                  {!isExporting && (
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M12 16L7 11L8.4 9.6L11 12.2V4H13V12.2L15.6 9.6L17 11L12 16Z" fill="currentColor"/>
                      <path d="M5 20V18H19V20H5Z" fill="currentColor"/>
                    </svg>
                  )}
                  {isExporting ? 'Exporting...' : `Export as ${selectedFormat.toUpperCase()}`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Scan History Section - Only for authenticated users */}
      {isAuthenticated && user && (
        <div className="scan-history-section" style={{ marginTop: '3rem', padding: '2rem', backgroundColor: '#f8f9fa', borderRadius: '12px', border: '1px solid #e9ecef' }}>
          <h3 style={{ marginBottom: '1.5rem', color: '#2c3e50', fontSize: '1.5rem', fontWeight: '600' }}>
            Recent Scan History
          </h3>

          
          {isLoadingHistory ? (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <div style={{ display: 'inline-block', width: '20px', height: '20px', border: '2px solid #e9ecef', borderTop: '2px solid #007bff', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
              <p style={{ marginTop: '1rem', color: '#6c757d' }}>Loading your scan history...</p>
            </div>
          ) : scanHistory.length > 0 ? (
            <div className="scan-history-list">
              {scanHistory.map((scan, index) => {
                const isExpanded = expandedHistoryItems.has(index)
                return (
                  <div 
                    key={index} 
                    style={{ 
                      backgroundColor: 'white', 
                      padding: '1rem', 
                      marginBottom: '0.75rem', 
                      borderRadius: '8px', 
                      border: isExpanded ? '2px solid #007bff' : '1px solid #dee2e6',
                      cursor: 'pointer !important',
                      transition: 'all 0.2s ease',
                      boxShadow: isExpanded ? '0 4px 12px rgba(0,0,0,0.1)' : '0 1px 3px rgba(0,0,0,0.05)',
                      userSelect: 'none',
                      position: 'relative',
                      zIndex: 10,
                      pointerEvents: 'auto'
                    }}
                    onClick={() => toggleHistoryItemExpansion(index)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.transform = 'translateY(-1px)'
                      e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.transform = 'translateY(0)'
                      e.currentTarget.style.boxShadow = isExpanded ? '0 4px 12px rgba(0,0,0,0.1)' : '0 1px 3px rgba(0,0,0,0.05)'
                    }}
                  >
                    <div style={{ 
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ 
                          fontWeight: '500', 
                          color: '#2c3e50', 
                          marginBottom: '0.25rem',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}>
                          {scan.content_type === 'text' ? '📝 Text Analysis' : 
                           scan.content_type === 'file' ? '📄 File Analysis' : 
                           scan.file_name ? `📄 ${scan.file_name}` : '🔍 Content Analysis'}
                          <span style={{ 
                            fontSize: '0.75rem', 
                            color: '#6c757d',
                            fontWeight: 'normal'
                          }}>
                            {isExpanded ? '▼ Click to collapse' : '▶ Click to expand'}
                          </span>
                        </div>
                        <div style={{ fontSize: '0.875rem', color: '#6c757d' }}>
                          {scan.content_length && `${scan.content_length} characters • `}
                          {scan.prediction && `${(scan.prediction * 100).toFixed(1)}% AI, ${((1 - scan.prediction) * 100).toFixed(1)}% Human • `}
                          {new Date(scan.timestamp).toLocaleDateString()} at {new Date(scan.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                      <div style={{ 
                        padding: '0.25rem 0.75rem', 
                        borderRadius: '20px', 
                        fontSize: '0.75rem', 
                        fontWeight: '500',
                        backgroundColor: scan.prediction > 0.5 ? '#fff3cd' : '#d1ecf1',
                        color: scan.prediction > 0.5 ? '#856404' : '#0c5460',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        gap: '2px',
                        minWidth: '80px'
                      }}>
                        {scan.prediction ? (
                          <>
                            <div>{(scan.prediction * 100).toFixed(1)}% AI</div>
                            <div>{((1 - scan.prediction) * 100).toFixed(1)}% Human</div>
                          </>
                        ) : 'Analyzed'}
                      </div>
                    </div>
                    
                    {/* Expanded Content */}
                    {isExpanded && (
                      <div style={{ 
                        marginTop: '1rem', 
                        paddingTop: '1rem', 
                        borderTop: '1px solid #e9ecef',
                        opacity: 1,
                        transition: 'opacity 0.3s ease'
                      }}>
                        {/* Text Content Preview */}
                        {scan.text_content && (
                          <div style={{ marginBottom: '1rem' }}>
                            <h5 style={{ 
                              fontSize: '0.875rem', 
                              fontWeight: '600', 
                              color: '#495057', 
                              marginBottom: '0.5rem' 
                            }}>
                              📄 Content Preview:
                            </h5>
                            <div style={{ 
                              backgroundColor: '#f8f9fa', 
                              padding: '0.75rem', 
                              borderRadius: '6px', 
                              border: '1px solid #e9ecef',
                              fontSize: '0.875rem',
                              color: '#495057',
                              maxHeight: '120px',
                              overflow: 'auto',
                              lineHeight: '1.4',
                              whiteSpace: 'pre-wrap'
                            }}>
                              {scan.text_content}
                            </div>
                          </div>
                        )}
                        
                        {/* Detailed Analysis Results */}
                        {scan.analysis_result && (
                          <div style={{ marginBottom: '1rem' }}>
                            <h5 style={{ 
                              fontSize: '0.875rem', 
                              fontWeight: '600', 
                              color: '#495057', 
                              marginBottom: '0.5rem' 
                            }}>
                              🔍 Detailed Analysis:
                            </h5>
                            <div style={{ 
                              display: 'grid', 
                              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
                              gap: '1rem' 
                            }}>
                              {/* AI Detection Results */}
                              <div style={{ 
                                backgroundColor: '#f8f9fa', 
                                padding: '0.75rem', 
                                borderRadius: '6px', 
                                border: '1px solid #e9ecef' 
                              }}>
                                <h6 style={{ 
                                  fontSize: '0.75rem', 
                                  fontWeight: '600', 
                                  color: '#6c757d', 
                                  marginBottom: '0.5rem',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px'
                                }}>
                                  🤖 Detection Results
                                </h6>
                                <div style={{ fontSize: '0.875rem', color: '#495057' }}>
                                  <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between', 
                                    marginBottom: '0.25rem' 
                                  }}>
                                    <span>AI Probability:</span>
                                    <span style={{ 
                                      fontWeight: '600', 
                                      color: scan.analysis_result.ai_probability > 0.5 ? '#dc3545' : '#28a745' 
                                    }}>
                                      {(scan.analysis_result.ai_probability * 100).toFixed(2)}%
                                    </span>
                                  </div>
                                  <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between',
                                    marginBottom: '0.25rem' 
                                  }}>
                                    <span>Human Probability:</span>
                                    <span style={{ 
                                      fontWeight: '600', 
                                      color: scan.analysis_result.ai_probability > 0.5 ? '#28a745' : '#dc3545' 
                                    }}>
                                      {(scan.analysis_result.human_probability * 100).toFixed(2)}%
                                    </span>
                                  </div>
                                  <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between',
                                    marginBottom: '0.25rem' 
                                  }}>
                                    <span>Confidence:</span>
                                    <span style={{ fontWeight: '600' }}>
                                      {(scan.analysis_result.confidence * 100).toFixed(1)}%
                                    </span>
                                  </div>
                                  <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between',
                                    marginBottom: '0.25rem' 
                                  }}>
                                    <span>Classification:</span>
                                    <span style={{ fontWeight: '600' }}>
                                      {scan.analysis_result.classification}
                                    </span>
                                  </div>
                                  <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between' 
                                  }}>
                                    <span>Risk Level:</span>
                                    <span style={{ 
                                      fontWeight: '600',
                                      color: scan.analysis_result.risk_level === 'Very High' || scan.analysis_result.risk_level === 'High' ? '#dc3545' :
                                             scan.analysis_result.risk_level === 'Medium' ? '#ffc107' : '#28a745'
                                    }}>
                                      {scan.analysis_result.risk_level}
                                    </span>
                                  </div>
                                </div>
                              </div>

                              {/* Method Information */}
                              {scan.analysis_result.method_info && (
                                <div style={{ 
                                  backgroundColor: '#f8f9fa', 
                                  padding: '0.75rem', 
                                  borderRadius: '6px', 
                                  border: '1px solid #e9ecef' 
                                }}>
                                  <h6 style={{ 
                                    fontSize: '0.75rem', 
                                    fontWeight: '600', 
                                    color: '#6c757d', 
                                    marginBottom: '0.5rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px'
                                  }}>
                                    ⚙️ Detection Method
                                  </h6>
                                  <div style={{ fontSize: '0.875rem', color: '#495057' }}>
                                    <div style={{ marginBottom: '0.25rem' }}>
                                      <strong>Method:</strong> {scan.analysis_result.method_info.prediction_method || scan.analysis_result.method_info.method || 'Unknown'}
                                    </div>
                                    {scan.analysis_result.method_info.neural_prediction !== undefined && (
                                      <div style={{ marginBottom: '0.25rem' }}>
                                        <strong>Neural Model:</strong> {(scan.analysis_result.method_info.neural_prediction * 100).toFixed(1)}%
                                      </div>
                                    )}
                                    {scan.analysis_result.method_info.pattern_prediction !== undefined && (
                                      <div style={{ marginBottom: '0.25rem' }}>
                                        <strong>Pattern Analysis:</strong> {(scan.analysis_result.method_info.pattern_prediction * 100).toFixed(1)}%
                                      </div>
                                    )}
                                    {scan.analysis_result.method_info.rule_prediction !== undefined && (
                                      <div style={{ marginBottom: '0.25rem' }}>
                                        <strong>Rule-based:</strong> {(scan.analysis_result.method_info.rule_prediction * 100).toFixed(1)}%
                                      </div>
                                    )}
                                    {scan.analysis_result.method_info.agreement_score !== undefined && (
                                      <div>
                                        <strong>Agreement Score:</strong> {(scan.analysis_result.method_info.agreement_score * 100).toFixed(1)}%
                                      </div>
                                    )}
                                  </div>
                                </div>
                              )}

                              {/* Pattern Analysis */}
                              {scan.analysis_result.pattern_analysis && (
                                <div style={{ 
                                  backgroundColor: '#f8f9fa', 
                                  padding: '0.75rem', 
                                  borderRadius: '6px', 
                                  border: '1px solid #e9ecef' 
                                }}>
                                  <h6 style={{ 
                                    fontSize: '0.75rem', 
                                    fontWeight: '600', 
                                    color: '#6c757d', 
                                    marginBottom: '0.5rem',
                                    textTransform: 'uppercase',
                                    letterSpacing: '0.5px'
                                  }}>
                                    🔍 Pattern Analysis
                                  </h6>
                                  <div style={{ fontSize: '0.875rem', color: '#495057' }}>
                                    <div style={{ marginBottom: '0.25rem' }}>
                                      <strong>Patterns Detected:</strong> {scan.analysis_result.pattern_analysis.total_patterns || 0}
                                    </div>
                                    <div style={{ marginBottom: '0.25rem' }}>
                                      <strong>AI Score:</strong> {scan.analysis_result.pattern_analysis.ai_score?.toFixed(2) || 'N/A'}
                                    </div>
                                    <div>
                                      <strong>Human Score:</strong> {scan.analysis_result.pattern_analysis.human_score?.toFixed(2) || 'N/A'}
                                    </div>
                                  </div>
                                </div>
                              )}
                            </div>

                            {/* Feedback Messages */}
                            {scan.analysis_result.feedback_messages && scan.analysis_result.feedback_messages.length > 0 && (
                              <div style={{ 
                                marginTop: '1rem',
                                backgroundColor: '#e7f3ff', 
                                padding: '0.75rem', 
                                borderRadius: '6px', 
                                border: '1px solid #b3d9ff' 
                              }}>
                                <h6 style={{ 
                                  fontSize: '0.75rem', 
                                  fontWeight: '600', 
                                  color: '#0056b3', 
                                  marginBottom: '0.5rem',
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.5px'
                                }}>
                                  💡 Analysis Insights
                                </h6>
                                <div style={{ fontSize: '0.875rem', color: '#0056b3' }}>
                                  {scan.analysis_result.feedback_messages.slice(0, 3).map((message, idx) => (
                                    <div key={idx} style={{ marginBottom: '0.25rem' }}>
                                      • {message}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                        
                        {/* Fallback for old data format */}
                        {!scan.analysis_result && (
                          <div style={{ 
                            display: 'grid', 
                            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
                            gap: '1rem' 
                          }}>
                            {/* AI Detection Results */}
                            <div style={{ 
                              backgroundColor: '#f8f9fa', 
                              padding: '0.75rem', 
                              borderRadius: '6px', 
                              border: '1px solid #e9ecef' 
                            }}>
                              <h6 style={{ 
                                fontSize: '0.75rem', 
                                fontWeight: '600', 
                                color: '#6c757d', 
                                marginBottom: '0.5rem',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px'
                              }}>
                                🤖 Detection Results
                              </h6>
                              {scan.prediction ? (
                                <div>
                                  <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between', 
                                    marginBottom: '0.25rem' 
                                  }}>
                                    <span style={{ fontSize: '0.875rem', color: '#495057' }}>AI Generated:</span>
                                    <span style={{ 
                                      fontWeight: '600', 
                                      color: scan.prediction > 0.5 ? '#dc3545' : '#28a745' 
                                    }}>
                                      {(scan.prediction * 100).toFixed(2)}%
                                    </span>
                                  </div>
                                  <div style={{ 
                                    display: 'flex', 
                                    justifyContent: 'space-between' 
                                  }}>
                                    <span style={{ fontSize: '0.875rem', color: '#495057' }}>Human Written:</span>
                                    <span style={{ 
                                      fontWeight: '600', 
                                      color: scan.prediction > 0.5 ? '#28a745' : '#dc3545' 
                                    }}>
                                      {((1 - scan.prediction) * 100).toFixed(2)}%
                                    </span>
                                  </div>
                                </div>
                              ) : (
                                <span style={{ fontSize: '0.875rem', color: '#6c757d' }}>
                                  Analysis completed
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {/* Scan Details */}
                        <div style={{ 
                          marginTop: '1rem',
                          backgroundColor: '#f8f9fa', 
                          padding: '0.75rem', 
                          borderRadius: '6px', 
                          border: '1px solid #e9ecef' 
                        }}>
                          <h6 style={{ 
                            fontSize: '0.75rem', 
                            fontWeight: '600', 
                            color: '#6c757d', 
                            marginBottom: '0.5rem',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px'
                          }}>
                            📊 Scan Details
                          </h6>
                          <div style={{ fontSize: '0.875rem', color: '#495057' }}>
                            <div style={{ marginBottom: '0.25rem' }}>
                              <strong>Date:</strong> {new Date(scan.timestamp).toLocaleDateString('en-US', { 
                                weekday: 'short', 
                                year: 'numeric', 
                                month: 'short', 
                                day: 'numeric' 
                              })}
                            </div>
                            <div style={{ marginBottom: '0.25rem' }}>
                              <strong>Time:</strong> {new Date(scan.timestamp).toLocaleTimeString('en-US', { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              })}
                            </div>
                            {(scan.content_length || scan.text_length) && (
                              <div style={{ marginBottom: '0.25rem' }}>
                                <strong>Length:</strong> {(scan.content_length || scan.text_length)?.toLocaleString()} characters
                              </div>
                            )}
                            {(scan.file_name || scan.filename) && (
                              <div style={{ marginBottom: '0.25rem' }}>
                                <strong>File:</strong> {scan.file_name || scan.filename}
                              </div>
                            )}
                            {scan.source && (
                              <div>
                                <strong>Source:</strong> {scan.source === 'text_input' ? 'Text Input' : scan.source === 'file_upload' ? 'File Upload' : scan.source}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#6c757d' }}>
              <p>No scan history yet. Start analyzing content to see your history here!</p>
            </div>
          )}
        </div>
      )}
    </section>
  )
}