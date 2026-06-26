import React, { useState } from 'react';
import './App.css';
import UploadScreen from './components/UploadScreen';
import ScoreScreen from './components/ScoreScreen';
import TailorScreen from './components/TailorScreen';

// Screen names for the flow
const SCREENS = {
  LANDING: 'landing',
  UPLOAD: 'upload',
  SCORE: 'score',
  TAILOR: 'tailor',
};

function App() {
  const [screen, setScreen] = useState(SCREENS.LANDING);
  const [documentIds, setDocumentIds] = useState({
    resumeDocumentId: null,
    jdDocumentId: null,
  });

  const handleUploadComplete = ({ resumeDocumentId, jdDocumentId }) => {
    setDocumentIds({ resumeDocumentId, jdDocumentId });
    setScreen(SCREENS.SCORE);
  };

  const handleScoreContinue = ({ resumeDocumentId, jdDocumentId }) => {
    setDocumentIds({ resumeDocumentId, jdDocumentId });
    setScreen(SCREENS.TAILOR);
  };

  if (screen === SCREENS.UPLOAD) {
    return (
      <div className="app-container" style={{ alignItems: 'flex-start', paddingTop: '4rem' }}>
        <div className="glow"></div>
        <div className="content" style={{ width: '100%' }}>
          <UploadScreen onComplete={handleUploadComplete} />
        </div>
      </div>
    );
  }

  if (screen === SCREENS.SCORE) {
    return (
      <div className="app-container" style={{ alignItems: 'flex-start', paddingTop: '4rem' }}>
        <div className="glow"></div>
        <div className="content" style={{ width: '100%' }}>
          <ScoreScreen
            resumeDocumentId={documentIds.resumeDocumentId}
            jdDocumentId={documentIds.jdDocumentId}
            onContinue={handleScoreContinue}
          />
        </div>
      </div>
    );
  }

  if (screen === SCREENS.TAILOR) {
    return (
      <div className="app-container" style={{ alignItems: 'flex-start', paddingTop: '4rem' }}>
        <div className="glow"></div>
        <div className="content" style={{ width: '100%' }}>
          <TailorScreen
            resumeDocumentId={documentIds.resumeDocumentId}
            jdDocumentId={documentIds.jdDocumentId}
          />
        </div>
      </div>
    );
  }

  // LANDING
  return (
    <div className="app-container">
      <div className="glow"></div>

      <div className="content">
        <div className="badge">✨ AlignAI Frontend Scaffolded</div>

        <h1 className="title">
          Build the future of <br />
          <span>Alignment</span>
        </h1>

        <p className="subtitle">
          Your React + Vite application is successfully set up and ready for development.
          Start building powerful, aligned AI interfaces with premium aesthetics.
        </p>

        <button className="cta-button" onClick={() => setScreen(SCREENS.UPLOAD)}>
          Start Flow
        </button>

        <div className="features">
          <div className="feature-card">
            <div className="feature-icon">⚡️</div>
            <h3 className="feature-title">Lightning Fast</h3>
            <p className="feature-desc">Powered by Vite for instant server start and lightning fast HMR.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚛️</div>
            <h3 className="feature-title">React Ecosystem</h3>
            <p className="feature-desc">Built on React for maximum composability and state management.</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎨</div>
            <h3 className="feature-title">Premium Design</h3>
            <p className="feature-desc">Pre-configured with a modern, glassmorphism aesthetic.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
