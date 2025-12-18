import React from 'react';
import './OrderSummary.css';

const OrderSummary = ({ items, totals, showButton = false, onPlaceOrder, submitting = false }) => {
  return (
    <div className="summary-card">
      <h2>Order Summary</h2>
      <div className="summary-items">
        {items.map((item) => (
          <div key={item.id} className="summary-item">
            <div className="summary-item-info">
              <span className="summary-item-name">{item.product_name}</span>
              <span className="summary-item-qty">Qty: {item.quantity}</span>
            </div>
            <span className="summary-item-price">
              ₹{(parseFloat(item.price) * item.quantity).toFixed(2)}
            </span>
          </div>
        ))}
      </div>
      <div className="summary-divider"></div>
      <div className="summary-row">
        <span>Subtotal</span>
        <span>₹{totals.subtotal.toFixed(2)}</span>
      </div>
      <div className="summary-row">
        <span>VAT (12%)</span>
        <span>₹{totals.taxAmount.toFixed(2)}</span>
      </div>
      <div className="summary-row">
        <span>Shipping</span>
        <span>₹{totals.shippingCost.toFixed(2)}</span>
      </div>
      <div className="summary-divider"></div>
      <div className="summary-row summary-total">
        <span>Total</span>
        <span>₹{totals.totalAmount.toFixed(2)}</span>
      </div>
      {showButton && (
        <button
          type="submit"
          className="btn-place-order"
          disabled={submitting}
          onClick={onPlaceOrder}
        >
          {submitting ? (
            <>
              <span className="spinner-small"></span>
              Placing Order...
            </>
          ) : (
            'Place Order'
          )}
        </button>
      )}
    </div>
  );
};

export default OrderSummary;