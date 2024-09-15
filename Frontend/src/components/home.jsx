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
        <div className='sync'>
          <h1 className="home-text">
            Make The Highlight of your
            <span className=""> Dreams Today</span>
          </h1>
        </div>
        {/* <a className="cta-text" onClick={handleRedirect}>Get Started</a> */}
        <button className='cta-text' onClick={handleRedirect}>Get Started</button>
      </div>
    </div>
  );
}

export default HomePage;