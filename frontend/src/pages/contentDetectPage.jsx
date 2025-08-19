import { useState, useRef, useEffect } from 'react'
import { incrementScan, addFeedback } from '../utils/metrics'
// ContentDetectPage – demo UI for the AI content detector.
// Notes:
// - This page simulates analysis on the client (no backend calls yet).
// - Results depend on text length to create deterministic mock values.

export default function ContentDetectPage() {
  // UI state
  const [activeTab, setActiveTab] = useState('text') // which tab is active: 'text' | 'file'
  const [text, setText] = useState('') // user input text
  const MAX_CHARS = 10000 // max characters allowed
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

  // Derived UI values (unique names to avoid redeclaration)
  const uiCharCount = text.length
  const uiCanAnalyze = text.trim().length >= 50
  const remainingSubmissions = Math.max(0, DAILY_LIMIT - submissionsUsed)

  // Trigger hidden file picker programmatically
  function onPickFile() { fileInputRef.current?.click() }

  // Handle incoming file (from drop or picker) with quick extension validation.
  function handleFile(file) {
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
    if (isTxt) {
      setFileError('')
      const reader = new FileReader()
      reader.onload = () => {
        let v = String(reader.result || '')
        if (v.length > MAX_CHARS) {
          v = v.slice(0, MAX_CHARS)
          setLimitNotice(`Input truncated to ${MAX_CHARS.toLocaleString()} characters.`)
        } else if (v.length > Math.floor(MAX_CHARS * 0.9)) {
          setLimitNotice(`Approaching limit: ${v.length.toLocaleString()}/${MAX_CHARS.toLocaleString()}`)
        } else {
          setLimitNotice('')
        }
        // set text to the truncated value
        setText(v)
      }
      reader.readAsText(file)
    } else {
      // DOCX/PDF accepted, but this demo cannot preview/parse them yet (to be implemented in the backend)
      setText('')
      setFileError('Cannot preview DOCX/PDF files yet. Please upload a TXT file to analyze.')
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

  // Perform a mock analysis. This simulates latency and produces
  // deterministic values based on content length just to test the UI.
  function analyze() {
    if (!text.trim()) return
    // Daily limit check (client-side demo)
    if (remainingSubmissions <= 0) {
      setSubmissionMsg('Daily limit exceeded. Try again tomorrow.')
      return
    }
    // Inform current remaining before processing
    setSubmissionMsg(`You have ${remainingSubmissions}/${DAILY_LIMIT} submissions remaining today.`)
    setIsAnalyzing(true)
    const start = performance.now()
    // Simulate scoring deterministically from content length
    const seed = Math.min(1000, text.trim().length)
    const base = (seed % 87) + 10 // 10 - 96
    const aiLikelihood = Math.min(99, Math.round(base * 0.78)) // overall % for the circle
    const perplex = (120 - (base % 60)).toFixed(1) // mock perplexity
    const burst = (2.2 + (base % 30) / 20).toFixed(1) // mock burstiness
    const metricsBars = {
      structure: (50 + (base % 45)), // 0-100 for progress bars
      vocabulary: (40 + (base % 50)),
      style: (30 + (base % 60)),
    }

    setTimeout(() => {
      // this is just a demo
      setResult({
        overall: base,
        aiLikelihood,
        metrics: { perplexity: perplex, burstiness: burst },
        metricsBars,
        // Legacy: keep snippets for fallback
        snippets: extractSnippets(text),
        // New: flagged spans within the original text
        flaggedSpans: computeFlaggedSpans(text)
      })
      const elapsed = ((performance.now() - start) / 1000).toFixed(1)
      setAnalysisTime(elapsed + 's')
      setIsAnalyzing(false)
      // On successful submission, increment and persist counters
      try { incrementScan() } catch {}
      setSubmissionsUsed((prev) => {
        const next = Math.min(DAILY_LIMIT, prev + 1)
        try {
          const today = new Date().toISOString().slice(0, 10)
          localStorage.setItem(STORAGE_KEY, JSON.stringify({ date: today, used: next }))
        } catch {
          // ignore storage errors in demo
        }
        const rem = Math.max(0, DAILY_LIMIT - next)
        setSubmissionMsg(`${rem}/${DAILY_LIMIT} daily submissions remaining.`)
        return next
      })
    }, 1000)
  }

  // this demo function is just to extract a few sentences for the highlights block
  function extractSnippets(t) {
    // Split into sentences
    const sents = String(t).replace(/\n+/g, ' ').split(/(?<=[.!?])\s+/).filter(Boolean)
    return sents.slice(0, 3)
  }

  // Compute a few deterministic in-text flagged spans (start,end) based on word positions
  function computeFlaggedSpans(t) {
    const str = String(t)
    if (!str.trim()) return []
    // Build word index map
    const words = []
    const re = /\S+/g
    let m
    // Find all words
    while ((m = re.exec(str)) !== null) {
      words.push({ start: m.index, end: m.index + m[0].length })
    }
    if (words.length === 0) return []
    const out = []
    // Pick up to 3 positions spread across the text deterministically
    const picks = [Math.floor(words.length * 0.2), Math.floor(words.length * 0.5), Math.floor(words.length * 0.8)]
    for (const idx of picks) {
      const w = words[Math.max(0, Math.min(words.length - 1, idx))]
      // Expand to include the next 2 words if available to create a small phrase
      const next1 = words[Math.min(words.length - 1, Math.max(0, idx + 1))]
      const next2 = words[Math.min(words.length - 1, Math.max(0, idx + 2))]
      const start = w.start
      const end = Math.max(w.end, next1.end, next2.end)
      out.push({ start, end })
    }
    // Deduplicate overlapping spans
    out.sort((a,b)=>a.start-b.start)
    const merged = []
    for (const s of out) {
      const last = merged[merged.length - 1]
      if (last && s.start <= last.end) {
        last.end = Math.max(last.end, s.end)
      } else {
        merged.push({ ...s })
      }
    }
    return merged.slice(0, 3)
  }

  // Renders a short excerpt around a flagged span with the span highlighted
  function HighlightExcerpt({ text: full, span, context = 60 }) {
    const s = Math.max(0, span.start)
    const e = Math.min(full.length, span.end)
    const beforeStart = Math.max(0, s - context)
    const afterEnd = Math.min(full.length, e + context)
    const before = full.slice(beforeStart, s)
    const mid = full.slice(s, e)
    const after = full.slice(e, afterEnd)
    const prefix = beforeStart > 0 ? '…' : ''
    const suffix = afterEnd < full.length ? '…' : ''
    return (
      <p>
        {prefix}{before}<mark>{mid}</mark>{after}{suffix}
      </p>
    )
  }

  // UI handlers
  function exportResults() { alert('Export feature is yet to be implemented.') }
  function provideFeedback() {
    try { addFeedback() } catch {}
    alert('Thanks for your feedback!')
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
                  setText(v)
                }}
              />
              <div className="input-info">
                <span id="char-count">{uiCharCount.toLocaleString()} / {MAX_CHARS.toLocaleString()} characters</span>
                <span className={`min-chars ${uiCanAnalyze ? 'ok' : ''}`}>Minimum 50 characters required</span>
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

            <button className="btn btn-primary analyze-btn" onClick={analyze} disabled={!uiCanAnalyze || isAnalyzing || remainingSubmissions === 0}>
              <i className="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
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
                  <div className="score-circle" style={{ ['--p']: `${result.aiLikelihood}%` }}>
                    <div className="score-value" id="score-value">{result.aiLikelihood}%</div>
                    <div className="score-label">AI content detected</div>
                  </div>
                  <div className="score-interpretation" id="score-interpretation">
                    <div className="interpretation-text">{result.aiLikelihood >= 60 ? 'Likely AI‑generated' : 'Likely human‑written'}</div>
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
                    {Array.isArray(result.flaggedSpans) && result.flaggedSpans.length > 0
                      ? result.flaggedSpans.map((span, i) => (
                          <HighlightExcerpt key={i} text={text} span={span} />
                        ))
                      : result.snippets.map((snip, i) => (
                          <p key={i}><mark>{snip}</mark></p>
                        ))}
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
    </section>
  )
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span className="metric-label">{label}</span>
      <div className="metric-bar"><div className="metric-fill" style={{ width: `${Math.min(100, Math.max(0, Math.round(value)))}%` }} /></div>
      <span className="metric-value">{Math.round(value)}%</span>
    </div>
  )
}