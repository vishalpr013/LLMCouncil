import React, { useState } from 'react';
import './ClaimsPanel.css';

function ClaimsPanel({ claims }) {
  const [groupByModel, setGroupByModel] = useState(true);

  if (!claims || claims.length === 0) {
    return <p>No claims extracted.</p>;
  }

  // Group claims by model
  const claimsByModel = claims.reduce((acc, claim) => {
    const model = claim.original_model;
    if (!acc[model]) {
      acc[model] = [];
    }
    acc[model].push(claim);
    return acc;
  }, {});

  return (
    <div className="claims-panel">
      <div className="claims-header">
        <div className="claims-stats">
          <span className="stat-item">
            Total Claims: <strong>{claims.length}</strong>
          </span>
          <span className="stat-item">
            From Models: <strong>{Object.keys(claimsByModel).length}</strong>
          </span>
        </div>
        <button
          className="toggle-button"
          onClick={() => setGroupByModel(!groupByModel)}
        >
          {groupByModel ? 'Show All' : 'Group by Model'}
        </button>
      </div>

      {groupByModel ? (
        <div className="grouped-claims">
          {Object.entries(claimsByModel).map(([model, modelClaims]) => (
            <div key={model} className="model-group">
              <h4 className="model-group-title">{model}</h4>
              <div className="claims-list">
                {modelClaims.map((claim) => (
                  <div key={claim.claim_id} className="claim-item">
                    <p className="claim-text">{claim.canonical_text}</p>
                    <div className="claim-meta">
                      <span className="claim-id">{claim.claim_id}</span>
                      <span className="word-count">{claim.word_count} words</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="claims-list">
          {claims.map((claim) => (
            <div key={claim.claim_id} className="claim-item">
              <p className="claim-text">{claim.canonical_text}</p>
              <div className="claim-meta">
                <span className="claim-model">from {claim.original_model}</span>
                <span className="claim-id">{claim.claim_id}</span>
                <span className="word-count">{claim.word_count} words</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ClaimsPanel;
