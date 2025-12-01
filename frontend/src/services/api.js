/**
 * API service for communicating with the backend
 */

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Submit a query to the LLM Council pipeline
 * @param {string} query - User query
 * @param {object} options - Optional query options
 * @returns {Promise<object>} - Pipeline response
 */
export async function submitQuery(query, options = {}) {
  const response = await fetch(`${API_URL}/api/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      options: {
        use_cache: options.use_cache !== false,
        timeout: options.timeout || 120,
        enable_parallel: options.enable_parallel !== false,
        skip_failed_models: options.skip_failed_models !== false,
      },
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail?.message || error.detail || 'Request failed');
  }

  return response.json();
}

/**
 * Check health status of all models
 * @returns {Promise<object>} - Health status
 */
export async function checkHealth() {
  const response = await fetch(`${API_URL}/api/health`);

  if (!response.ok) {
    throw new Error('Health check failed');
  }

  return response.json();
}

/**
 * Get pipeline statistics
 * @returns {Promise<object>} - Statistics
 */
export async function getStatistics() {
  const response = await fetch(`${API_URL}/api/stats`);

  if (!response.ok) {
    throw new Error('Failed to fetch statistics');
  }

  return response.json();
}

/**
 * Clear the response cache
 * @returns {Promise<object>} - Success message
 */
export async function clearCache() {
  const response = await fetch(`${API_URL}/api/cache/clear`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Failed to clear cache');
  }

  return response.json();
}
