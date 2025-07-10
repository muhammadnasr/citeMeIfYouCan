import { useState, useEffect } from 'react'
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
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="max-w-5xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        <header className="text-center mb-12 pb-6 border-b border-gray-200">
          <h1 className="text-4xl md:text-5xl font-bold text-primary mb-3">Cite Me If You Can</h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Ask questions about scientific research and get answers with proper citations
          </p>
        </header>

        <main className="space-y-8">
          <div className="card hover:shadow-lg transition-shadow duration-300">
            <QuestionForm 
              onSubmit={handleQuestionSubmit} 
              isLoading={isLoading} 
            />
          </div>
          
          {isLoading && (
            <div className="flex justify-center py-10">
              <div className="animate-pulse flex flex-col items-center">
                <div className="h-12 w-12 rounded-full border-4 border-t-primary border-primary/30 animate-spin mb-4"></div>
                <p className="text-gray-600 italic">Searching for relevant information...</p>
              </div>
            </div>
          )}
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-lg">
              <p className="font-medium">Error: {error}</p>
            </div>
          )}
          
          {answerData && (
            <div className="space-y-8">
              <div className="bg-white rounded-xl shadow-md overflow-hidden border border-indigo-50">
                <div className="bg-gradient-to-r from-indigo-50 to-blue-50 px-6 py-4 border-b border-indigo-100">
                  <h2 className="text-xl font-semibold text-gray-800">Research Answer</h2>
                </div>
                <div className="p-6">
                  <AnswerDisplay 
                    answer={answerData.answer} 
                    citations={answerData.citations} 
                  />
                </div>
              </div>
              
              {sessionCitations.length > 0 && (
                <div className="bg-white rounded-xl shadow-md overflow-hidden border border-indigo-50">
                  <div className="bg-gradient-to-r from-indigo-50 to-blue-50 px-6 py-4 border-b border-indigo-100">
                    <h2 className="text-xl font-semibold text-gray-800">Citation Analysis</h2>
                  </div>
                  <div className="p-6">
                    <CitationChart citations={sessionCitations} />
                  </div>
                </div>
              )}
            </div>
          )}
        </main>

        <footer className="mt-16 pt-6 border-t border-gray-200 text-center text-gray-500 text-sm">
          <p>&copy; {new Date().getFullYear()} Cite Me If You Can - Semantic Search for Scientific Research</p>
        </footer>
      </div>
    </div>
  )
}

export default App
