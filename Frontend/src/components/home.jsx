import React from 'react';
import { useNavigate } from 'react-router-dom';
import Background from '../assets/Lebron.mp4';
import './HomePage.css';

function HomePage() {
  const navigate = useNavigate();

  const handleRedirect = () => {
    navigate('/upload'); 
  };

  return (
    <div className="home-page">
      <video autoPlay loop muted className="background-video">
        <source src={Background} type="video/mp4" />
      </video>

      <div className="overlay"></div>

      <div className="text-container">
        <h1 className="home-text">
          Take a Step Forward in 
          <span className="highlight"> Guaranteeing Your Sports Future</span>
        </h1>
        <p className="sub-text">
          Join the next generation of athletes and make your mark on the world of sports.
        </p>
        <button className="cta-button" onClick={handleRedirect}>Get Started</button>
      </div>
    </div>
  );
}

export default HomePage;
