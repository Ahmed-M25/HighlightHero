import React, { useState, useEffect } from 'react';

const VideoImport = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [videoSrc, setVideoSrc] = useState('');

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);

    if (file) {
      const videoUrl = URL.createObjectURL(file);
      setVideoSrc(videoUrl);
    }
  };

  useEffect(() => {
    // Cleanup function to revoke the object URL when component unmounts
    return () => {
      if (videoSrc) {
        URL.revokeObjectURL(videoSrc);
      }
    };
  }, [videoSrc]);

  return (
    <div>
      {/* put fade in buttons here */}
      {videoSrc && (
        <div>
          <h3>Video Preview</h3>
          <video width="320" height="240" controls>
            <source src={videoSrc} type={selectedFile.type} />
            Your browser does not support the video tag.
          </video>
        </div>
      )}
    </div>
  );
};

export default VideoImport;