import React, { useState } from 'react';
import './index.css';
import LandingPage from './components/LandingPage';
import UploadScreen from './components/UploadScreen';
import ScoreScreen from './components/ScoreScreen';
import TailorScreen from './components/TailorScreen';

// ── Screen state machine ───────────────────────────────────────────
const SCREENS = {
  LANDING: 'landing',
  UPLOAD:  'upload',
  SCORE:   'score',
  TAILOR:  'tailor',
};

export default function App() {
  const [screen, setScreen] = useState(SCREENS.LANDING);
  const [documentIds, setDocumentIds] = useState({
    resumeDocumentId: null,
    jdDocumentId:     null,
  });

  const handleUploadComplete = ({ resumeDocumentId, jdDocumentId }) => {
    setDocumentIds({ resumeDocumentId, jdDocumentId });
    setScreen(SCREENS.SCORE);
  };

  const handleScoreContinue = ({ resumeDocumentId, jdDocumentId }) => {
    setDocumentIds({ resumeDocumentId, jdDocumentId });
    setScreen(SCREENS.TAILOR);
  };

  if (screen === SCREENS.LANDING) {
    return <LandingPage onStart={() => setScreen(SCREENS.UPLOAD)} />;
  }

  if (screen === SCREENS.UPLOAD) {
    return <UploadScreen onComplete={handleUploadComplete} />;
  }

  if (screen === SCREENS.SCORE) {
    return (
      <div style={{ minHeight: '100vh', background: '#001233', padding: '5rem 2rem 2rem' }}>
        <ScoreScreen
          resumeDocumentId={documentIds.resumeDocumentId}
          jdDocumentId={documentIds.jdDocumentId}
          onContinue={handleScoreContinue}
        />
      </div>
    );
  }

  if (screen === SCREENS.TAILOR) {
    return (
      <div style={{ minHeight: '100vh', background: '#001233', padding: '5rem 2rem 2rem' }}>
        <TailorScreen
          resumeDocumentId={documentIds.resumeDocumentId}
          jdDocumentId={documentIds.jdDocumentId}
        />
      </div>
    );
  }

  return null;
}
