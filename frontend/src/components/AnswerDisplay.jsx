import { useState } from 'react';

/**
 * Component for displaying the answer with citations
 */
const AnswerDisplay = ({ answer, citations }) => {
  const [showCitations, setShowCitations] = useState(true);

  if (!answer) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Answer</h2>
        <div className="prose prose-blue max-w-none text-gray-700">
          {answer.split('\n').map((paragraph, i) => (
            paragraph ? <p key={i} className="mb-4">{paragraph}</p> : <br key={i} />
          ))}
        </div>
      </div>

      <div className="mt-8 border-t pt-6 border-gray-200">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-800">Citations</h3>
          <button 
            className="px-3 py-1 text-sm rounded border border-gray-300 hover:bg-gray-100 transition-colors duration-200 flex items-center gap-1"
            onClick={() => setShowCitations(!showCitations)}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              {showCitations ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              )}
            </svg>
            {showCitations ? 'Hide Citations' : 'Show Citations'}
          </button>
        </div>
        
        {showCitations && citations && citations.length > 0 && (
          <div className="space-y-4">
            {citations.map((citation, index) => (
              <div key={index} className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">Source:</span>{' '}
                    <span className="text-gray-600">{citation.source_doc_id}</span>
                  </div>
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">Section:</span>{' '}
                    <span className="text-gray-600">{citation.section_heading}</span>
                  </div>
                </div>
                
                <div className="bg-white p-3 rounded border border-blue-100 mb-3">
                  <p className="text-sm text-gray-700">{citation.text}</p>
                </div>
                
                <div className="flex justify-end">
                  <a 
                    href={citation.link} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-sm text-primary hover:text-blue-700 font-medium"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    View Source Document
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {showCitations && (!citations || citations.length === 0) && (
          <p className="text-sm text-gray-600">No citations available for this answer.</p>
        )}
      </div>
    </div>
  );
};

export default AnswerDisplay;
