import React from 'react';
import VideoUpload from '../Video.jsx'; 
import '../VideoUpload.css'

function UploadPage() {
  return (
    <div>
      <div className="uploadArea">
        <VideoUpload />  
      </div>
    </div>
  );
}

export default UploadPage;
