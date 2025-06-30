import { useState, useEffect } from 'react'
import './App.css'
import QuestionForm from './components/QuestionForm'
import AnswerDisplay from './components/AnswerDisplay'
import CitationChart from './components/CitationChart'
import { getAnswer } from './services/api'

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [answerData, setAnswerData] = useState(null)
  const [sessionCitations, setSessionCitations] = useState([])

  // Update session citations whenever we get new answer data with citations
  useEffect(() => {
    if (answerData && answerData.citations && answerData.citations.length > 0) {
      // Track the new answer's citations separately to avoid duplicate counting
      const newCitations = answerData.citations.map(citation => ({
        ...citation,
        answerId: Date.now() // Add a unique ID to group citations by answer
      }));
      setSessionCitations(prevCitations => [...prevCitations, ...newCitations]);
    }
  }, [answerData])

  const handleQuestionSubmit = async (question) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const data = await getAnswer(question)
      setAnswerData(data)
    } catch (err) {
      setError(err.message || 'Failed to get answer. Please try again.')
      setAnswerData(null)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Cite Me If You Can</h1>
        <p className="app-description">
          Ask questions about scientific research and get answers with proper citations
        </p>
      </header>

      <main className="app-content">
        <QuestionForm 
          onSubmit={handleQuestionSubmit} 
          isLoading={isLoading} 
        />
        
        {isLoading && (
          <div className="loading-indicator">
            <p>Searching for relevant information...</p>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        {answerData && (
          <AnswerDisplay 
            answer={answerData.answer} 
            citations={answerData.citations} 
          />
        )}
        
        {/* Citation chart showing most cited articles in this session */}
        <CitationChart citations={sessionCitations} />
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} Cite Me If You Can - Semantic Search for Scientific Research</p>
      </footer>
    </div>
  )
}

export default App
