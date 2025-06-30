/**
 * API service for interacting with the backend
 */

const API_URL = 'http://localhost:8000';

/**
 * Send a question to the API and get an answer with citations
 * @param {string} question - The user's question
 * @param {number} k - Number of results to retrieve (default: 10)
 * @param {number} minScore - Minimum similarity score (default: 0.25)
 * @returns {Promise} - Promise resolving to the answer and citations
 */
export const getAnswer = async (question, k = 10, minScore = 0.25) => {
  try {
    const response = await fetch(`${API_URL}/api/question_answer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        k,
        min_score: minScore,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get answer');
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting answer:', error);
    throw error;
  }
};

/**
 * Perform a direct similarity search
 * @param {string} query - The search query
 * @param {number} k - Number of results to retrieve
 * @param {number} minScore - Minimum similarity score
 * @returns {Promise} - Promise resolving to search results
 */
export const similaritySearch = async (query, k = 10, minScore = 0.25) => {
  try {
    const response = await fetch(`${API_URL}/api/similarity_search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        k,
        min_score: minScore,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to perform search');
    }

    return await response.json();
  } catch (error) {
    console.error('Error performing search:', error);
    throw error;
  }
};
