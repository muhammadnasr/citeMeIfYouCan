import { useState } from 'react';
import './AnswerDisplay.css';

/**
 * Component for displaying the answer with citations
 */
const AnswerDisplay = ({ answer, citations }) => {
  const [showCitations, setShowCitations] = useState(true);

  if (!answer) {
    return null;
  }

  return (
    <div className="answer-container">
      <div className="answer-content">
        <h2>Answer</h2>
        <div className="answer-text">
          {answer}
        </div>
      </div>

      <div className="citations-section">
        <div className="citations-header">
          <h3>Citations</h3>
          <button 
            className="toggle-citations"
            onClick={() => setShowCitations(!showCitations)}
          >
            {showCitations ? 'Hide Citations' : 'Show Citations'}
          </button>
        </div>
        
        {showCitations && citations && citations.length > 0 && (
          <ul className="citations-list">
            {citations.map((citation, index) => (
              <li key={index} className="citation-item">
                <div className="citation-source">
                  <strong>Source:</strong> {citation.source_doc_id}
                </div>
                <div className="citation-section">
                  <strong>Section:</strong> {citation.section_heading}
                </div>
                <div className="citation-link">
                  <a 
                    href={citation.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                  >
                    View Source Document
                  </a>
                </div>
              </li>
            ))}
          </ul>
        )}
        
        {showCitations && (!citations || citations.length === 0) && (
          <p className="no-citations">No citations available for this answer.</p>
        )}
      </div>
    </div>
  );
};

export default AnswerDisplay;
