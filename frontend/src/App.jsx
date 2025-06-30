import { useState } from 'react'
import './App.css'
import QuestionForm from './components/QuestionForm'
import AnswerDisplay from './components/AnswerDisplay'
import { getAnswer } from './services/api'

function App() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [answerData, setAnswerData] = useState(null)

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
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} Cite Me If You Can - Semantic Search for Scientific Research</p>
      </footer>
    </div>
  )
}

export default App
