import React, { useState, useEffect, useRef } from 'react';
import './ScoreScreen.css';

/* ─── Icons ─────────────────────────────────────────────────────────────────── */
const I = {
  Upload:  () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>,
  Score:   () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>,
  Tailor:  () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>,
  History: () => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="12 8 12 12 14 14"/><path d="M3.05 11a9 9 0 1 1 .5 4m-.5 5v-5h5"/></svg>,
  Settings:() => <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>,
  Why:     () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
  Skills:  () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="8" r="6"/><path d="M15.477 12.89L17 22l-5-3-5 3 1.523-9.11"/></svg>,
  Structure:()=> <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>,
  Lang:    () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  Fix:     () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
  Arrow:   () => <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>,
  Alert:   () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  Menu:    () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>,
  Close:   () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  Chevron: () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>,
  Check:   () => <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"/></svg>,
  X:       () => <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  CritFix: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#e74c3c" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  WarnFix: () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f0b429" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
  LowFix:  () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3a9fd8" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>,
};

/* ─── Nav items ──────────────────────────────────────────────────────────────── */
const NAV = [
  { Icon: I.Upload,  label:'Upload',   active:false, badge:null   },
  { Icon: I.Score,   label:'ATS Score',active:true,  badge:null   },
  { Icon: I.Tailor,  label:'Tailor',   active:false, badge:'next' },
  { Icon: I.History, label:'History',  active:false, badge:'soon' },
  { Icon: I.Settings,label:'Settings', active:false, badge:'soon' },
];

/* ─── Sidebar ────────────────────────────────────────────────────────────────── */
function Sidebar({ open, onClose }) {
  return (
    <>
      <aside className={`sidebar${open ? ' sidebar--open' : ''}`}>
        <div className="sidebar__brand">
          <div className="sidebar__brand-dot" />
          <span className="sidebar__brand-name">AlignAI</span>
        </div>
        <span className="sidebar__section-label">Workspace</span>
        <nav className="sidebar__nav">
          {NAV.map(({ Icon, label, active, badge }) => (
            <button key={label} className={`sidebar__nav-item${active ? ' sidebar__nav-item--active' : ''}`}>
              <span className="sidebar__nav-icon"><Icon /></span>
              {label}
              {badge && <span className="sidebar__nav-badge">{badge}</span>}
            </button>
          ))}
        </nav>
        <div className="sidebar__footer">
          <div className="sidebar__status"><div className="sidebar__status-dot" />Backend connected</div>
          <div className="sidebar__status" style={{color:'#37455E',fontSize:'0.65rem'}}>localhost:8000</div>
        </div>
      </aside>
      <div className={`sidebar-overlay${open?'':' sidebar-overlay--hidden'}`} onClick={onClose} />
    </>
  );
}

/* ─── Derivation helpers ─────────────────────────────────────────────────────── */
function getStatus(score) {
  if (score >= 80) return { label:'Excellent',        cls:'excellent',  color:'#2ecc71' };
  if (score >= 65) return { label:'Good',             cls:'good',       color:'#27ae60' };
  if (score >= 50) return { label:'Fair',             cls:'fair',       color:'#f0b429' };
  if (score >= 35) return { label:'Needs Improvement',cls:'needs-work', color:'#e67e22' };
  return              { label:'Poor',             cls:'poor',       color:'#e74c3c' };
}

function getOneLiner(data) {
  const { skill_match, section_coverage } = data.layer_breakdown;
  const sa = data.structural_analysis;
  if (!sa.has_experience_section) return 'Your resume is missing an Experience section — a critical ATS requirement.';
  if (skill_match.score < 35)     return 'Your resume is missing too many required skills to rank well for this role.';
  if (skill_match.score >= 65 && section_coverage.score < 50) return 'Strong skill alignment, but your resume structure needs improvement.';
  if (section_coverage.score >= 70 && skill_match.score < 60) return 'Your resume is structurally solid but is missing key technical skills.';
  if (skill_match.score >= 65 && section_coverage.score >= 65) return 'Good overall match — fine-tuning keyword language could push you into the top bracket.';
  return 'Your resume shows potential but has gaps in both skills and structure.';
}

function getPotential(score, gaps) {
  const bump = (gaps || []).reduce((s, g) => s + (g.severity==='high'?15:g.severity==='medium'?8:4), 0);
  return Math.min(100, score + bump);
}

function simQuality(score) {
  // score is 0-100 (already normalised in backend)
  if (score < 8)  return { label:'Very Low',  cls:'red',    color:'#e74c3c', barColor:'linear-gradient(90deg,#8b1a0f,#e74c3c)' };
  if (score < 20) return { label:'Low',       cls:'orange', color:'#e67e22', barColor:'linear-gradient(90deg,#994c08,#e67e22)' };
  if (score < 40) return { label:'Fair',      cls:'yellow', color:'#f0b429', barColor:'linear-gradient(90deg,#b27d0e,#f0b429)' };
  if (score < 65) return { label:'Good',      cls:'green',  color:'#2ecc71', barColor:'linear-gradient(90deg,#1a9e4a,#2ecc71)' };
  return                  { label:'Strong',   cls:'green',  color:'#2ecc71', barColor:'linear-gradient(90deg,#1a9e4a,#2ecc71)' };
}

function metricQuality(score) {
  if (score >= 70) return { label:'Strong',      cls:'green'  };
  if (score >= 55) return { label:'Good',        cls:'green'  };
  if (score >= 40) return { label:'Fair',        cls:'yellow' };
  if (score >= 25) return { label:'Needs Work',  cls:'orange' };
  return                  { label:'Critical',    cls:'red'    };
}

// Build the "Why is my score X?" factors list
function buildWhyFactors(data) {
  const { gaps, skill_analysis, structural_analysis: sa, layer_breakdown: lb } = data;
  const factors = [];

  // Negatives from structural
  if (!sa.has_experience_section)
    factors.push({ dot:'red', text:'Missing Experience Section', impact:'-15 pts', impactCls:'neg' });
  if (sa.years_gap)
    factors.push({ dot:'orange', text:'Experience gap vs JD requirements', impact:'-8 pts', impactCls:'warn' });
  if (!sa.has_skills_section)
    factors.push({ dot:'orange', text:'No dedicated Skills section', impact:'-5 pts', impactCls:'warn' });

  // Negatives from skill gaps
  const missingReq = skill_analysis.missing_required.length;
  if (missingReq > 0)
    factors.push({ dot:'red', text:`Missing ${missingReq} Required Skill${missingReq>1?'s':''}`, impact:`-${missingReq*5} pts`, impactCls:'neg', detail: skill_analysis.missing_required.slice(0,3).join(', ') + (missingReq>3?` +${missingReq-3} more`:'') });

  // Low keyword match
  if (lb.content_similarity.score < 15)
    factors.push({ dot:'orange', text:'Very low ATS keyword overlap', impact:'-10 pts', impactCls:'warn' });

  // Positives
  const matchedReq = skill_analysis.matched_required.length;
  if (matchedReq > 0)
    factors.push({ dot:'green', text:`${matchedReq} required skill${matchedReq>1?'s':''} matched`, impact:`+${matchedReq*4} pts`, impactCls:'pos' });
  if (sa.has_experience_section && sa.has_education && sa.has_skills_section)
    factors.push({ dot:'green', text:'Strong resume structure', impact:'+20 pts', impactCls:'pos' });
  else if (sa.has_experience_section)
    factors.push({ dot:'green', text:'Experience section present', impact:'+15 pts', impactCls:'pos' });

  return factors;
}

// Build priority fixes from gaps
function buildFixes(gaps, sa) {
  const fixes = [];
  if (!sa.has_experience_section)
    fixes.push({ Icon:I.CritFix, title:'Add an Experience Section', desc:'This is the most critical missing element. ATS systems heavily weight work history.', impact:'+15 pts', cls:'critical', impactCls:'crit', items:[] });
  (gaps || []).forEach(g => {
    const isCrit = g.severity === 'high';
    const isWarn = g.severity === 'medium';
    const impact = isCrit ? '+15 pts' : isWarn ? '+8 pts' : '+4 pts';
    const Icon   = isCrit ? I.CritFix : isWarn ? I.WarnFix : I.LowFix;
    const cls    = isCrit ? 'critical' : isWarn ? 'warning' : 'low';
    const impactCls = isCrit ? 'crit' : isWarn ? 'warn' : 'low';
    const readableTitle = g.type
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
    fixes.push({ Icon, title: readableTitle, desc: g.suggestion, impact, cls, impactCls, items: g.items || [] });
  });
  return fixes;
}

/* ─── Collapsible skill section ──────────────────────────────────────────────── */
function SkillSection({ dotCls, name, skills, chipCls, icon, defaultOpen = false, maxVisible = 6 }) {
  const [open, setOpen] = useState(defaultOpen);
  const [showAll, setShowAll] = useState(false);
  if (!skills.length) return null;
  const visible = showAll ? skills : skills.slice(0, maxVisible);
  return (
    <div className="skill-section">
      <button className="skill-section__toggle" onClick={() => setOpen(o => !o)}>
        <div className="skill-section__toggle-left">
          <span className={`skill-section__dot skill-section__dot--${dotCls}`} />
          <span className="skill-section__name">{name}</span>
          <span className="skill-section__count">{skills.length}</span>
        </div>
        <span className={`skill-section__chevron${open?' skill-section__chevron--open':''}`}>
          <I.Chevron />
        </span>
      </button>
      {open && (
        <>
          <div className="skill-chips">
            {visible.map((s, i) => (
              <span key={i} className={`skill-chip skill-chip--${chipCls}`}>
                <span className="skill-chip__icon">{icon}</span> {s}
              </span>
            ))}
          </div>
          {skills.length > maxVisible && !showAll && (
            <button className="show-more-btn" onClick={() => setShowAll(true)}>
              Show all {skills.length} {name.toLowerCase()} →
            </button>
          )}
        </>
      )}
    </div>
  );
}

/* ─── SVG circular dial ──────────────────────────────────────────────────────── */
function ScoreDial({ score, color }) {
  const r = 52;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  return (
    <div className="hero-dial__ring">
      <svg className="hero-dial__svg" viewBox="0 0 120 120">
        <circle className="hero-dial__track" cx="60" cy="60" r={r} />
        <circle
          className="hero-dial__fill"
          cx="60" cy="60" r={r}
          stroke={color}
          strokeDasharray={`${circ - offset} ${offset}`}
          strokeOpacity="0.85"
        />
      </svg>
      <div className="hero-dial__center">
        <span className="hero-dial__number" style={{ color }}>{score}</span>
        <span className="hero-dial__denom">/100</span>
      </div>
    </div>
  );
}

/* ─── Main ───────────────────────────────────────────────────────────────────── */
export default function ScoreScreen({ resumeDocumentId, jdDocumentId, onContinue }) {
  const [scoreData,   setScoreData]   = useState(null);
  const [loading,     setLoading]     = useState(true);
  const [error,       setError]       = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const hasStarted = useRef(false);

  useEffect(() => {
    const run = async () => {
      setLoading(true); setError(null);
      try {
        const res = await fetch('http://localhost:8000/api/ats-score', {
          method:'POST', headers:{'Content-Type':'application/json'},
          body: JSON.stringify({ resume_document_id: resumeDocumentId, jd_document_id: jdDocumentId }),
        });
        if (!res.ok) {
          let msg = 'An unknown error occurred';
          try { const j = await res.json(); msg = j.detail || msg; } catch {}
          throw new Error(msg);
        }
        const d = await res.json();
        if (d.success) setScoreData(d);
        else throw new Error('ATS scoring failed. Please try again.');
      } catch (e) { setError(e.message); }
      finally { setLoading(false); }
    };
    if (hasStarted.current) return;
    hasStarted.current = true;
    run();
  }, [resumeDocumentId, jdDocumentId]);

  const shell = (children) => (
    <div className="dashboard">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="dashboard__main">
        <header className="topbar">
          <button className="topbar__hamburger" onClick={() => setSidebarOpen(o => !o)}>
            {sidebarOpen ? <I.Close /> : <I.Menu />}
          </button>
          <div className="topbar__left">
            <div className="topbar__breadcrumb">AlignAI <span className="topbar__breadcrumb-sep">›</span> <span style={{color:'#DFDFE0'}}>ATS Score</span></div>
            <div className="topbar__title">ATS Score Analysis</div>
          </div>
          <div className="topbar__right">
            <div className="topbar__step-indicator">
              <div className="topbar__step-dot topbar__step-dot--done"   title="Upload" />
              <div className="topbar__step-dot topbar__step-dot--active" title="ATS Score" />
              <div className="topbar__step-dot" title="Tailor" />
            </div>
          </div>
        </header>
        <main className="dashboard__content">{children}</main>
      </div>
    </div>
  );

  if (loading) return shell(
    <div className="score-loading">
      <div className="score-loading__spinner" />
      <div className="score-loading__text">Calculating your ATS score…</div>
      <div className="score-loading__sub">Running 3-layer analysis — this takes a few seconds</div>
    </div>
  );

  if (error) return shell(
    <div className="score-error"><span className="score-error__icon"><I.Alert /></span>{error}</div>
  );

  /* ─ Destructure ─ */
  const { final_score, layer_breakdown: lb, skill_analysis: sa, structural_analysis: str, content_similarity_detail: cd, gaps } = scoreData;
  const status    = getStatus(final_score);
  const oneLiner  = getOneLiner(scoreData);
  const potential = getPotential(final_score, gaps);
  const delta     = potential - final_score;
  const whyItems  = buildWhyFactors(scoreData);
  const fixes     = buildFixes(gaps, str);
  const simScore  = lb.content_similarity.score;   // already 0-100
  const simQ      = simQuality(simScore);
  const skillQ    = metricQuality(lb.skill_match.score);
  const structQ   = metricQuality(lb.section_coverage.score);

  /* Language match plain-English explanation */
  function simExplain(q) {
    if (q.cls === 'red')    return { headline:'Very Low', body:'Your resume uses very few of the important phrases found in the job description. Project descriptions and bullet points should better reflect the wording used in the job posting.' };
    if (q.cls === 'orange') return { headline:'Low', body:'Your resume captures some of the job\'s key language, but significant phrasing differences remain. Mirror the exact terms the job posting uses when describing your experience.' };
    if (q.cls === 'yellow') return { headline:'Fair', body:'Your resume partially matches the job\'s language. Consider aligning your bullet points more closely with the role\'s specific responsibilities.' };
    return { headline:'Good', body:'Your resume language is well-aligned with the job description. Small refinements could push this into the Excellent range.' };
  }
  const simExp = simExplain(simQ);

  /* Structural checklist items */
  const sections = [
    { label:'Experience',    present: str.has_experience_section, impact:'-15 ATS points' },
    { label:'Education',     present: str.has_education,          impact:'-5 ATS points'  },
    { label:'Skills',        present: str.has_skills_section,     impact:'-8 ATS points'  },
    { label:'Projects',      present: str.has_projects,           impact:'-4 ATS points'  },
    { label:'Certifications',present: str.has_certifications,     impact:'-3 ATS points'  },
  ];

  return shell(
    <>
      {/* ══ SECTION 1: HERO ═══════════════════════════════════════════════════ */}
      <div className="score-section">
        <div className="score-section-label">Overall Score</div>

        <div className="hero-card">
          {/* Dial */}
          <div className="hero-dial">
            <ScoreDial score={final_score} color={status.color} />
            <span className={`hero-status-badge hero-status-badge--${status.cls}`}>
              {status.label}
            </span>
          </div>

          {/* Info */}
          <div className="hero-info">
            <div className="hero-info__label">Step 2 of 3 · ATS Score</div>
            <div className="hero-info__headline">Your resume analysis is complete.</div>
            <div className="hero-info__oneliner">{oneLiner}</div>
            {delta > 0 && (
              <div className="hero-potential">
                Potential score after fixing issues:&nbsp;
                <strong style={{color:'#DFDFE0'}}>{potential}</strong>
                <span className="hero-potential__delta">&nbsp;(+{delta} pts)</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ══ SECTION 2: WHY ════════════════════════════════════════════════════ */}
      {whyItems.length > 0 && (
        <div className="score-section">
          <div className="score-section-label">Why this score?</div>
          <div className="why-card">
            <div className="why-card__header">
              <div className="why-card__header-icon"><I.Why /></div>
              <div>
                <div className="why-card__title">Why your score is {final_score}</div>
                <div className="why-card__sub">Top factors affecting your ATS ranking</div>
              </div>
            </div>
            <div className="why-list">
              {whyItems.map((item, i) => (
                <div key={i} className="why-item">
                  <span className={`why-item__dot why-item__dot--${item.dot}`} />
                  <div className="why-item__text">
                    {item.text}
                    {item.detail && <><br /><span>{item.detail}</span></>}
                  </div>
                  <span className={`why-item__impact why-item__impact--${item.impactCls}`}>{item.impact}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ══ SECTION 3: METRIC CARDS ═══════════════════════════════════════════ */}
      <div className="score-section">
        <div className="score-section-label">Score Breakdown</div>
        <div className="metric-row">

          {/* Skills Match */}
          <div className={`metric-card metric--${skillQ.cls}`}>
            <div className="metric-card__top">
              <div className="metric-card__icon-wrap"><I.Skills /></div>
            </div>
            <div>
              <div className="metric-card__name">Skills Match</div>
              <div className="metric-card__pct">{lb.skill_match.score}<span style={{fontSize:'1rem',color:'#6E7788'}}> %</span></div>
              <div className={`metric-card__status`}>{skillQ.label}</div>
            </div>
            <div className="metric-card__bar-wrap">
              <div className="metric-card__bar" style={{width:`${lb.skill_match.score}%`}} />
            </div>
            <div className="metric-card__note">
              {sa.matched_required.length} of {sa.matched_required.length + sa.missing_required.length} required skills found in your resume.
            </div>
          </div>

          {/* Resume Completeness */}
          <div className={`metric-card metric--${structQ.cls}`}>
            <div className="metric-card__top">
              <div className="metric-card__icon-wrap"><I.Structure /></div>
            </div>
            <div>
              <div className="metric-card__name">Resume Completeness</div>
              <div className="metric-card__pct">{lb.section_coverage.score}<span style={{fontSize:'1rem',color:'#6E7788'}}> %</span></div>
              <div className="metric-card__status">{structQ.label}</div>
            </div>
            <div className="metric-card__bar-wrap">
              <div className="metric-card__bar" style={{width:`${lb.section_coverage.score}%`}} />
            </div>
            <div className="metric-card__note">
              How well your resume sections align with what this role requires.
            </div>
          </div>

          {/* ATS Keyword Match */}
          <div className={`metric-card metric--${simQ.cls}`}>
            <div className="metric-card__top">
              <div className="metric-card__icon-wrap"><I.Lang /></div>
            </div>
            <div>
              <div className="metric-card__name">ATS Keyword Match</div>
              <div className="metric-card__pct" style={{color:simQ.color}}>{simQ.label}</div>
            </div>
            <div className="metric-card__bar-wrap">
              <div className="metric-card__bar" style={{width:`${Math.max(simScore, 4)}%`, background:simQ.barColor}} />
            </div>
            <div className="metric-card__note">
              How closely your resume language mirrors the job posting's phrasing.
            </div>
          </div>
        </div>
      </div>

      {/* ══ SECTION 4: DETAILED ANALYSIS ══════════════════════════════════════ */}
      <div className="score-section">
        <div className="score-section-label">Detailed Analysis</div>

        <div className="two-col">
          {/* 4a — Resume Structure */}
          <div className="panel">
            <div className="panel__header">
              <div className="panel__header-icon"><I.Structure /></div>
              <div>
                <div className="panel__title">Resume Structure</div>
                <div className="panel__subtitle">Key sections expected by ATS systems</div>
              </div>
            </div>
            <div className="panel__body">
              <div className="checklist">
                {sections.map(({ label, present, impact }) => (
                  <div key={label} className={`checklist-item${present?'':' checklist-item--missing'}`}>
                    <div className={`checklist-item__icon checklist-item__icon--${present?'pass':'fail'}`}>
                      {present ? <I.Check /> : <I.X />}
                    </div>
                    <div className="checklist-item__body">
                      <div className={`checklist-item__label checklist-item__label--${present?'pass':'fail'}`}>{label}</div>
                      {!present && (
                        <div className="checklist-item__note">
                          Estimated impact: {impact}
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Years of experience row */}
                <div className="checklist-item">
                  <div className={`checklist-item__icon checklist-item__icon--${str.years_gap?'fail':'pass'}`}>
                    {str.years_gap ? <I.X /> : <I.Check />}
                  </div>
                  <div className="checklist-item__body">
                    <div className={`checklist-item__label checklist-item__label--${str.years_gap?'fail':'pass'}`}>
                      Years of Experience
                    </div>
                    <div className="checklist-item__years-row">
                      <span className="checklist-item__years-pill checklist-item__years-pill--ok">
                        Detected: {str.years_detected}y
                      </span>
                      <span className={`checklist-item__years-pill checklist-item__years-pill--${str.years_required?'warn':'na'}`}>
                        Required: {str.years_required ?? 'Not specified'}
                      </span>
                    </div>
                    {str.years_gap && <div className="checklist-item__note">Gap detected vs JD requirement</div>}
                  </div>
                </div>
              </div>

              {/* JD requirements */}
              <div className="jd-req-row" style={{marginTop:'0.75rem'}}>
                <span className="jd-req-pill jd-req-pill--neutral">JD Requirements:</span>
                <span className={`jd-req-pill jd-req-pill--${str.jd_requires_degree?(str.has_education?'match':'miss'):'neutral'}`}>
                  {str.jd_requires_degree ? 'Degree required' : 'No degree req'}
                </span>
                <span className={`jd-req-pill jd-req-pill--${str.jd_emphasizes_certifications?(str.has_certifications?'match':'miss'):'neutral'}`}>
                  {str.jd_emphasizes_certifications ? 'Certs emphasised' : 'No cert req'}
                </span>
                <span className={`jd-req-pill jd-req-pill--${str.jd_requires_leadership?(str.resume_shows_leadership?'match':'miss'):'neutral'}`}>
                  {str.jd_requires_leadership ? `Leadership ${str.resume_shows_leadership?'✓':'needed'}` : 'No leadership req'}
                </span>
              </div>
            </div>
          </div>

          {/* 4b — Skill Analysis */}
          <div className="panel">
            <div className="panel__header">
              <div className="panel__header-icon"><I.Skills /></div>
              <div>
                <div className="panel__title">Skill Analysis</div>
                <div className="panel__subtitle">Required, preferred and bonus skills</div>
              </div>
            </div>
            <div className="panel__body">
              <SkillSection dotCls="matched"  name="Required Skills"          skills={sa.matched_required}  chipCls="matched"   icon="✓" defaultOpen={true} />
              <SkillSection dotCls="missing"  name="Missing Required"         skills={sa.missing_required}  chipCls="missing"   icon="⚠" defaultOpen={true} />
              <SkillSection dotCls="preferred" name="Preferred Skills"        skills={sa.matched_preferred} chipCls="preferred" icon="◎" />
              <SkillSection dotCls="preferred" name="Missing Preferred"       skills={sa.missing_preferred} chipCls="preferred" icon="◎" />
              <SkillSection dotCls="bonus"    name="Bonus Skills"             skills={sa.bonus_skills}      chipCls="bonus"     icon="+" maxVisible={4} />
            </div>
          </div>
        </div>

        {/* 4c — Resume Language Match */}
        <div className="panel">
          <div className="panel__header">
            <div className="panel__header-icon"><I.Lang /></div>
            <div>
              <div className="panel__title">Resume Language Match</div>
              <div className="panel__subtitle">How closely your resume mirrors the job posting's phrasing</div>
            </div>
          </div>
          <div className="lang-match-body">
            <div className="lang-match-score">
              <span className="lang-match-score__label" style={{color: simQ.color}}>{simExp.headline}</span>
              <span className={`lang-match-score__badge metric--${simQ.cls}`}
                style={{background:`rgba(${simQ.color.replace('#','').match(/.{2}/g).map(h=>parseInt(h,16)).join(',')},0.1)`,
                        border:`1px solid rgba(${simQ.color.replace('#','').match(/.{2}/g).map(h=>parseInt(h,16)).join(',')},0.25)`,
                        color: simQ.color}}>
                ATS Keyword Match
              </span>
            </div>
            <div className="lang-match-bar-wrap">
              <div className="lang-match-bar" style={{width:`${Math.max(simScore,3)}%`, background:simQ.barColor}} />
            </div>
            <div className="lang-match-explain">
              {simExp.body}
              {' '}<strong>Use the Tailor step to generate AI-powered rewrites</strong> that align your bullet points with the exact language this role expects.
            </div>
          </div>
        </div>
      </div>

      {/* ══ SECTION 5: PRIORITY FIXES ══════════════════════════════════════════ */}
      {fixes.length > 0 && (
        <div className="score-section">
          <div className="score-section-label">Priority Fixes</div>
          <div className="panel">
            <div className="panel__header">
              <div className="panel__header-icon"><I.Fix /></div>
              <div>
                <div className="panel__title">What Needs Attention</div>
                <div className="panel__subtitle">Sorted by estimated score impact — fix these first</div>
              </div>
            </div>
            <div className="panel__body">
              <div className="fixes-list">
                {fixes.map((f, i) => (
                  <div key={i} className={`fix-item fix-item--${f.cls}`}>
                    <div className="fix-item__icon"><f.Icon /></div>
                    <div className="fix-item__body">
                      <div className="fix-item__title">{f.title}</div>
                      {f.items.length > 0 && (
                        <div className="fix-item__items">
                          {f.items.slice(0,5).map((it,j) => <span key={j} className="fix-item__chip">{it}</span>)}
                          {f.items.length > 5 && <span className="fix-item__chip">+{f.items.length-5} more</span>}
                        </div>
                      )}
                      <div className="fix-item__desc">{f.desc}</div>
                    </div>
                    <div className={`fix-item__impact fix-item__impact--${f.impactCls}`}>
                      <I.Arrow />{f.impact}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ══ SECTION 6: CTA ════════════════════════════════════════════════════ */}
      <div className="cta-section">
        <div className="cta-section__eyebrow">Ready to improve?</div>
        <div className="cta-section__title">Ready to improve your ATS score?</div>
        <div className="cta-section__sub">
          Generate AI-powered resume improvements tailored to this job description.
          Every suggestion is grounded in your actual experience and audited for accuracy.
        </div>
        <button id="tailor-btn" className="cta-btn" onClick={() => onContinue?.({ resumeDocumentId, jdDocumentId })}>
          Generate Tailored Suggestions
          <I.Arrow />
        </button>
      </div>
    </>
  );
}
