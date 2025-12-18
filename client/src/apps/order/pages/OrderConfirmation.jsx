import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getOrderByNumber } from '../services/orderService'
import { OrderSummary, AddressCard, OrderItem, StatusBadge } from '../components'
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
      setError(err.message || 'Failed to load order details')
    } finally {
      setLoading(false)
    }
  }

  // Calculate order totals for the OrderSummary component
  const calculateTotals = (order) => {
    if (!order) return { subtotal: 0, taxAmount: 0, shippingCost: 0, totalAmount: 0 };
    
    return {
      subtotal: parseFloat(order.subtotal),
      taxAmount: parseFloat(order.tax_amount),
      shippingCost: parseFloat(order.shipping_cost),
      totalAmount: parseFloat(order.total_amount),
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

  const totals = calculateTotals(order)

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
              <span className="info-value">
                <StatusBadge status={order.status} />
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
                <OrderItem key={item.id} item={item} />
              ))}
            </div>
          </div>

          <div className="order-addresses">
            <AddressCard 
              title="Billing Address"
              address={{
                first_name: order.first_name,
                last_name: order.last_name,
                address_line1: order.billing_address_line1,
                address_line2: order.billing_address_line2,
                city: order.billing_city,
                state: order.billing_state,
                postal_code: order.billing_postal_code,
                country: order.billing_country,
                phone_number: order.phone_number
              }}
            />
            
            <AddressCard 
              title="Shipping Address"
              address={{
                first_name: order.first_name,
                last_name: order.last_name,
                address_line1: order.shipping_address_line1,
                address_line2: order.shipping_address_line2,
                city: order.shipping_city,
                state: order.shipping_state,
                postal_code: order.shipping_postal_code,
                country: order.shipping_country
              }}
            />
          </div>

          <div className="order-summary-card">
            <h2>Order Summary</h2>
            <OrderSummary 
              items={order.items || []}
              totals={totals}
              showButton={false}
            />
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