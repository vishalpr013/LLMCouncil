import React from 'react';
import { getVerdictColor, getVerdictEmoji, getConsensusDescription } from '../utils/formatting';
import './ReviewerPanel.css';

function ReviewerPanel({ verdicts, aggregation }) {
  if (!verdicts || verdicts.length === 0) {
    return <p>No reviews available.</p>;
  }

  const consensusInfo = getConsensusDescription(aggregation.consensus_score);

  return (
    <div className="reviewer-panel">
      {/* Aggregation Summary */}
      <div className="aggregation-summary">
        <h4>Review Summary</h4>
        <div className="summary-grid">
          <div className="summary-item supported">
            <span className="summary-icon">✅</span>
            <div>
              <div className="summary-label">Supported</div>
              <div className="summary-value">{aggregation.supported_claims.length}</div>
            </div>
          </div>
          <div className="summary-item rejected">
            <span className="summary-icon">❌</span>
            <div>
              <div className="summary-label">Rejected</div>
              <div className="summary-value">{aggregation.rejected_claims.length}</div>
            </div>
          </div>
          <div className="summary-item uncertain">
            <span className="summary-icon">❓</span>
            <div>
              <div className="summary-label">Uncertain</div>
              <div className="summary-value">{aggregation.uncertain_claims.length}</div>
            </div>
          </div>
          <div className="summary-item disputed">
            <span className="summary-icon">⚠️</span>
            <div>
              <div className="summary-label">Disputed</div>
              <div className="summary-value">{aggregation.disputed_claims.length}</div>
            </div>
          </div>
        </div>

        <div className="consensus-badge" style={{ background: consensusInfo.color }}>
          {consensusInfo.text}: {(aggregation.consensus_score * 100).toFixed(0)}%
        </div>
      </div>

      {/* Individual Reviewers */}
      <div className="reviewers-section">
        {verdicts.map((verdict, idx) => (
          <div key={idx} className="reviewer-card">
            <h4 className="reviewer-name">{verdict.reviewer_name}</h4>
            <p className="reviewer-stats">
              Reviewed {verdict.reviews.length} claims
            </p>

            <div className="reviews-list">
              {verdict.reviews.map((review, reviewIdx) => (
                <div key={reviewIdx} className="review-item">
                  <div className="review-header">
                    <span
                      className="verdict-badge"
                      style={{ background: getVerdictColor(review.verdict) }}
                    >
                      {getVerdictEmoji(review.verdict)} {review.verdict}
                    </span>
                    <span className="confidence-badge">
                      {(review.confidence * 100).toFixed(0)}% confident
                    </span>
                  </div>
                  <p className="claim-id-ref">{review.claim_id}</p>
                  <p className="review-reason">{review.reason}</p>
                  {review.evidence_needed && (
                    <span className="evidence-badge">🔍 Evidence Needed</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ReviewerPanel;
