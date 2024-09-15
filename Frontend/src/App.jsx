import React from 'react'
import { BrowserRouter as Router, Route, Routes } from "react-router-dom"
import HomePage from "./components/home"
import AboutPage from "./components/about"
import UploadPage from "./components/upload"

import Navigation from './components/navigation'

import './App.css'

function App() {
  return (
    <Router>
      <main>
        <Navigation />
        <Routes>
          <Route path='/' element={<HomePage/>} />
          <Route path="/about" element={<AboutPage/>} />
          <Route path="/upload" element={<UploadPage/>} />
        </Routes>
      </main>
    </Router>
  )
}

export default App
