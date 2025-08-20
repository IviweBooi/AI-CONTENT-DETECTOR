export default function HelpPage() {
    return (
        <div className="help-page">
            <h1>Help & Support</h1>
            <div className="help-content">
                <section className="help-section">
                    <h2>Frequently Asked Questions</h2>
                    <div className="faq-list">
                        <div className="faq-item">
                            <h3>How do I detect AI content?</h3>
                            <p>Navigate to the Detect Content page and upload your text or document for analysis.</p>
                        </div>
                        <div className="faq-item">
                            <h3>What file types are supported?</h3>
                            <p>We support .txt, .docx, and .pdf file formats for content analysis.</p>
                        </div>
                        <div className="faq-item">
                            <h3>How accurate is the detection?</h3>
                            <p>Our model has an accuracy of over 85% in detecting AI-generated content.</p>
                        </div>
                    </div>
                </section>
                
                <section className="help-section">
                    <h2>Need More Help?</h2>
                    <p>If you can't find what you're looking for, please contact our support team.</p>
                    <a href="mailto:support@aicdetector.com" className="contact-link">
                        Contact Support
                    </a>
                </section>
            </div>
        </div>
    );
}
