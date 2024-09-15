import React from 'react';
import Background from '../assets/catVideo.mp4'

function HomePage () {
    return (
        <div className="app-container">
            <video autoPlay loop muted className="background-video">
                <source src={Background} type="video/mp4" />
            </video>
        </div>
    );
}

export default HomePage;