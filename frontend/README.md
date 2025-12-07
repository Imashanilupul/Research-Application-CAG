# Research Assistant for PDFs - Frontend

A React-based frontend for the Research Assistant application that allows users to upload research papers in PDF format, view AI-generated structured summaries, and ask questions about the papers using a RAG-powered chatbot.

## Features

- **PDF Upload**: Drag-and-drop or click to upload research papers
- **Structured Summary**: Automatic generation of summaries with:
  - Title & Authors
  - Abstract
  - Problem Statement
  - Methodology
  - Key Results
  - Conclusion
- **Q&A Chatbot**: Ask natural language questions about the uploaded paper
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 19** - UI library
- **Vite** - Build tool and dev server
- **CSS3** - Modern styling with animations and gradients

## Prerequisites

- Node.js 18+ (LTS recommended)
- npm or yarn
- Backend server running on port 8000

## Setup Instructions

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env if your backend runs on a different port
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

4. **Open in browser**:
   Navigate to http://localhost:5173

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

## Build for Production

```bash
npm run build
npm run preview  # Preview production build locally
```

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── FileUpload.jsx    # PDF upload with drag-drop
│   │   ├── SummaryDisplay.jsx # Structured summary display
│   │   └── ChatInterface.jsx  # Q&A chatbot
│   ├── services/
│   │   └── api.js       # API communication layer
│   ├── App.jsx          # Main application component
│   ├── App.css          # Application styles
│   ├── index.css        # Global styles
│   └── main.jsx         # Entry point
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
└── package.json         # Dependencies and scripts
```

## API Endpoints Used

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/upload` | Upload PDF and get summary |
| GET | `/documents/list` | List all uploaded documents |
| POST | `/qa/ask` | Ask a question about a document |
| GET | `/health/` | Check API health status |

## Development

### Code Style

- ESLint is configured for code quality
- Run `npm run lint` to check for issues

### Adding New Features

1. Create components in `src/components/`
2. Export from `src/components/index.js`
3. Add API calls to `src/services/api.js`

