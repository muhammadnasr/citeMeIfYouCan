import { useState } from 'react';
import './QuestionForm.css';

/**
 * Component for submitting questions
 */
const QuestionForm = ({ onSubmit, isLoading }) => {
  const [question, setQuestion] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim()) {
      onSubmit(question);
    }
  };

  return (
    <div className="question-form">
      <h2>Ask a Research Question</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Enter your research question..."
            disabled={isLoading}
            className="question-input"
          />
        </div>
        <button 
          type="submit" 
          disabled={!question.trim() || isLoading}
          className="submit-button"
        >
          {isLoading ? 'Searching...' : 'Get Answer'}
        </button>
      </form>
    </div>
  );
};

export default QuestionForm;
