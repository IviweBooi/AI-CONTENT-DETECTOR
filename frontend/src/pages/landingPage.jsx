import { Link } from 'react-router-dom'
import detectIcon from '../assets/icons/detect.svg'

export default function LandingPage() {
  return (
    <main className="hero">
      {/* Decorative background */}
      <div className="hero-bg">
        <div className="glow glow-blue" />
        <div className="glow glow-teal" />
        <div className="grid-overlay" />
      </div>

      {/* Content */}
      <section className="hero-content">
        <p className="badge">Academic Integrity • AI Content Detection</p>
        <h1 className="headline">
          Detect AI‑generated content with
          <span className="gradient-text"> precision</span>
        </h1>
        <p className="subhead">
          Upload documents or paste text to instantly analyze authorship signals.
          Minimal noise. Actionable insights. Built for modern academia.
        </p>

        <div className="cta-row">
          <Link to="/content-detect" className="btn btn-primary">
            <img src={detectIcon} alt="detect" className="icon" aria-hidden="true" />
            <span>Start detecting now</span>
          </Link>
          <Link to="/learn" className="btn btn-ghost">Learn more</Link>
        </div>

        <ul className="trust-row">
          <li>Fast • Real‑time scoring</li>
          <li>Transparent • Highlighted cues</li>
          <li>Private • On‑device ready</li>
        </ul>
      </section>
    </main>
  )
}