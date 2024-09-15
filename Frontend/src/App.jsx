import { useState } from 'react'
import Background from './assets/catVideo.mp4'
import VideoImport from './Video.jsx' // Import the correct component
import './App.css'

function App() {
  return (
    <div className="app-container">
      <video autoPlay loop muted className="background-video">
        <source src={Background} type="video/mp4" />
      </video>
      <div className="content-overlay">
        <VideoImport />  {/* Render VideoImport here */}
      </div>
    </div>
  )
}

export default App
