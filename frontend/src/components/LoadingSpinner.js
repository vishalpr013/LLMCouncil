import React from 'react';
import './LoadingSpinner.css';

function LoadingSpinner() {
  return (
    <div className="spinner-container">
      <div className="spinner">
        <div className="double-bounce1"></div>
        <div className="double-bounce2"></div>
      </div>
      <div className="stage-indicators">
        <div className="stage-indicator">Stage 1: First Opinions</div>
        <div className="stage-indicator">Stage 2: Claim Extraction</div>
        <div className="stage-indicator">Stage 3: Peer Review</div>
        <div className="stage-indicator">Stage 4: Aggregation</div>
        <div className="stage-indicator">Stage 5: Final Synthesis</div>
      </div>
    </div>
  );
}

export default LoadingSpinner;
