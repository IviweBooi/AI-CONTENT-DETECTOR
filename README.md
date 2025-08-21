# AI Content Detector (AICD)

A full-stack web application that detects AI-generated content in academic or written submissions. Users can upload documents (.pdf, .docx, .txt) or paste text for analysis. The system provides an AI-likelihood score, highlights suspicious text, and generates detailed reports.

## Features

- 📝 Multiple input methods: Paste text or upload documents (PDF, DOCX, TXT)
- 🔍 AI content detection with confidence scoring
- 🎯 Likelihood classification (Human/AI) with 51%+ threshold
- 📊 Interactive results visualisation
- 📥 Downloadable detailed reports
- 🔒 Secure and private processing
- 🎨 Modern, responsive UI 

## Tech Stack

- **Frontend**: React.js
- **State Management**: React Context API
- **Build Tool**: Vite

## Getting Started

### Prerequisites

- Node.js (v16 or later)
- npm or yarn
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone [repository-url]
   cd AICD
   ```

2. Install dependencies:
   ```bash
   # Install frontend dependencies
   cd frontend
   npm install


### Running the Application

2. In a new terminal, start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open your browser and navigate to `http://localhost:5173`

## Usage

1. Navigate to the application in your web browser
2. Choose to either paste text or upload a document
3. Click "Analyze" to process the content
4. View the AI detection results, including:
   - AI likelihood score
   - Likelihood classification
   - Highlighted suspicious text
   - Detailed analysis
5. Download a PDF report if needed


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
