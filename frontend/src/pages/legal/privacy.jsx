import { Link, useNavigate } from 'react-router-dom';

export default function PrivacyPolicy() {
  const navigate = useNavigate();
  return (
    <div className="legal-container">
      <div className="legal-content">
        <h1 className="legal-title">Privacy Policy</h1>
        <p className="last-updated">Last updated: August 22, 2025</p>
        
        <section className="legal-section">
          <h2>1. Information We Collect</h2>
          <p>
            We collect information that you provide directly to us, such as when you create an account, use our service, or contact us. This may include:
          </p>
          <ul>
            <li>Contact information (name, email address)</li>
            <li>Account credentials</li>
            <li>Content you submit for analysis</li>
            <li>Usage data and analytics</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>2. How We Use Your Information</h2>
          <p>We use the information we collect to:</p>
          <ul>
            <li>Provide, maintain, and improve our services</li>
            <li>Process transactions and send related information</li>
            <li>Respond to your comments, questions, and requests</li>
            <li>Monitor and analyze usage and trends</li>
            <li>Detect, investigate, and prevent security incidents</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>3. Data Security</h2>
          <p>
            We implement appropriate technical and organizational measures to protect your personal information. However, no method of transmission over the internet is 100% secure.
          </p>
        </section>

        <section className="legal-section">
          <h2>4. Data Retention</h2>
          <p>
            We retain your personal information only for as long as necessary to provide you with our services and as described in this Privacy Policy.
          </p>
        </section>

        <section className="legal-section">
          <h2>5. Your Rights</h2>
          <p>You have the right to:</p>
          <ul>
            <li>Access the personal information we hold about you</li>
            <li>Request correction of your personal information</li>
            <li>Request deletion of your personal information</li>
            <li>Object to or restrict processing of your personal information</li>
            <li>Request transfer of your personal information</li>
          </ul>
        </section>

        <section className="legal-section">
          <h2>6. Changes to This Policy</h2>
          <p>
            We may update our Privacy Policy from time to time. We will notify you of any changes by updating the "Last updated" date at the top of this page.
          </p>
        </section>

        <div className="legal-footer">
          <Link to="/terms" className="link">Terms of Service</Link>
          <button onClick={() => navigate(-1)} className="btn btn-primary">
            <i className="fa-solid fa-arrow-left" aria-hidden="true"></i>
            <span>Back</span>
          </button>
        </div>
      </div>
    </div>
  );
}
