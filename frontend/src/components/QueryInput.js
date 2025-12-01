import React, { useState } from 'react';
import './QueryInput.css';

function QueryInput({ onSubmit, disabled }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query.trim());
    }
  };

  const exampleQueries = [
    "What causes climate change?",
    "How does photosynthesis work?",
    "Explain quantum computing in simple terms",
    "What are the health benefits of exercise?",
  ];

  const handleExampleClick = (example) => {
    setQuery(example);
  };

  return (
    <div className="query-input-container">
      <form onSubmit={handleSubmit} className="query-form">
        <div className="input-wrapper">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your question here..."
            className="query-input"
            disabled={disabled}
            maxLength={1000}
          />
          <button
            type="submit"
            className="submit-button"
            disabled={disabled || !query.trim()}
          >
            {disabled ? 'Processing...' : 'Ask Council'}
          </button>
        </div>
      </form>

      <div className="examples-section">
        <p className="examples-label">Try these examples:</p>
        <div className="examples-grid">
          {exampleQueries.map((example, idx) => (
            <button
              key={idx}
              className="example-button"
              onClick={() => handleExampleClick(example)}
              disabled={disabled}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default QueryInput;
