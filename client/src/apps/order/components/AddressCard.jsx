import React from 'react';
import './AddressCard.css';

const AddressCard = ({ title, address, isDefault = false, onSelect, showSelectButton = false }) => {
  return (
    <div className="address-card" onClick={onSelect}>
      <div className="address-header">
        <h3>{title}</h3>
        {isDefault && <span className="default-badge">Default</span>}
      </div>
      <div className="address-body">
        <p className="address-name">{address.first_name} {address.last_name}</p>
        <p className="address-street">{address.address_line1}</p>
        {address.address_line2 && <p className="address-street">{address.address_line2}</p>}
        <p className="address-city">
          {address.city}, {address.state} {address.postal_code}
        </p>
        <p className="address-country">{address.country}</p>
        <p className="address-phone">{address.phone_number}</p>
      </div>
      {showSelectButton && (
        <div className="address-select">
          <span>Use this address</span>
        </div>
      )}
    </div>
  );
};

export default AddressCard;