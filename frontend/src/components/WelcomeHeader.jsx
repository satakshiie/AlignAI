import React from 'react';
import LottieModule from 'lottie-react';
import animationDataFile from '../../assets/Frame-1.json';
import frame2Image from '../assets/Frame 2.png';
import './WelcomeHeader.css';

const Lottie = LottieModule.default || LottieModule;
const animationData = animationDataFile.default || animationDataFile;

const WelcomeHeader = () => {
  return (
    <div className="welcome-header">
      <div className="welcome-header-left">
        <div className="brand-content">
          <h1 className="brand-title">AlignAI<span className="frame-text"></span></h1>
          <h2 className="brand-subtitle">Land the Interview.<br />Don't Fake the Skills.</h2>
          <p className="brand-description">
            Paste a job link, upload your resume, and let AlignAI do the heavy lifting. Get a perfectly tailored, ATS-friendly resume or a personalized roadmap to build the skills you're missing.
          </p>
          <button className="get-started-button">
            get started
          </button>
        </div>
      </div>
      <div className="welcome-header-right">
        <div className="graphics-wrapper">
          <img src={frame2Image} alt="Resume behind" className="background-frame" />
          <div className="lottie-container">
            <Lottie
              animationData={animationData}
              loop={true}
              autoplay={true}
              style={{ width: '100%', height: '100%' }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeHeader;
