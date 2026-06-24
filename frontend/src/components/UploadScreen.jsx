import React, { useState } from 'react';

export default function UploadScreen({ onComplete }) {
  const [resumeData, setResumeData] = useState(null);
  const [resumeLoading, setResumeLoading] = useState(false);
  const [resumeError, setResumeError] = useState(null);

  const [jdData, setJdData] = useState(null);
  const [jdLoading, setJdLoading] = useState(false);
  const [jdError, setJdError] = useState(null);

  const handleUpload = async (event, docType) => {
    const file = event.target.files[0];
    if (!file) return;

    const isResume = docType === 'resume';
    const setLoading = isResume ? setResumeLoading : setJdLoading;
    const setError = isResume ? setResumeError : setJdError;
    const setData = isResume ? setResumeData : setJdData;

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
        let errorMessage = 'An unknown error occurred';
        try {
          const errJson = await response.json();
          // Expecting backend to return { detail: "some error message" }
          errorMessage = errJson.detail || errorMessage;
        } catch (e) {
          errorMessage = response.statusText;
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      if (data.success) {
        if (data.doc_type && data.doc_type !== docType) {
          const expectedType = docType === 'resume' ? 'Resume' : 'Job Description';
          const detectedType = data.doc_type === 'resume' ? 'Resume' : 'Job Description';
          throw new Error(`Invalid document: You uploaded a ${detectedType} in the ${expectedType} slot.`);
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
  const resumeDocumentId = resumeData?.document_id;
  const jdDocumentId = jdData?.document_id;

  if (onComplete) {
    onComplete({
      resumeData,
      jdData,
      resumeDocumentId,
      jdDocumentId
    });
  }
};

  const isContinueEnabled = resumeData?.success && jdData?.success;

  return (
    <div>
      <h2>Upload Documents</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <h3>Resume</h3>
        <input 
          type="file" 
          accept=".pdf" 
          onChange={(e) => handleUpload(e, 'resume')} 
        />
        {resumeLoading && <p>Uploading...</p>}
        {resumeError && <p style={{ color: 'red' }}>Error: {resumeError}</p>}
        {resumeData && <p>Uploaded successfully: {resumeData.filename}</p>}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3>Job Description</h3>
        <input 
          type="file" 
          accept=".pdf" 
          onChange={(e) => handleUpload(e, 'jd')} 
        />
        {jdLoading && <p>Uploading...</p>}
        {jdError && <p style={{ color: 'red' }}>Error: {jdError}</p>}
        {jdData && <p>Uploaded successfully: {jdData.filename}</p>}
      </div>

      <button 
        onClick={handleContinue} 
        disabled={!isContinueEnabled}
      >
        Continue
      </button>
    </div>
  );
}
