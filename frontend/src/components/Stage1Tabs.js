import React, { useState } from 'react';
import './Stage1Tabs.css';

function Stage1Tabs({ opinions }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!opinions || opinions.length === 0) {
    return <p>No opinions available.</p>;
  }

  const activeOpinion = opinions[activeTab];

  return (
    <div className="stage1-tabs">
      <div className="tabs-header">
        {opinions.map((opinion, idx) => (
          <button
            key={idx}
            className={`tab-button ${activeTab === idx ? 'active' : ''}`}
            onClick={() => setActiveTab(idx)}
          >
            {opinion.model_name}
          </button>
        ))}
      </div>

      <div className="tab-content">
        <div className="model-name-badge">{activeOpinion.model_name}</div>

        <div className="answer-section">
          <h4>Answer:</h4>
          <p className="answer-text">{activeOpinion.answer_text}</p>
        </div>

        {activeOpinion.claims && activeOpinion.claims.length > 0 && (
          <div className="claims-section">
            <h4>Claims:</h4>
            <ul className="claims-list">
              {activeOpinion.claims.map((claim, idx) => (
                <li key={idx}>{claim}</li>
              ))}
            </ul>
          </div>
        )}

        {activeOpinion.citations && activeOpinion.citations.length > 0 && (
          <div className="citations-section">
            <h4>Citations:</h4>
            <div className="citations-list">
              {activeOpinion.citations.map((citation, idx) => (
                <div key={idx} className="citation-item">
                  {citation.source && <strong>{citation.source}</strong>}
                  {citation.url && (
                    <a
                      href={citation.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="citation-link"
                    >
                      {citation.url}
                    </a>
                  )}
                  {citation.snippet && <p className="citation-snippet">{citation.snippet}</p>}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Stage1Tabs;
