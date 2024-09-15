import React, { useState } from 'react';
import axios from 'axios';
import ReactPlayer from 'react-player';
import './VideoUpload.css';

function VideoUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadMessage, setUploadMessage] = useState("");
  const [videoUrl, setVideoUrl] = useState(""); // Store the URL of the processed video

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleFileUpload = async (event) => {
    event.preventDefault();

    if (!selectedFile) {
      setUploadMessage("Please select a file first.");
      return;
    }

    const formData = new FormData();
    formData.append("video", selectedFile);

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload_video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        withCredentials: true,
      });

      // Using the file path returned from the server as the video URL
      setVideoUrl('output.mp4');
    } catch (error) {
      if (error.response) {
        setUploadMessage(`Error uploading file: ${error.response.status} - ${error.response.data.error}`);
      } else if (error.request) {
        setUploadMessage("No response from server.");
      } else {
        setUploadMessage("Error: " + error.message);
      }
    }
  };

  return (
    <div style={{
      backgroundColor: 'black',
      color: 'white',
      minHeight: '100vh',
      width: '100vw',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
    }}>
      <div>
        <h2>Upload Video</h2>
        <form onSubmit={handleFileUpload}>
          <label htmlFor="file-upload" className="custom-file-upload" style={{
              marginTop: '10px',
              marginRight: '5px',
              padding: '8px 16px',
              color: 'black',
              background: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}>
            Upload File
          </label>
          <input id="file-upload" type="file" onChange={handleFileChange} accept=".mp4" style={{display:'none'}} />
          <button type="submit" style={{
              marginTop: '10px',
              marginLeft: '5px',
              padding: '8px 16px',
              color: 'black',
              background: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}>Submit</button>
        </form>
        {uploadMessage && <p>{uploadMessage}</p>}
      </div>
      <br/>
      <br/>
      {videoUrl && (
        <video controls width="1200">
          <source src={videoUrl} type="video/mp4"/>
        </video>
      )}
    </div>
  );
}

export default VideoUpload;
