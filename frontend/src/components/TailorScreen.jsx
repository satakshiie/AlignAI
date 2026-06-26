import React, { useState, useEffect, useRef } from 'react';

// ── Mode constants ─────────────────────────────────────────────────────────────
const MODE = {
  LOADING: 'loading',
  REVIEW: 'review',
  SUBMITTING_REVIEW: 'submitting_review',
  RESULTS: 'results',
  ERROR: 'error',
};

// ── FinalResults sub-component ─────────────────────────────────────────────────
// Shared between Shape A (direct) and Shape B (post-review-submit) rendering.
function FinalResults({ data }) {
  const { summary, bullet_rewrites, learning_roadmap } = data;
  const changedBullets = bullet_rewrites?.filter((b) => b.changed) ?? [];

  return (
    <div>
      {/* Summary */}
      <div>
        <h3>Summary</h3>
        <p>{summary}</p>
      </div>

      {/* Bullet rewrites — only show items that actually changed */}
      {changedBullets.length > 0 && (
        <div>
          <h3>Suggested Bullet Rewrites</h3>
          {changedBullets.map((bullet, i) => (
            <div key={i} style={{ marginBottom: '16px', borderLeft: '3px solid #ccc', paddingLeft: '10px' }}>
              <p><strong>Original:</strong> {bullet.original}</p>
              <p><strong>Rewritten:</strong> {bullet.rewritten}</p>
            </div>
          ))}
        </div>
      )}

      {/* Learning roadmap */}
      {learning_roadmap?.length > 0 && (
        <div>
          <h3>Learning Roadmap</h3>
          {learning_roadmap.map((item, i) => (
            <div key={i} style={{ marginBottom: '16px', borderLeft: '3px solid #ccc', paddingLeft: '10px' }}>
              <p>
                <strong>{item.skill}</strong>{' '}
                <span>— Priority: {item.priority}</span>
              </p>
              <p><em>Approach:</em> {item.suggested_approach}</p>
              <p><em>Estimated timeframe:</em> {item.estimated_timeframe}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function TailorScreen({ resumeDocumentId, jdDocumentId }) {
  const [mode, setMode] = useState(MODE.LOADING);
  const hasStarted = useRef(false);
  const [errorMessage, setErrorMessage] = useState(null);

  // Holds the full /tailor/start response so we can extract thread_id later
  const [startResponse, setStartResponse] = useState(null);

  // Holds the final results data (Shape A body, or /tailor/resume response)
  const [resultsData, setResultsData] = useState(null);

  // Per-item decisions during review: { [key]: "approved" | "rejected" }
  // key is bullet.original for bullets, gap.skill for gaps
  const [decisions, setDecisions] = useState({});

  // ── Fetch on mount ───────────────────────────────────────────────────────────
  useEffect(() => {
    const startTailoring = async () => {
      setMode(MODE.LOADING);
      setErrorMessage(null);

      try {
        const response = await fetch('http://localhost:8000/api/tailor/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            resume_document_id: resumeDocumentId,
            jd_document_id: jdDocumentId,
          }),
        });

        if (!response.ok) {
          // 429 gets its own user-facing message
          if (response.status === 429) {
            setErrorMessage("You've used your free tailoring run for today. Try again tomorrow.");
            setMode(MODE.ERROR);
            return;
          }
          let errorMessage = 'An unknown error occurred';
          try {
            const errJson = await response.json();
            errorMessage = errJson.detail || errorMessage;
          } catch (e) {
            errorMessage = response.statusText;
          }
          throw new Error(errorMessage);
        }

        const data = await response.json();
        setStartResponse(data);

        if (data.status === 'completed') {
          setResultsData(data);
          setMode(MODE.RESULTS);
        } else if (data.status === 'needs_review') {
          // Pre-populate decisions as empty so the UI knows which items exist
          const initialDecisions = {};
          data.flagged_bullets?.forEach((b) => { initialDecisions[b.original] = null; });
          data.flagged_gaps?.forEach((g) => { initialDecisions[g.skill] = null; });
          setDecisions(initialDecisions);
          setMode(MODE.REVIEW);
        } else {
          throw new Error(`Unexpected status from server: "${data.status}"`);
        }
      } catch (err) {
        setErrorMessage(err.message);
        setMode(MODE.ERROR);
      }
    };

    if (hasStarted.current) return;
    hasStarted.current = true;

    startTailoring();
  }, [resumeDocumentId, jdDocumentId]);

  // ── Decision helpers ─────────────────────────────────────────────────────────
  const setDecision = (key, value) => {
    setDecisions((prev) => ({ ...prev, [key]: value }));
  };

  // All flagged items must have a decision before submitting
  const allDecided = Object.values(decisions).every((v) => v !== null);

  // ── Submit review ────────────────────────────────────────────────────────────
  const handleSubmitReview = async () => {
    setMode(MODE.SUBMITTING_REVIEW);
    setErrorMessage(null);

    try {
      const response = await fetch('http://localhost:8000/api/tailor/resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: startResponse.thread_id,
          decisions,
        }),
      });

      if (!response.ok) {
        if (response.status === 429) {
          setErrorMessage("You've used your free tailoring run for today. Try again tomorrow.");
          setMode(MODE.ERROR);
          return;
        }
        let errorMessage = 'An unknown error occurred';
        try {
          const errJson = await response.json();
          errorMessage = errJson.detail || errorMessage;
        } catch (e) {
          errorMessage = response.statusText;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setResultsData(data);
      setMode(MODE.RESULTS);
    } catch (err) {
      setErrorMessage(err.message);
      setMode(MODE.ERROR);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────────
  if (mode === MODE.LOADING) {
    return <p>Analyzing your resume against this job… this may take a moment.</p>;
  }

  if (mode === MODE.SUBMITTING_REVIEW) {
    return <p>Applying your decisions and generating final suggestions…</p>;
  }

  if (mode === MODE.ERROR) {
    return <p>Error: {errorMessage}</p>;
  }

  if (mode === MODE.RESULTS) {
    return (
      <div>
        <h2>Tailoring Results</h2>
        <FinalResults data={resultsData} />
      </div>
    );
  }

  // ── REVIEW mode ──────────────────────────────────────────────────────────────
  const { flagged_bullets = [], flagged_gaps = [] } = startResponse ?? {};

  return (
    <div>
      <h2>Review Flagged Items</h2>
      <p>
        Our critic flagged the items below. Review each one and approve or reject
        before we generate your final suggestions.
      </p>

      {/* Flagged bullet rewrites */}
      {flagged_bullets.length > 0 && (
        <div>
          <h3>Flagged Bullet Rewrites</h3>
          {flagged_bullets.map((bullet, i) => {
            const key = bullet.original;
            const decision = decisions[key];
            return (
              <div
                key={i}
                style={{ marginBottom: '20px', borderLeft: '3px solid #ccc', paddingLeft: '10px' }}
              >
                <p><strong>Original:</strong> {bullet.original}</p>
                <p><strong>Rewritten:</strong> {bullet.rewritten}</p>
                <p><em>Critic notes:</em> {bullet.critic_notes}</p>
                <div>
                  <button
                    onClick={() => setDecision(key, 'approved')}
                    disabled={decision === 'approved'}
                  >
                    {decision === 'approved' ? '✓ Approved' : 'Approve'}
                  </button>{' '}
                  <button
                    onClick={() => setDecision(key, 'rejected')}
                    disabled={decision === 'rejected'}
                  >
                    {decision === 'rejected' ? '✗ Rejected' : 'Reject'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Flagged gaps */}
      {flagged_gaps.length > 0 && (
        <div>
          <h3>Flagged Skill Gaps</h3>
          {flagged_gaps.map((gap, i) => {
            const key = gap.skill;
            const decision = decisions[key];
            return (
              <div
                key={i}
                style={{ marginBottom: '20px', borderLeft: '3px solid #ccc', paddingLeft: '10px' }}
              >
                <p><strong>Skill:</strong> {gap.skill}</p>
                <p><strong>Suggested action:</strong> {gap.suggested_action}</p>
                <p><em>Critic notes:</em> {gap.critic_notes}</p>
                <div>
                  <button
                    onClick={() => setDecision(key, 'approved')}
                    disabled={decision === 'approved'}
                  >
                    {decision === 'approved' ? '✓ Approved' : 'Approve'}
                  </button>{' '}
                  <button
                    onClick={() => setDecision(key, 'rejected')}
                    disabled={decision === 'rejected'}
                  >
                    {decision === 'rejected' ? '✗ Rejected' : 'Reject'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Submit */}
      <div style={{ marginTop: '24px' }}>
        <button onClick={handleSubmitReview} disabled={!allDecided}>
          Submit review
        </button>
        {!allDecided && (
          <p><em>Please approve or reject every item above before submitting.</em></p>
        )}
      </div>
    </div>
  );
}
