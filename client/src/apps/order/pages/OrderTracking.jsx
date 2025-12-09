import { useState } from 'react'
import { trackOrder } from '../services/orderService'
import './OrderTracking.css'

function OrderTracking() {
  const [orderNumber, setOrderNumber] = useState('')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [order, setOrder] = useState(null)

  const handleTrack = async (e) => {
    e.preventDefault()
    if (!orderNumber.trim()) {
      setError('Please enter an order number')
      return
    }

    try {
      setLoading(true)
      setError('')
      setOrder(null)
      const data = await trackOrder(orderNumber, email)
      setOrder(data)
    } catch (err) {
      setError(err.message || 'Failed to find order')
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'status-success'
      case 'shipped': return 'status-info'
      case 'processing': return 'status-warning'
      case 'cancelled': return 'status-danger'
      default: return 'status-default'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="order-tracking-page">
      <div className="tracking-container">
        <h1>Track Your Order</h1>
        <p className="tracking-subtitle">Enter your order ID to see the current status of your order.</p>

        <form onSubmit={handleTrack} className="tracking-form">
          <div className="form-group">
            <label htmlFor="orderNumber">Order ID *</label>
            <input
              type="text"
              id="orderNumber"
              value={orderNumber}
              onChange={(e) => setOrderNumber(e.target.value)}
              placeholder="e.g. ORD-12345678"
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email Address (Optional)</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter email for verification"
            />
          </div>

          <button type="submit" className="btn-track" disabled={loading}>
            {loading ? 'Tracking...' : 'Track Order'}
          </button>
        </form>

        {error && (
          <div className="tracking-error">
            <p>{error}</p>
          </div>
        )}

        {order && (
          <div className="tracking-result">
            <div className="result-header">
              <div className="result-info">
                <h3>Order #{order.order_number}</h3>
                <span className="order-date">Placed on {formatDate(order.created_at)}</span>
              </div>
              <span className={`order-status ${getStatusColor(order.status)}`}>
                {order.status.replace(/_/g, ' ')}
              </span>
            </div>

            <div className="order-progress">
              <div className={`progress-step ${['pending', 'confirmed', 'processing', 'shipped', 'delivered'].includes(order.status) ? 'active' : ''}`}>
                <div className="step-icon">✓</div>
                <span>Ordered</span>
              </div>
              <div className={`progress-step ${['processing', 'shipped', 'delivered'].includes(order.status) ? 'active' : ''}`}>
                <div className="step-icon">⚙</div>
                <span>Processing</span>
              </div>
              <div className={`progress-step ${['shipped', 'delivered'].includes(order.status) ? 'active' : ''}`}>
                <div className="step-icon">🚚</div>
                <span>Shipped</span>
              </div>
              <div className={`progress-step ${order.status === 'delivered' ? 'active' : ''}`}>
                <div className="step-icon">🏠</div>
                <span>Delivered</span>
              </div>
            </div>

            <div className="result-details">
              <div className="detail-section">
                <h4>Shipping Address</h4>
                <p>{order.shipping_address_line1}</p>
                {order.shipping_address_line2 && <p>{order.shipping_address_line2}</p>}
                <p>{order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}</p>
                <p>{order.shipping_country}</p>
              </div>
              
              <div className="detail-section">
                <h4>Order Summary</h4>
                <div className="summary-row">
                  <span>Subtotal</span>
                  <span>₹{parseFloat(order.subtotal).toFixed(2)}</span>
                </div>
                <div className="summary-row">
                  <span>Shipping</span>
                  <span>₹{parseFloat(order.shipping_cost).toFixed(2)}</span>
                </div>
                <div className="summary-row">
                  <span>Tax</span>
                  <span>₹{parseFloat(order.tax_amount).toFixed(2)}</span>
                </div>
                <div className="summary-row total">
                  <span>Total</span>
                  <span>₹{parseFloat(order.total_amount).toFixed(2)}</span>
                </div>
              </div>
            </div>
            
            <div className="order-items-list">
              <h4>Items</h4>
              {order.items.map((item, index) => (
                <div key={index} className="order-item">
                  <span>{item.product_name} x {item.quantity}</span>
                  <span>₹{parseFloat(item.total_price).toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default OrderTracking
