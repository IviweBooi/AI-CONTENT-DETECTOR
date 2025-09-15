import { useEffect, useMemo, useState } from 'react'


export default function LearnPage() {
  // Fixed metrics for demo
  const stats = [
    { label: 'Scans Completed', value: 1000, suffix: '' },
    { label: 'Model Accuracy', value: 85, suffix: '%' },
  ]

  // Scroll-reveal on mount
  useEffect(() => {
    const els = document.querySelectorAll('[data-reveal]')
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('in') })
    }, { threshold: 0.12 })
    els.forEach((el) => io.observe(el))
    return () => io.disconnect()
  }, [])

  return (
    <main className="learn-page">
      {/* Hero */}
      <section className="learn-hero" data-reveal>
        <div className="container">
          <h1 className="learn-title">AI content detection that puts clarity first</h1>
          <p className="learn-subhead">
            Paste text or upload a document and get a fast, transparent assessment with clear cues.
            Designed for educators, students and reviewers who value originality.
          </p>
          <div className="cta-row">
            <a className="btn btn-primary animated-btn" href="/content-detect">Try the Detector</a>
          </div>
        </div>
      </section>

      {/* Key Performance Indicators (KPIs) - This section displays the metrics for the AI content detector */}
      <section className="learn-section" id="kpis" data-reveal>
        <ul className="kpi-grid">
          {/* Map over the stats array to display each metric */}
          {stats.map((s, i) => (
            <li className="kpi-card" key={i}>
              <div className="kpi-value">{s.value}<span className="kpi-suffix">{s.suffix}</span></div>
              <div className="kpi-label">{s.label}</div>
            </li>
          ))}
        </ul>
      </section>

      {/* What it does (concise) */}
      <section className="learn-section glass-card" id="purpose" data-reveal>
        <h2>What it does</h2>
        <p>
          Detects likely AI‑generated writing and highlights patterns so you can review with context.
          Upload .docx/.pdf/.txt or paste text, then export a report for record‑keeping.
        </p>
      </section>

      {/* Who it helps */}
      <section className="learn-section" id="stakeholders" data-reveal>
        <h2>Who it helps</h2>
        <ul className="card-grid">
          <li className="card"><h3>Educators</h3><p>Review submissions with evidence‑based cues.</p></li>
          <li className="card"><h3>Students</h3><p>Self‑check drafts and learn to write with originality.</p></li>
          <li className="card"><h3>Admins & Reviewers</h3><p>Adopt consistent, transparent workflows.</p></li>
        </ul>
      </section>

      {/* Features */}
      <section className="learn-section" id="features" data-reveal>
        <h2>Features</h2>
        <div className="feature-grid">
          <div className="feature"><h3>Fast results</h3><p>Clear scores in seconds for ~1000 words.</p></div>
          <div className="feature"><h3>Explainability</h3><p>Highlights and metrics to support decisions.</p></div>
          <div className="feature"><h3>Reports</h3><p>Export findings for follow‑up or records.</p></div>
          <div className="feature"><h3>History</h3><p>Signed‑in users get a dashboard of past scans and reports.</p></div>
          <div className="feature"><h3>Uploads</h3><p>TXT, DOCX, PDF (size limits apply).</p></div>
          <div className="feature"><h3>Access control</h3><p>Authentication for protected features.</p></div>
        </div>
      </section>


      {/* Call-to-action (CTA) - This section encourages users to try the AI content detector */}
      <section className="learn-cta" data-reveal>
        <div className="container">
          <h2>Run your first scan</h2>
          <p>Start with a sample paragraph or upload a document.</p>
          <div className="cta-row">
            <a className="btn btn-primary animated-btn" href="/content-detect">Analyze Content</a>
          </div>
        </div>
      </section>
    </main>
  )
}