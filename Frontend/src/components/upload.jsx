import React from 'react';
import VideoImport from '../Video.jsx' // Import the correct component

function UploadPage () {
    return (
        <div>
            <div className="content-overlay">
                <VideoImport />  {/* Render VideoImport here */}
            </div>
        </div>
    );
}

export default UploadPage;