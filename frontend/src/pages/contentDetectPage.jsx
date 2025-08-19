import { useState, useRef, useEffect } from 'react'
// ContentDetectPage – demo UI for an AI content detector.
// Notes:
// - This page simulates analysis on the client (no backend calls).
// - Results depend on text length to create deterministic mock values.

export default function ContentDetectPage() {
  // UI state
  const [activeTab, setActiveTab] = useState('text') // which tab is active: 'text' | 'file'
  const [text, setText] = useState('') // user input text
  const [isAnalyzing, setIsAnalyzing] = useState(false) // loading state during analysis
  const [result, setResult] = useState(null) // analysis result object or null
  const [analysisTime, setAnalysisTime] = useState(null) // elapsed analysis time string, e.g. "1.2s"
  const [isDragging, setIsDragging] = useState(false) // drag-over visual state for file drop
  const [fileName, setFileName] = useState('') // selected file name (for preview)
  const fileInputRef = useRef(null) // hidden file input ref

  // Set up a light intersection observer for small reveal animations.
  useEffect(() => {
    const els = document.querySelectorAll('[data-reveal]')
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('in') })
    }, { threshold: 0.12 })
    els.forEach((el) => io.observe(el))
    return () => io.disconnect()
  }, [])

  // Trigger hidden file picker programmatically
  function onPickFile() { fileInputRef.current?.click() }

  // Handle incoming file (from drop or picker). For the demo, only read text-like files.
  function handleFile(file) {
    if (!file) return
    setFileName(file.name)
    // Only read as text for txt-like files in this mock
    if (/\.txt$|\.md$|\.csv$/i.test(file.name)) {
      const reader = new FileReader()
      reader.onload = () => setText(String(reader.result || ''))
      reader.readAsText(file)
    } else {
      // Unsupported parse in demo
      setText('')
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

  // Perform a mock analysis locally. This simulates latency and produces
  // deterministic values based on content length so you can test the UI.
  function analyze() {
    if (!text.trim()) return
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
    const signals = [
      { label: 'Repetitiveness', value: (base % 100) }, // additional demo signals
      { label: 'Function-word ratio', value: (60 + (base % 35)) },
      { label: 'Sentence uniformity', value: (50 + (base % 45)) },
    ]

    setTimeout(() => {
      // Populate the result with all fields the UI expects
      setResult({
        overall: base,
        aiLikelihood,
        metrics: { perplexity: perplex, burstiness: burst },
        metricsBars,
        signals,
        snippets: extractSnippets(text)
      })
      const elapsed = ((performance.now() - start) / 1000).toFixed(1)
      setAnalysisTime(elapsed + 's')
      setIsAnalyzing(false)
    }, 1000)
  }

  // Very small helper to grab a few sentences for the highlights block
  function extractSnippets(t) {
    const sents = String(t).replace(/\n+/g, ' ').split(/(?<=[.!?])\s+/).filter(Boolean)
    return sents.slice(0, 3)
  }

  // Action stubs for demo buttons
  function exportResults() { alert('Export is a stub in this demo.') }
  function provideFeedback() { alert('Feedback is a stub in this demo.') }

  // Derived UI values
  const charCount = text.length
  const canAnalyze = text.trim().length >= 50 // enable analyze when min chars reached

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
                onChange={(e) => setText(e.target.value)}
              />
              <div className="input-info">
                <span id="char-count">{charCount} characters</span>
                <span className={`min-chars ${canAnalyze ? 'ok' : ''}`}>Minimum 50 characters required</span>
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
                <input ref={fileInputRef} type="file" id="file-input" accept=".txt,.md,.csv,.docx,.pdf" hidden onChange={onFileChosen} />
                <div className="supported-formats">Supported: TXT, DOCX, PDF (max 10MB)</div>
              </div>
              {fileName && (
                <div className="uploaded-file">
                  <div className="file-info">
                    <i className="fa-solid fa-file-lines" aria-hidden="true"></i>
                    <span className="file-name">{fileName}</span>
                    <button className="remove-file" onClick={() => { setFileName(''); setText('') }}>✕</button>
                  </div>
                </div>
              )}
            </div>

            <button className="btn btn-primary analyze-btn" onClick={analyze} disabled={!canAnalyze || isAnalyzing}>
              <i className="fa-solid fa-magnifying-glass" aria-hidden="true"></i>
              <span>{isAnalyzing ? 'Analyzing…' : 'Analyze'}</span>
              {isAnalyzing && <span className="loading-spinner" />}
            </button>
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
                    <div className="score-label">AI Confidence</div>
                  </div>
                  <div className="score-interpretation" id="score-interpretation">
                    <div className="interpretation-text">{result.aiLikelihood >= 60 ? 'Likely AI‑generated' : 'Likely human‑written'}</div>
                    <div className="interpretation-desc">Preview estimate based on surface‑level signals only.</div>
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
                    {result.snippets.map((snip, i) => (
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