import { Link } from 'react-router-dom';
import './ErrorPage.css';

export default function ErrorPage() {
    return (
        <div className="error-container">
            <div className="error-card">
                <div className="error-header">
                    <div className="error-icon">
                        <svg 
                            fill="none" 
                            stroke="currentColor" 
                            viewBox="0 0 24 24" 
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path 
                                strokeLinecap="round" 
                                strokeLinejoin="round" 
                                strokeWidth={2} 
                                d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
                            />
                        </svg>
                    </div>
                    <h1 className="error-title">404 - Page Not Found</h1>
                    <p className="error-description">
                        Oops! The page you're looking for doesn't exist or has been moved.
                    </p>
                </div>
                
                <div className="error-actions">
                    <Link to="/" className="error-button primary-button">
                        <svg className="button-icon" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm.707-10.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L9.414 11H13a1 1 0 100-2H9.414l1.293-1.293z" clipRule="evenodd" />
                        </svg>
                        Return Home
                    </Link>
                    <Link to="/help" className="error-button secondary-button">
                        <svg className="button-icon" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                        </svg>
                        Get Help
                    </Link>
                </div>
                
                <div className="error-footer">
                    <p>
                        Think this is a mistake?{' '}
                        <a href="mailto:support@aicd.com">Contact support</a>
                    </p>
                </div>
            </div>
        </div>
    );
}