import { useEffect } from 'react';

export default function HelpPage() {
    // Set up intersection observer for reveal animations
    useEffect(() => {
        const els = document.querySelectorAll('[data-reveal]');
        const io = new IntersectionObserver((entries) => {
            entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('in') });
        }, { threshold: 0.12 });
        els.forEach((el) => io.observe(el));
        return () => io.disconnect();
    }, []);

    return (
        <div className="help-page" data-reveal>
            <h1>Help & Support</h1>
            <div className="help-content">
                <section className="help-section" data-reveal>
                    <h2>Frequently Asked Questions</h2>
                    <div className="faq-list" data-reveal style={{"transitionDelay": "0.1s"}}>
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
                
                <section className="help-section contact-section" data-reveal style={{"transitionDelay": "0.2s"}}>
                    <h2>Contact Us</h2>
                    <p>If you can't find what you're looking for, our support team is here to help.</p>
                    
                    <div className="contact-options">
                        <div className="contact-method">
                            <div className="contact-icon">
                                <i className="fas fa-envelope"></i>
                            </div>
                            <h3>Email Us</h3>
                            <p>Send us an email and we'll get back to you within 24 hours.</p>
                            <a href="mailto:support@aicdetector.com" className="btn btn-outline">
                                support@aicdetector.com
                            </a>
                        </div>

                        <div className="contact-method">
                            <div className="contact-icon">
                                <i className="fas fa-phone"></i>
                            </div>
                            <h3>Call Us</h3>
                            <p>Available Monday to Friday, 9AM to 5PM</p>
                            <a href="tel:+27821234567" className="btn btn-outline">
                                +27 82 123 4567
                            </a>
                        </div>

                    </div>

                </section>
            </div>
        </div>
    );
}
