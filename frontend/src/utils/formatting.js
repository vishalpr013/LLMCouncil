/**
 * Utility functions for formatting and displaying data
 */

/**
 * Format duration in seconds to human-readable string
 * @param {number} seconds - Duration in seconds
 * @returns {string} - Formatted duration
 */
export function formatDuration(seconds) {
  if (seconds < 1) {
    return `${(seconds * 1000).toFixed(0)}ms`;
  }
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = (seconds % 60).toFixed(0);
  return `${minutes}m ${remainingSeconds}s`;
}

/**
 * Format confidence score as percentage
 * @param {number} confidence - Confidence (0.0-1.0)
 * @returns {string} - Formatted percentage
 */
export function formatConfidence(confidence) {
  return `${(confidence * 100).toFixed(0)}%`;
}

/**
 * Get color for verdict type
 * @param {string} verdict - Verdict type
 * @returns {string} - CSS color
 */
export function getVerdictColor(verdict) {
  const colors = {
    CORRECT: '#28a745',
    INCORRECT: '#dc3545',
    UNCERTAIN: '#ffc107',
  };
  return colors[verdict] || '#6c757d';
}

/**
 * Get emoji for verdict type
 * @param {string} verdict - Verdict type
 * @returns {string} - Emoji
 */
export function getVerdictEmoji(verdict) {
  const emojis = {
    CORRECT: '✅',
    INCORRECT: '❌',
    UNCERTAIN: '❓',
  };
  return emojis[verdict] || '⚪';
}

/**
 * Truncate text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated text
 */
export function truncate(text, maxLength = 100) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Highlight text matching a search query
 * @param {string} text - Text to highlight
 * @param {string} query - Search query
 * @returns {string} - HTML with highlights
 */
export function highlightText(text, query) {
  if (!query) return text;
  const regex = new RegExp(`(${query})`, 'gi');
  return text.replace(regex, '<mark>$1</mark>');
}

/**
 * Format timestamp to readable date/time
 * @param {string} timestamp - ISO timestamp
 * @returns {string} - Formatted date/time
 */
export function formatTimestamp(timestamp) {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleString();
}

/**
 * Calculate consensus description
 * @param {number} score - Consensus score (0.0-1.0)
 * @returns {object} - Description and color
 */
export function getConsensusDescription(score) {
  if (score >= 0.9) {
    return { text: 'Strong Consensus', color: '#28a745' };
  }
  if (score >= 0.7) {
    return { text: 'Good Consensus', color: '#5cb85c' };
  }
  if (score >= 0.5) {
    return { text: 'Moderate Consensus', color: '#ffc107' };
  }
  if (score >= 0.3) {
    return { text: 'Weak Consensus', color: '#ff9800' };
  }
  return { text: 'No Consensus', color: '#dc3545' };
}
