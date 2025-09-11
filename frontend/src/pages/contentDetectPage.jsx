import { useState, useRef, useEffect } from 'react'
import detectIcon from '../assets/icons/detect.svg'
import { analyzeText, analyzeFile, submitFeedback, trackScan, exportReport } from '../services/api'
// ContentDetectPage – demo UI for the AI content detector.
// Notes:
// - This page now uses API services for analysis.
// - Results are fetched from the backend API.

export default function ContentDetectPage() {
  // UI state
  const [activeTab, setActiveTab] = useState('text') // which tab is active: 'text' | 'file'
  const [text, setText] = useState('') // user input text
  const MIN_CHARS = 500 // minimum characters for better analysis accuracy
  const MAX_CHARS = 2000 // max characters allowed (optimized for RoBERTa's 512 token limit)
  const [limitNotice, setLimitNotice] = useState('') // warning/notice when approaching/reaching limit
  const [isAnalyzing, setIsAnalyzing] = useState(false) // loading state during analysis
  const [result, setResult] = useState(null) // analysis result object or null
  const [analysisTime, setAnalysisTime] = useState(null) // elapsed analysis time string, e.g. "1.2s"
  const [isDragging, setIsDragging] = useState(false) // drag-over visual state for file drop
  const [fileName, setFileName] = useState('') // selected file name (for preview)
  const [fileError, setFileError] = useState('') // instant feedback for unsupported files
  const fileInputRef = useRef(null) // hidden file input ref

  // Daily submission limit (client-side demo)
  const DAILY_LIMIT = 100
  const STORAGE_KEY = 'aicd_daily_counter'
  const [submissionsUsed, setSubmissionsUsed] = useState(0)
  const [submissionMsg, setSubmissionMsg] = useState('')

  // Feedback modal state
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [feedbackType, setFeedbackType] = useState('');
  const [feedbackComment, setFeedbackComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccessMessage, setShowSuccessMessage] = useState(false);

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    if (!feedbackType || isSubmitting) return;
    
    setIsSubmitting(true);
    
    try {
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
        fileName: file.name
      });
      
      return response.data;
    } catch (error) {
      console.error('File analysis error:', error);
      setSubmissionMsg('An error occurred analyzing the file. Please try again.');
      return null;
    } finally {
      setIsAnalyzing(false);
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
    
    setIsAnalyzing(true)
    const startTime = performance.now()
    
    try {
      // Use the API service to analyze the file
      const response = await analyzeFile(file)
      
      if (!response.success) {
        throw new Error(response.error || 'File analysis failed')
      }
      
      setResult(response.data)
      const elapsed = ((performance.now() - startTime) / 1000).toFixed(1)
      setAnalysisTime(elapsed + 's')
      
      // Extract text for display
      if (response.data.text) {
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
      }
      
      // Track scan with file metadata
      trackScan({
        contentType: 'file',
        contentLength: file.size,
        fileName: file.name
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
      setFileError('Error processing file. Please try another file.')
      setFileName('')
      setText('')
    } finally {
      setIsAnalyzing(false)
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
      
      // Track scan with content metadata
      trackScan({
        contentType: 'text',
        contentLength: text.length
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
  async function exportResults(format = 'pdf') {
    if (!result) {
      alert('No results to export.');
      return;
    }
    
    try {
      // Use the API service to export results
      const response = await exportReport(result, format);
      
      if (!response.success) {
        throw new Error(response.error || 'Export failed');
      }
      
      // In a real implementation with actual file download
      alert(`Report exported in ${format} format successfully!`);
      console.log('Export response:', response);
    } catch (error) {
      console.error('Error exporting report:', error);
      alert('Failed to export report. Please try again.');
    }
  }
  const provideFeedback = () => setShowFeedbackModal(true);
  
  // Increment scan counter for analytics
  function incrementScan() {
    // This function now uses the API service
    trackScan()
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
              {fileName && (
                <div className="uploaded-file">
                  <div className="file-info">
                    <i className="fa-solid fa-file-lines" aria-hidden="true"></i>
                    <span className="file-name">{fileName}</span>
                    <button className="remove-file" onClick={() => { setFileName(''); setText(''); setFileError('') }}>✕</button>
                  </div>
                </div>
              )}
            </div>

            <button 
              className="btn btn-primary analyze-btn" 
              onClick={analyze} 
              disabled={text.length < MIN_CHARS || isAnalyzing || remainingSubmissions === 0}
            >
              <img src={detectIcon} alt="detect" height="20" />
              <span>{isAnalyzing ? 'Analyzing…' : 'Analyze'}</span>
              {isAnalyzing && <span className="loading-spinner" />}
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
                  <div className="score-circle" style={{ '--p': `${result.aiLikelihood}%` }}>
                    <div className="score-value" id="score-value">{result.aiLikelihood}%</div>
                    <div className="score-label">AI content detected</div>
                  </div>
                  <div className="score-interpretation" id="score-interpretation">
                    <div className="interpretation-text">{result.aiLikelihood >= 51 ? 'Likely AI‑generated' : 'Likely human‑written'}</div>
                    <div className="interpretation-desc">Preview estimate based on AI patterns</div>
                  </div>
                </div>

                <div className="detailed-analysis">
                  <h4>Detailed Analysis</h4>
                  <div className="analysis-metrics">
                    <Metric label="Sentence Structure" value={result.metricsBars.structure} />
                    <Metric label="Vocabulary Patterns" value={result.metricsBars.vocabulary} />
                    <Metric label="Writing Style" value={result.metricsBars.style} />
                  </div>
                </div>

                <div className="content-highlights" id="content-highlights">
                  <h4>Flagged Sections</h4>
                  <div className="highlighted-content">
                    <p>Flagged content will appear here when the backend is implemented.</p>
                  </div>
                </div>

                <div className="results-actions">
                  <button className="btn btn-ghost" onClick={exportResults}>
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
            <span>Thank you for your feedback! We appreciate your input.</span>
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
                  {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  )
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span className="metric-label">{label}</span>
      <div className="metric-bar">
        <div className="metric-fill" style={{ width: `${Math.min(100, Math.max(0, Math.round(value)))}%` }} />
      </div>
      <span className="metric-value">{Math.round(value)}%</span>
    </div>
  )
}