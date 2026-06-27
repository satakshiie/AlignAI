import React from 'react';
import { useLottie } from 'lottie-react';
import animationData from '../assets/Frame-1.json';
import './LandingPage.css';

function LottieAnimation() {
  const { View } = useLottie(
    { animationData, loop: true, autoplay: true },
    { width: '100%', height: '100%' }
  );
  return View;
}

export default function LandingPage({ onStart }) {
  return (
    <div className="landing">

      {/* ── Split background layers ── */}
      <div className="landing__bg-left"  aria-hidden="true" />
      <div className="landing__bg-right" aria-hidden="true" />
      <div className="landing__seam"     aria-hidden="true" />

      {/* ── Grid & texture ── */}
      <div className="landing__grid"      aria-hidden="true" />
      <div className="landing__scanlines" aria-hidden="true" />

      {/* ── Floating orbs ── */}
      <div className="landing__orb landing__orb--1" aria-hidden="true" />
      <div className="landing__orb landing__orb--2" aria-hidden="true" />
      <div className="landing__orb landing__orb--3" aria-hidden="true" />

      {/* ── Fixed nav ── */}
      <nav className="landing__nav" role="navigation" aria-label="Main navigation">
        <div className="landing__nav-logo">
          <div className="landing__nav-logo-dot" aria-hidden="true" />
          AlignAI
        </div>
        <div className="landing__nav-right">
          <span className="landing__nav-tag">Resume Intelligence</span>
        </div>
      </nav>

      {/* ══ Two-column body ═══════════════════════════════════════════ */}
      <div className="landing__body">

        {/* ── LEFT — text & CTA ── */}
        <div className="landing__left">

          <div className="landing__badge" role="note">
            <span className="landing__badge-dot" aria-hidden="true" />
            Multi-Agent · Human-in-the-Loop
          </div>

          <h1 className="landing__headline">
            <span className="landing__headline-static">Your resume,</span>
            <span className="landing__headline-gradient">truly aligned.</span>
          </h1>

          <p className="landing__desc">
            AlignAI scores your resume against any job description using a{' '}
            <strong>three-layer ATS engine</strong>, then generates{' '}
            <strong>hallucination-aware suggestions</strong> — every rewrite grounded
            in your actual experience, audited by an independent Critic before you
            ever see it.
          </p>

          <div className="landing__cta-group">
            <button
              id="start-btn"
              className="landing__cta"
              onClick={onStart}
              aria-label="Start aligning your resume"
            >
              Get Started
              <span className="landing__cta-arrow" aria-hidden="true">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </span>
            </button>

            <div className="landing__stats" role="list" aria-label="Key statistics">
              <div className="landing__stat" role="listitem">
                <span className="landing__stat-value">3-layer</span>
                <span className="landing__stat-label">ATS Engine</span>
              </div>
              <div className="landing__stat-sep" aria-hidden="true" />
              <div className="landing__stat" role="listitem">
                <span className="landing__stat-value">5-node</span>
                <span className="landing__stat-label">Agent Graph</span>
              </div>
              <div className="landing__stat-sep" aria-hidden="true" />
              <div className="landing__stat" role="listitem">
                <span className="landing__stat-value">0</span>
                <span className="landing__stat-label">Hallucinations</span>
              </div>
            </div>
          </div>

        </div>

        {/* ── RIGHT — Lottie animation ── */}
        <div className="landing__right">

          {/* Floating HUD labels */}
          <span className="landing__hud landing__hud--tl" aria-hidden="true">
            SYS:ACTIVE
          </span>
          <span className="landing__hud landing__hud--br" aria-hidden="true">
            AI:READY
          </span>

          <div className="landing__right-frame" aria-label="AlignAI animation">
            {/* Decorative inner brackets */}
            <div className="landing__right-frame-inner" aria-hidden="true" />

            {/* Rotating orbit rings */}
            <div className="landing__ring"     aria-hidden="true" />
            <div className="landing__ring landing__ring--2" aria-hidden="true" />

            {/* Lottie */}
            <div className="landing__lottie">
              <LottieAnimation />
            </div>
          </div>
        </div>

      </div>{/* end landing__body */}

      {/* ── Scroll hint ── */}
      <div className="landing__scroll" aria-hidden="true">
        <div className="landing__scroll-line" />
        <span className="landing__scroll-label">Scroll</span>
      </div>

    </div>
  );
}
