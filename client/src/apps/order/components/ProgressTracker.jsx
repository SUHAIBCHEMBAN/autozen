import React from 'react';
import './ProgressTracker.css';

const ProgressTracker = ({ currentStatus }) => {
  const steps = [
    { id: 'pending', icon: '✓', label: 'Ordered' },
    { id: 'confirmed', icon: '✓', label: 'Confirmed' },
    { id: 'processing', icon: '⚙', label: 'Processing' },
    { id: 'shipped', icon: '🚚', label: 'Shipped' },
    { id: 'delivered', icon: '🏠', label: 'Delivered' }
  ];

  const isStepActive = (stepId) => {
    const currentIndex = steps.findIndex(step => step.id === currentStatus);
    const stepIndex = steps.findIndex(step => step.id === stepId);
    return stepIndex <= currentIndex;
  };

  return (
    <div className="order-progress">
      {steps.map((step, index) => (
        <div 
          key={step.id} 
          className={`progress-step ${isStepActive(step.id) ? 'active' : ''}`}
        >
          <div className="step-icon">{step.icon}</div>
          <span>{step.label}</span>
        </div>
      ))}
    </div>
  );
};

export default ProgressTracker;