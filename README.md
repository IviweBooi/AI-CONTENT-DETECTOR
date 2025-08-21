# AI Content Detector (AICD)

A full-stack web application that detects AI-generated content in academic or written submissions. Users can upload documents (.pdf, .docx, .txt) or paste text for analysis. The system provides an AI-likelihood score, highlights suspicious text, and generates detailed reports.

## Features

- 📝 Multiple input methods: Paste text or upload documents (PDF, DOCX, TXT)
- 🔍 AI content detection with confidence scoring
- 🎯 Likelihood classification (Human/AI) with 51%+ threshold
- 📊 Interactive results visualization
- 📥 Downloadable detailed reports
- 🔒 Secure and private processing
- 🎨 Modern, responsive UI with dark/light mode

## Tech Stack

- **Frontend**: React.js, Tailwind CSS
- **Backend**: Node.js, Express
- **AI Models**: Hugging Face Transformers
- **Document Processing**: pdf-parse, mammoth.js
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
   
   # Install backend dependencies
   cd ../backend
   npm install
   ```

3. Set up environment variables:
   Create a `.env` file in the backend directory with:
   ```
   PORT=5000
   HUGGINGFACE_API_KEY=your_api_key_here
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   npm start
   ```

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
