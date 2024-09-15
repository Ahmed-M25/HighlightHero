import React from 'react';
import { Link } from 'react-router-dom';
import './navigation.css';

function Navigation() {
  return (
    <nav className="navigation">
      <ul>
        <li><Link to="/">Home</Link></li>
        <li><Link to="/about">About</Link></li>
      </ul>
    </nav>
  );
}

export default Navigation;
