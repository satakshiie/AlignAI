import React, { useState, useRef } from 'react';
import './UploadScreen.css';

// ── Sidebar nav items (content TBD) ───────────────────────────────────────────
const NAV_ITEMS = [
  { icon: UploadIcon,   label: 'Upload',    active: true  },
  { icon: ScoreIcon,    label: 'ATS Score', active: false, badge: 'next' },
  { icon: TailorIcon,   label: 'Tailor',    active: false, badge: 'next' },
  { icon: HistoryIcon,  label: 'History',   active: false, badge: 'soon' },
  { icon: SettingsIcon, label: 'Settings',  active: false, badge: 'soon' },
];

// ── Inline SVG icons (no external dep needed) ─────────────────────────────────
function UploadIcon()   { return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>; }
function ScoreIcon()    { return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>; }
function TailorIcon()   { return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>; }
function HistoryIcon()  { return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="12 8 12 12 14 14"/><path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5"/></svg>; }
function SettingsIcon() { return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>; }
function FileIcon()     { return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>; }
function CloudUpIcon()  { return <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>; }
function CheckIcon()    { return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>; }
function AlertIcon()    { return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>; }
function SpinnerIcon()  { return <svg className="spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><circle cx="12" cy="12" r="10" strokeOpacity="0.25"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor"/></svg>; }
function ArrowIcon()    { return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>; }
function MenuIcon()     { return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>; }
function CloseIcon()    { return <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>; }

// ── Single upload card ─────────────────────────────────────────────────────────
function UploadCard({ title, subtitle, acceptStr, docType, data, loading, error, onFileChange }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const status = loading ? 'uploading'
    : error   ? 'error'
    : data    ? 'success'
    : 'idle';

  const badgeLabel = { idle: 'Waiting', uploading: 'Uploading…', success: 'Ready', error: 'Error' }[status];

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (!file) return;
    // Synthesise a fake event so existing handleUpload works unchanged
    onFileChange({ target: { files: [file] } });
  };

  return (
    <div className={`upload-card upload-card--${status}`}>
      {/* Header */}
      <div className="upload-card__header">
        <div className="upload-card__title-group">
          <div className="upload-card__type-icon">
            <FileIcon />
          </div>
          <div>
            <div className="upload-card__title">{title}</div>
            <div className="upload-card__subtitle">{subtitle}</div>
          </div>
        </div>
        <span className={`upload-card__status-badge upload-card__status-badge--${status}`}>
          {loading && <SpinnerIcon />}{' '}
          {badgeLabel}
        </span>
      </div>

      {/* Drop zone — always visible unless we have a result to show */}
      {!data && (
        <div
          className={`upload-card__dropzone${dragging ? ' upload-card__dropzone--dragging' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          role="button"
          tabIndex={0}
          aria-label={`Upload ${title}`}
          onKeyDown={(e) => e.key === 'Enter' && inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            accept={acceptStr}
            onChange={onFileChange}
            className="upload-card__input"
            aria-label={`Select ${title} file`}
            onClick={(e) => e.stopPropagation()}
          />

          <div className="upload-card__dropzone-icon">
            {loading ? <SpinnerIcon /> : <CloudUpIcon />}
          </div>

          <div className="upload-card__dropzone-title">
            {loading ? 'Uploading…' : 'Drop file here'}
          </div>
          <div className="upload-card__dropzone-sub">
            {loading
              ? 'Processing your document'
              : `Accepts ${acceptStr.replace(/\./g, '').toUpperCase()} · click to browse`}
          </div>

          {!loading && (
            <button
              className="upload-card__browse-btn"
              type="button"
              tabIndex={-1}
              aria-hidden="true"
            >
              Browse files
            </button>
          )}
        </div>
      )}

      {/* Success result */}
      {data && (
        <div className="upload-card__result">
          <div className="upload-card__result-row">
            <div className="upload-card__result-icon"><FileIcon /></div>
            <div className="upload-card__result-info">
              <div className="upload-card__result-name">{data.filename}</div>
              <div className="upload-card__result-meta">
                {data.mime_type} · {data.size_mb?.toFixed(2)} MB · {data.extraction_method}
              </div>
            </div>
            <div className="upload-card__result-check"><CheckIcon /></div>
          </div>
          <div className="upload-card__progress">
            <div className="upload-card__progress-fill upload-card__progress-fill--success" />
          </div>
          {/* Allow re-upload */}
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              className="upload-card__browse-btn"
              type="button"
              onClick={() => inputRef.current?.click()}
              style={{ fontSize: '0.72rem', padding: '0.3rem 0.8rem' }}
            >
              Replace file
            </button>
            <input
              ref={inputRef}
              type="file"
              accept={acceptStr}
              onChange={onFileChange}
              style={{ display: 'none' }}
              aria-label={`Replace ${title} file`}
            />
          </div>
        </div>
      )}

      {/* Loading progress strip */}
      {loading && (
        <div className="upload-card__result">
          <div className="upload-card__progress">
            <div className="upload-card__progress-fill upload-card__progress-fill--loading" />
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="upload-card__error">
          <span className="upload-card__error-icon"><AlertIcon /></span>
          {error}
        </div>
      )}
    </div>
  );
}

// ── Main UploadScreen ──────────────────────────────────────────────────────────
export default function UploadScreen({ onComplete }) {
  const [resumeData,    setResumeData]    = useState(null);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [resumeError,   setResumeError]   = useState(null);

  const [jdData,    setJdData]    = useState(null);
  const [jdLoading, setJdLoading] = useState(false);
  const [jdError,   setJdError]   = useState(null);

  const [sidebarOpen, setSidebarOpen] = useState(false);

  // ── Upload handler (logic unchanged from original) ───────────────────────────
  const handleUpload = async (event, docType) => {
    const file = event.target.files[0];
    if (!file) return;

    const isResume  = docType === 'resume';
    const setLoading = isResume ? setResumeLoading : setJdLoading;
    const setError   = isResume ? setResumeError   : setJdError;
    const setData    = isResume ? setResumeData     : setJdData;

    setLoading(true);
    setError(null);
    setData(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('doc_type', docType);

    try {
      const response = await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let msg = 'An unknown error occurred';
        try { const j = await response.json(); msg = j.detail || msg; } catch {}
        throw new Error(msg);
      }

      const data = await response.json();
      if (data.success) {
        if (data.doc_type && data.doc_type !== docType) {
          const expected = docType === 'resume' ? 'Resume' : 'Job Description';
          const detected = data.doc_type === 'resume' ? 'Resume' : 'Job Description';
          throw new Error(`Wrong document: you uploaded a ${detected} in the ${expected} slot.`);
        }
        setData(data);
      } else {
        throw new Error(data.message || 'Upload failed');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleContinue = () => {
    // NOTE: /api/upload response does not include an explicit document_id field
    // in the original spec — we read it from data.document_id (added by backend).
    // If undefined, the ATS/tailor screens will fail. Ensure backend returns it.
    if (onComplete) {
      onComplete({
        resumeData,
        jdData,
        resumeDocumentId: resumeData?.document_id,
        jdDocumentId:     jdData?.document_id,
      });
    }
  };

  const bothReady = resumeData?.success && jdData?.success;
  const readyCount = (resumeData?.success ? 1 : 0) + (jdData?.success ? 1 : 0);

  return (
    <div className="dashboard">

      {/* ══ Sidebar ════════════════════════════════════════════════════════════ */}
      <aside className={`sidebar${sidebarOpen ? ' sidebar--open' : ''}`} aria-label="Navigation">
        <div className="sidebar__brand">
          <div className="sidebar__brand-dot" aria-hidden="true" />
          <span className="sidebar__brand-name">AlignAI</span>
        </div>

        <span className="sidebar__section-label">Workspace</span>

        <nav className="sidebar__nav" role="navigation">
          {NAV_ITEMS.map(({ icon: Icon, label, active, badge }) => (
            <button
              key={label}
              className={`sidebar__nav-item${active ? ' sidebar__nav-item--active' : ''}`}
              aria-current={active ? 'page' : undefined}
            >
              <span className="sidebar__nav-icon"><Icon /></span>
              {label}
              {badge && (
                <span className="sidebar__nav-badge">{badge}</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar__footer">
          <div className="sidebar__status">
            <div className="sidebar__status-dot" />
            Backend connected
          </div>
          <div className="sidebar__status" style={{ color: '#37455E', fontSize: '0.65rem' }}>
            localhost:8000
          </div>
        </div>
      </aside>

      {/* Overlay for mobile */}
      <div
        className={`sidebar-overlay${sidebarOpen ? '' : ' sidebar-overlay--hidden'}`}
        onClick={() => setSidebarOpen(false)}
        aria-hidden="true"
      />

      {/* ══ Main ═══════════════════════════════════════════════════════════════ */}
      <div className="dashboard__main">

        {/* Top bar */}
        <header className="topbar">
          <button
            className="topbar__hamburger"
            onClick={() => setSidebarOpen(o => !o)}
            aria-label={sidebarOpen ? 'Close menu' : 'Open menu'}
          >
            {sidebarOpen ? <CloseIcon /> : <MenuIcon />}
          </button>

          <div className="topbar__left">
            <div className="topbar__breadcrumb">
              <span>AlignAI</span>
              <span className="topbar__breadcrumb-sep">›</span>
              <span style={{ color: '#DFDFE0' }}>Upload</span>
            </div>
            <div className="topbar__title">Document Upload</div>
          </div>

          <div className="topbar__right">
            <div className="topbar__step-indicator" aria-label="Flow progress: step 1 of 3">
              <div className="topbar__step-dot topbar__step-dot--active" title="Upload" />
              <div className="topbar__step-dot" title="ATS Score" />
              <div className="topbar__step-dot" title="Tailor" />
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="dashboard__content">

          <div className="upload__header">
            <div className="upload__header-tag">
              <span className="upload__header-tag-line" aria-hidden="true" />
              Step 1 of 3
            </div>
            <h1 className="upload__header-title">Upload your documents</h1>
            <p className="upload__header-sub">
              Upload your resume and the job description you're targeting.
              Both are analysed locally — nothing is stored without your consent.
            </p>
          </div>

          {/* Upload cards */}
          <div className="upload__grid">
            <UploadCard
              title="Resume"
              subtitle="Your CV or résumé"
              acceptStr=".pdf,.doc,.docx"
              docType="resume"
              data={resumeData}
              loading={resumeLoading}
              error={resumeError}
              onFileChange={(e) => handleUpload(e, 'resume')}
            />
            <UploadCard
              title="Job Description"
              subtitle="The role you're applying for"
              acceptStr=".pdf"
              docType="jd"
              data={jdData}
              loading={jdLoading}
              error={jdError}
              onFileChange={(e) => handleUpload(e, 'jd')}
            />
          </div>

          {/* Footer action bar */}
          <div className="upload__footer">
            <div className="upload__footer-status">
              <div className={`upload__footer-status-dot upload__footer-status-dot--${bothReady ? 'ready' : 'waiting'}`} />
              {bothReady
                ? 'Both documents ready — you can continue'
                : `${readyCount} of 2 documents uploaded`}
            </div>
            <button
              id="continue-btn"
              className="upload__continue-btn"
              onClick={handleContinue}
              disabled={!bothReady}
              aria-label="Continue to ATS scoring"
            >
              Continue to ATS Score
              <ArrowIcon />
            </button>
          </div>

        </main>
      </div>
    </div>
  );
}
