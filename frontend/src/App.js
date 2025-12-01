import React, { useState } from 'react';
import './App.css';
import QueryInput from './components/QueryInput';
import Stage1Tabs from './components/Stage1Tabs';
import ClaimsPanel from './components/ClaimsPanel';
import ReviewerPanel from './components/ReviewerPanel';
import FinalAnswer from './components/FinalAnswer';
import LoadingSpinner from './components/LoadingSpinner';
import { submitQuery } from './services/api';

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [query, setQuery] = useState('');

  const handleSubmit = async (userQuery) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setQuery(userQuery);

    try {
      const response = await submitQuery(userQuery);
      setResult(response);
    } catch (err) {
      setError(err.message || 'An error occurred while processing your query.');
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎯 LLM Council</h1>
        <p className="subtitle">Multi-Model Debate Pipeline</p>
      </header>

      <main className="App-main">
        <QueryInput onSubmit={handleSubmit} disabled={loading} />

        {loading && (
          <div className="loading-container">
            <LoadingSpinner />
            <p className="loading-text">
              Running multi-stage pipeline... This may take 30-60 seconds.
            </p>
          </div>
        )}

        {error && (
          <div className="error-container">
            <h3>❌ Error</h3>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="results-container">
            {/* Final Answer - Most Important */}
            <section className="section final-section">
              <h2 className="section-title">📋 Final Answer</h2>
              <FinalAnswer data={result.final_answer} metadata={result.metadata} />
            </section>

            {/* Stage 1 Opinions */}
            <section className="section">
              <h2 className="section-title">💭 Stage 1: Initial Opinions</h2>
              <Stage1Tabs opinions={result.stage1_opinions} />
            </section>

            {/* Paraphrased Claims */}
            <section className="section">
              <h2 className="section-title">📝 Stage 2: Extracted Claims</h2>
              <ClaimsPanel claims={result.paraphrased_claims} />
            </section>

            {/* Reviewer Verdicts */}
            <section className="section">
              <h2 className="section-title">⚖️ Stage 3: Peer Review</h2>
              <ReviewerPanel 
                verdicts={result.reviewer_verdicts}
                aggregation={result.aggregation}
              />
            </section>

            {/* Metadata */}
            <section className="section metadata-section">
              <h3>📊 Pipeline Metadata</h3>
              <div className="metadata-grid">
                <div className="metadata-item">
                  <span className="label">Processing Time:</span>
                  <span className="value">{result.metadata.processing_time.toFixed(2)}s</span>
                </div>
                <div className="metadata-item">
                  <span className="label">Models Used:</span>
                  <span className="value">{result.metadata.models_used.join(', ')}</span>
                </div>
                <div className="metadata-item">
                  <span className="label">Cache Hit:</span>
                  <span className="value">{result.metadata.cache_hit ? 'Yes' : 'No'}</span>
                </div>
                <div className="metadata-item">
                  <span className="label">Request ID:</span>
                  <span className="value">{result.metadata.request_id}</span>
                </div>
              </div>
            </section>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>Built with ❤️ by the LLM Council Team</p>
      </footer>
    </div>
  );
}

export default App;
