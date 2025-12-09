import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getOrderByNumber } from '../services/orderService'
import './OrderConfirmation.css'

function OrderConfirmation() {
  const { orderNumber } = useParams()
  const navigate = useNavigate()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (orderNumber) {
      loadOrder()
    }
  }, [orderNumber])

  const loadOrder = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await getOrderByNumber(orderNumber)
      setOrder(data)
    } catch (err) {
      if (err.message.includes('401') || err.message.includes('Authentication')) {
        navigate('/login', { replace: true })
        return
      }
      setError(err.message || 'Failed to load order details')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="order-confirmation-page">
        <div className="order-confirmation-container">
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading order details...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !order) {
    return (
      <div className="order-confirmation-page">
        <div className="order-confirmation-container">
          <div className="error-state">
            <h2>Order Not Found</h2>
            <p>{error || 'The order you are looking for does not exist.'}</p>
            <div className="error-actions">
              <Link to="/profile" className="btn-primary">
                View My Orders
              </Link>
              <Link to="/products" className="btn-secondary">
                Continue Shopping
              </Link>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="order-confirmation-page">
      <div className="order-confirmation-container">
        <div className="confirmation-header">
          <div className="success-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          </div>
          <h1>Order Confirmed!</h1>
          <p className="confirmation-message">
            Thank you for your order. We've received your order and will begin processing it shortly.
          </p>
        </div>

        <div className="order-details">
          <div className="order-info-card">
            <h2>Order Information</h2>
            <div className="info-row">
              <span className="info-label">Order Number:</span>
              <span className="info-value">{order.order_number}</span>
            </div>
            <div className="info-row">
              <span className="info-label">Order Date:</span>
              <span className="info-value">
                {new Date(order.created_at).toLocaleDateString('en-IN', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">Status:</span>
              <span className={`status-badge status-${order.status}`}>
                {order.status.charAt(0).toUpperCase() + order.status.slice(1).replace('_', ' ')}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">Payment Method:</span>
              <span className="info-value">
                {order.payment_method === 'cash_on_delivery' ? 'Cash on Delivery' : 
                 order.payment_method === 'bank_transfer' ? 'Bank Transfer' : 
                 order.payment_method}
              </span>
            </div>
            <div className="info-row">
              <span className="info-label">Payment Status:</span>
              <span className={`payment-status ${order.payment_status ? 'paid' : 'pending'}`}>
                {order.payment_status ? 'Paid' : 'Pending'}
              </span>
            </div>
          </div>

          <div className="order-items-card">
            <h2>Order Items</h2>
            <div className="items-list">
              {order.items && order.items.map((item) => (
                <div key={item.id} className="order-item">
                  <div className="item-info">
                    <h3>{item.product_name}</h3>
                    <p className="item-sku">SKU: {item.product_sku}</p>
                    <p className="item-quantity">Quantity: {item.quantity}</p>
                  </div>
                  <div className="item-price">
                    ₹{parseFloat(item.total_price).toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="order-addresses">
            <div className="address-card">
              <h3>Billing Address</h3>
              <div className="address-content">
                <p>{order.first_name} {order.last_name}</p>
                <p>{order.billing_address_line1}</p>
                {order.billing_address_line2 && <p>{order.billing_address_line2}</p>}
                <p>
                  {order.billing_city}, {order.billing_state} {order.billing_postal_code}
                </p>
                <p>{order.billing_country}</p>
                <p>Phone: {order.phone_number}</p>
                <p>Email: {order.email}</p>
              </div>
            </div>

            <div className="address-card">
              <h3>Shipping Address</h3>
              <div className="address-content">
                <p>{order.first_name} {order.last_name}</p>
                <p>{order.shipping_address_line1}</p>
                {order.shipping_address_line2 && <p>{order.shipping_address_line2}</p>}
                <p>
                  {order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}
                </p>
                <p>{order.shipping_country}</p>
              </div>
            </div>
          </div>

          <div className="order-summary-card">
            <h2>Order Summary</h2>
            <div className="summary-row">
              <span>Subtotal</span>
              <span>₹{parseFloat(order.subtotal).toFixed(2)}</span>
            </div>
            <div className="summary-row">
              <span>VAT (12%)</span>
              <span>₹{parseFloat(order.tax_amount).toFixed(2)}</span>
            </div>
            <div className="summary-row">
              <span>Shipping</span>
              <span>₹{parseFloat(order.shipping_cost).toFixed(2)}</span>
            </div>
            {order.discount_amount > 0 && (
              <div className="summary-row">
                <span>Discount</span>
                <span>-₹{parseFloat(order.discount_amount).toFixed(2)}</span>
              </div>
            )}
            <div className="summary-divider"></div>
            <div className="summary-row summary-total">
              <span>Total</span>
              <span>₹{parseFloat(order.total_amount).toFixed(2)}</span>
            </div>
          </div>

          {order.payment_method === 'bank_transfer' && (
            <div className="payment-instructions">
              <h3>Bank Transfer Instructions</h3>
              <p>Please transfer the amount of <strong>₹{parseFloat(order.total_amount).toFixed(2)}</strong> to:</p>
              <div className="bank-details">
                <p><strong>Account Name:</strong> AutoZen</p>
                <p><strong>Account Number:</strong> [Your Bank Account Number]</p>
                <p><strong>IFSC Code:</strong> [Your IFSC Code]</p>
                <p><strong>Bank Name:</strong> [Your Bank Name]</p>
              </div>
              <p className="payment-note">
                Please include your order number ({order.order_number}) in the transfer reference.
              </p>
            </div>
          )}

          {order.notes && (
            <div className="order-notes">
              <h3>Order Notes</h3>
              <p>{order.notes}</p>
            </div>
          )}
        </div>

        <div className="confirmation-actions">
          <Link to="/profile" className="btn-primary">
            View My Orders
          </Link>
          <Link to="/products" className="btn-secondary">
            Continue Shopping
          </Link>
        </div>
      </div>
    </div>
  )
}

export default OrderConfirmation


