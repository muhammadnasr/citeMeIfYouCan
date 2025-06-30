# Cite Me If You Can - Frontend

A React-based single-page web application that allows users to ask natural language questions about scientific research and receive AI-generated answers with proper citations.

## Features

- User-friendly interface for asking research questions
- Integration with backend semantic search API
- Display of AI-generated answers with proper citations
- Citation display showing source document, section heading, and clickable links

## Project Structure

- `src/components/` - React components for the UI
- `src/services/` - API services for backend communication

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev
```

The development server will start at http://localhost:5173 by default.

### Building for Production

```bash
# Build for production
npm run build
```

The build output will be in the `dist` directory.

## API Integration

The frontend communicates with the backend API using the following endpoints:

- `POST /api/question_answer` - Submit a question and get an AI-generated answer with citations
- `POST /api/similarity_search` - Perform a direct semantic search query

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
