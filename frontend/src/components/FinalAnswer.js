import React from 'react';
import { formatConfidence } from '../utils/formatting';
import './FinalAnswer.css';

function FinalAnswer({ data, metadata }) {
  return (
    <div className="final-answer-container">
      {/* Main Answer */}
      <div className="main-answer">
        <div className="confidence-bar-container">
          <div
            className="confidence-bar"
            style={{ width: `${data.confidence * 100}%` }}
          ></div>
        </div>
        <div className="confidence-label">
          Confidence: {formatConfidence(data.confidence)}
        </div>
        <p className="answer-text">{data.final_answer}</p>
      </div>

      {/* Supporting Claims */}
      {data.supporting_claims && data.supporting_claims.length > 0 && (
        <div className="claims-section supporting">
          <h4>✅ Supporting Claims</h4>
          <ul className="claims-list">
            {data.supporting_claims.map((claim, idx) => (
              <li key={idx}>{claim}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Uncertain Points */}
      {data.uncertain_points && data.uncertain_points.length > 0 && (
        <div className="claims-section uncertain">
          <h4>❓ Uncertain Points</h4>
          <ul className="claims-list">
            {data.uncertain_points.map((point, idx) => (
              <li key={idx}>{point}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Rejected Claims */}
      {data.rejected_claims && data.rejected_claims.length > 0 && (
        <div className="claims-section rejected">
          <h4>❌ Rejected Claims</h4>
          <ul className="claims-list">
            {data.rejected_claims.map((claim, idx) => (
              <li key={idx}>{claim}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Citations */}
      {data.citations && data.citations.length > 0 && (
        <div className="citations-section">
          <h4>📚 Citations</h4>
          <div className="citations-list">
            {data.citations.map((citation, idx) => (
              <div key={idx} className="citation-card">
                {citation.source && <strong>{citation.source}</strong>}
                {citation.url && (
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="citation-url"
                  >
                    {citation.url}
                  </a>
                )}
                {citation.snippet && (
                  <p className="citation-snippet">{citation.snippet}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reasoning Summary */}
      {data.reasoning_summary && (
        <div className="reasoning-section">
          <h4>🧠 Reasoning Summary</h4>
          <p className="reasoning-text">{data.reasoning_summary}</p>
        </div>
      )}
    </div>
  );
}

export default FinalAnswer;
