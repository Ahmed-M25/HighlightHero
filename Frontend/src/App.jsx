import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import Background from './assets/IMG_8670.mp4'
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