import React from 'react';
import './OrderItem.css';

const OrderItem = ({ item, showImage = false }) => {
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-product.png';
    if (image.startsWith('http')) return image;
    return `http://localhost:8000${image}`;
  };

  return (
    <div className="order-item">
      {showImage && item.product_image && (
        <img 
          src={getImageUrl(item.product_image)} 
          alt={item.product_name}
          className="item-image"
          onError={(e) => { e.target.src = '/placeholder-product.png' }}
        />
      )}
      <div className="item-info">
        <h3>{item.product_name}</h3>
        {item.product_sku && <p className="item-sku">SKU: {item.product_sku}</p>}
        <p className="item-quantity">Quantity: {item.quantity}</p>
      </div>
      <div className="item-price">
        ₹{parseFloat(item.total_price || (parseFloat(item.price) * item.quantity)).toFixed(2)}
      </div>
    </div>
  );
};

export default OrderItem;