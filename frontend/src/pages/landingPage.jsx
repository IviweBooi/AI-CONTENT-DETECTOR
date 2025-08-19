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
        <h1 className="headline animated-headline">
          <span className="word" style={{ ['--i']: 0 }}>Detect</span>
          <span> </span>
          <span className="word" style={{ ['--i']: 1 }}>AI‑generated</span>
          <span> </span>
          <span className="word" style={{ ['--i']: 2 }}>content</span>
          <span> </span>
          <span className="word" style={{ ['--i']: 3 }}>with</span>
          <span> </span>
          <span className="gradient-text word" style={{ ['--i']: 4 }}>precision</span>
        </h1>
        <p className="subhead animated-subhead">
          Upload documents or paste text to instantly analyze authorship signals.
          Minimal noise. Actionable insights. Built for modern academia.
        </p>

        <div className="cta-row">
          <Link to="/content-detect" className="btn btn-primary animated-btn">
            <img src={detectIcon} alt="detect" className="icon" aria-hidden="true" />
            <span>Start detecting now</span>
          </Link>
          <Link to="/learn" className="btn btn-ghost animated-btn">Learn more</Link>
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