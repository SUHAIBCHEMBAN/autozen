import React from 'react';
import './StatusBadge.css';

const StatusBadge = ({ status, className = '' }) => {
  const getStatusClass = (status) => {
    switch (status) {
      case 'delivered': return 'status-success';
      case 'shipped': return 'status-info';
      case 'processing': return 'status-warning';
      case 'pending': return 'status-pending';
      case 'cancelled': return 'status-danger';
      default: return 'status-default';
    }
  };

  const formatStatus = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1).replace(/_/g, ' ');
  };

  return (
    <span className={`status-badge ${getStatusClass(status)} ${className}`}>
      {formatStatus(status)}
    </span>
  );
};

export default StatusBadge;