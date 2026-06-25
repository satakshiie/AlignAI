import React, { useState, useEffect } from 'react';

export default function ScoreScreen({ resumeDocumentId, jdDocumentId, onContinue }) {
  const [scoreData, setScoreData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchScore = async () => {
      setLoading(true);
      setError(null);

      try {
        const response = await fetch('http://localhost:8000/api/ats-score', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            resume_document_id: resumeDocumentId,
            jd_document_id: jdDocumentId,
          }),
        });

        if (!response.ok) {
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
        if (data.success) {
          setScoreData(data);
        } else {
          throw new Error('ATS scoring failed. Please try again.');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchScore();
  }, [resumeDocumentId, jdDocumentId]);

  const handleContinue = () => {
    if (onContinue) {
      onContinue({ resumeDocumentId, jdDocumentId });
    }
  };

  // ── Severity label helpers ──────────────────────────────────────────────────
  const severityLabel = (severity) => {
    const map = { high: '[HIGH]', medium: '[MEDIUM]', low: '[LOW]' };
    return map[severity] ?? `[${severity?.toUpperCase()}]`;
  };

  // ── Render ──────────────────────────────────────────────────────────────────
  if (loading) {
    return <p>Calculating your ATS score...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  const { final_score, layer_breakdown, skill_analysis, structural_analysis, content_similarity_detail, gaps } = scoreData;

  return (
    <div>
      <h2>ATS Score Results</h2>

      {/* ── Final score ─────────────────────────────────────────────────── */}
      <div>
        <h3>Overall Score</h3>
        <p style={{ fontSize: '3rem', fontWeight: 'bold', margin: 0 }}>
          {final_score}
          <span style={{ fontSize: '1.5rem' }}>/100</span>
        </p>
      </div>

      {/* ── Layer breakdown ──────────────────────────────────────────────── */}
      <div>
        <h3>Score Breakdown</h3>
        <ul>
          <li>
            <strong>Skill Match:</strong> {layer_breakdown.skill_match.score}{' '}
            (weight: {layer_breakdown.skill_match.weight})
          </li>
          <li>
            <strong>Section Coverage:</strong> {layer_breakdown.section_coverage.score}{' '}
            (weight: {layer_breakdown.section_coverage.weight})
          </li>
          <li>
            <strong>Content Similarity:</strong>{' '}
            {layer_breakdown.content_similarity.score.toFixed(1)}{' '}
            (weight: {layer_breakdown.content_similarity.weight})
          </li>
        </ul>
      </div>

      {/* ── Skill analysis ───────────────────────────────────────────────── */}
      <div>
        <h3>Skill Analysis</h3>

        {skill_analysis.matched_required.length > 0 && (
          <div>
            <h4>Matched Required Skills</h4>
            <ul>
              {skill_analysis.matched_required.map((skill, i) => (
                <li key={i}>{skill}</li>
              ))}
            </ul>
          </div>
        )}

        {skill_analysis.missing_required.length > 0 && (
          <div>
            <h4>Missing Required Skills</h4>
            <ul>
              {skill_analysis.missing_required.map((skill, i) => (
                <li key={i}>{skill}</li>
              ))}
            </ul>
          </div>
        )}

        {skill_analysis.matched_preferred.length > 0 && (
          <div>
            <h4>Matched Preferred Skills</h4>
            <ul>
              {skill_analysis.matched_preferred.map((skill, i) => (
                <li key={i}>{skill}</li>
              ))}
            </ul>
          </div>
        )}

        {skill_analysis.missing_preferred.length > 0 && (
          <div>
            <h4>Missing Preferred Skills</h4>
            <ul>
              {skill_analysis.missing_preferred.map((skill, i) => (
                <li key={i}>{skill}</li>
              ))}
            </ul>
          </div>
        )}

        {skill_analysis.bonus_skills.length > 0 && (
          <div>
            <h4>Bonus Skills (not in JD but worth keeping)</h4>
            <ul>
              {skill_analysis.bonus_skills.map((skill, i) => (
                <li key={i}>{skill}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* ── Structural analysis ──────────────────────────────────────────── */}
      <div>
        <h3>Structural Analysis</h3>
        <ul>
          <li>Experience section present: {structural_analysis.has_experience_section ? 'Yes' : 'No'}</li>
          <li>
            Years of experience — Required:{' '}
            {structural_analysis.years_required !== null ? structural_analysis.years_required : 'Not specified'},{' '}
            Detected: {structural_analysis.years_detected}
            {structural_analysis.years_gap && ' ⚠ Gap detected'}
          </li>
          <li>Education section present: {structural_analysis.has_education ? 'Yes' : 'No'}</li>
          <li>JD requires a degree: {structural_analysis.jd_requires_degree ? 'Yes' : 'No'}</li>
          <li>Certifications present: {structural_analysis.has_certifications ? 'Yes' : 'No'}</li>
          <li>JD emphasises certifications: {structural_analysis.jd_emphasizes_certifications ? 'Yes' : 'No'}</li>
          <li>Projects section present: {structural_analysis.has_projects ? 'Yes' : 'No'}</li>
          <li>Skills section present: {structural_analysis.has_skills_section ? 'Yes' : 'No'}</li>
          <li>JD requires leadership: {structural_analysis.jd_requires_leadership ? 'Yes' : 'No'}</li>
          <li>Resume shows leadership: {structural_analysis.resume_shows_leadership ? 'Yes' : 'No'}</li>
        </ul>
      </div>

      {/* ── Content similarity detail ────────────────────────────────────── */}
      <div>
        <h3>Content Similarity Detail</h3>
        <ul>
          <li>
            Experience vs Responsibilities:{' '}
            {content_similarity_detail.experience_vs_responsibilities.toFixed(1)}
          </li>
          <li>
            Projects vs Responsibilities:{' '}
            {content_similarity_detail.projects_vs_responsibilities.toFixed(1)}
          </li>
          <li>
            Overall Document Similarity:{' '}
            {content_similarity_detail.overall_document_similarity.toFixed(1)}
          </li>
        </ul>
      </div>

      {/* ── Gaps ─────────────────────────────────────────────────────────── */}
      {gaps && gaps.length > 0 && (
        <div>
          <h3>Identified Gaps</h3>
          {/* Rendered in the order given — backend already sorts by severity */}
          {gaps.map((gap, i) => (
            <div key={i} style={{ marginBottom: '16px', borderLeft: '3px solid #ccc', paddingLeft: '10px' }}>
              <p style={{ margin: '0 0 4px 0' }}>
                <strong>{gap.type.replace(/_/g, ' ')}</strong>{' '}
                <span>{severityLabel(gap.severity)}</span>
              </p>
              {gap.items && gap.items.length > 0 && (
                <ul style={{ margin: '4px 0' }}>
                  {gap.items.map((item, j) => (
                    <li key={j}>{item}</li>
                  ))}
                </ul>
              )}
              <p style={{ margin: '4px 0 0 0', fontStyle: 'italic' }}>{gap.suggestion}</p>
            </div>
          ))}
        </div>
      )}

      {/* ── Continue button ──────────────────────────────────────────────── */}
      <div style={{ marginTop: '24px' }}>
        <button onClick={handleContinue}>
          Generate tailored suggestions
        </button>
      </div>
    </div>
  );
}
