import React from 'react';
import './Tag.css';

const Tag = ({ text, color = 'default', size = 'medium' }) => {
  return (
    <span className={`tag ${color} ${size}`}>
      {text}
    </span>
  );
};

export default Tag;