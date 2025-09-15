import { Link, useNavigate } from 'react-router-dom';

export default function TermsOfService() {
  const navigate = useNavigate();
  return (
    <div className="legal-container">
      <div className="legal-content">
        <h1 className="legal-title">Terms of Service</h1>
        <p className="last-updated">Last updated: August 22, 2025</p>
        
        <section className="legal-section">
          <h2>1. Introduction</h2>
          <p>
            Welcome to AICD (AI Content Detector). By accessing or using our service, you agree to be bound by these Terms of Service.
          </p>
        </section>

        <section className="legal-section">
          <h2>2. Use of Service</h2>
          <p>
            Our service allows users to detect AI-generated content. You agree to use the service only for lawful purposes and in accordance with these Terms.
          </p>
        </section>

        <section className="legal-section">
          <h2>3. User Accounts</h2>
          <p>
            You may be required to create an account to access certain features. You are responsible for maintaining the confidentiality of your account information.
          </p>
        </section>

        <section className="legal-section">
          <h2>4. Intellectual Property</h2>
          <p>
            All content and materials available on our service are the property of AICD or its licensors and are protected by intellectual property laws.
          </p>
        </section>

        <section className="legal-section">
          <h2>5. Limitation of Liability</h2>
          <p>
            AICD shall not be liable for any indirect, incidental, special, or consequential damages resulting from the use or inability to use the service.
          </p>
        </section>

        <section className="legal-section">
          <h2>6. Changes to Terms</h2>
          <p>
            We reserve the right to modify these terms at any time. We will notify users of any changes by updating the "Last updated" date at the top of this page.
          </p>
        </section>

        <div className="legal-footer">
          <Link to="/privacy-policy" className="link">Privacy Policy</Link>
          <button onClick={() => navigate(-1)} className="btn btn-primary">
            <i className="fa-solid fa-arrow-left" aria-hidden="true"></i>
            <span>Back</span>
          </button>
        </div>
      </div>
    </div>
  );
}
