import { useState } from 'react'
import Background from './assets/catVideo.mp4'
import Video from './Video.jsx'
import './App.css'

function App() {
  return (
    <div className="app-container">
      <video autoPlay loop muted className="background-video">
        <source src={Background} type="video/mp4" />
      </video>
      <div className="content-overlay">
        <Video />
      </div>
    </div>
  )
}

export default App