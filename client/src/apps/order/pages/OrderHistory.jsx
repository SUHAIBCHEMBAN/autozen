import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getOrderHistory, cancelOrder, downloadInvoice } from '../services/orderService'
import './OrderHistory.css'

function OrderHistory() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [cancellingId, setCancellingId] = useState(null)
  const [downloadingId, setDownloadingId] = useState(null)

  useEffect(() => {
    fetchOrders()
  }, [])

  const fetchOrders = async () => {
    try {
      setLoading(true)
      const data = await getOrderHistory()
      setOrders(data)
    } catch (err) {
      setError(err.message || 'Failed to load order history')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (orderId, orderNumber) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) {
      return
    }

    try {
      setCancellingId(orderId)
      await cancelOrder(orderId) // Using ID for endpoint which usually expects ID
      // Refresh list
      await fetchOrders()
      alert(`Order ${orderNumber} cancelled successfully`)
    } catch (err) {
      alert(err.message || 'Failed to cancel order')
    } finally {
      setCancellingId(null)
    }
  }

  const handleViewInvoice = (orderNumber) => {
    try {
      setDownloadingId(orderNumber)
      // Open invoice URL directly in a new tab
      const invoiceUrl = `http://localhost:8000/api/orders/orders/${orderNumber}/invoice/`
      window.open(invoiceUrl, '_blank')
    } catch (err) {
      alert(err.message || 'Failed to open invoice')
    } finally {
      setDownloadingId(null)
    }
  }

  const getImageUrl = (image) => {
    if (!image) return '/placeholder-product.png'
    if (image.startsWith('http')) return image
    return `http://localhost:8000${image}`
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
      day: 'numeric'
    })
  }

  if (loading && orders.length === 0) {
    return (
      <div className="order-history-page">
        <div className="history-container">
          <div className="loading-spinner">Loading your orders...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="order-history-page">
      <div className="history-container">
        <div className="history-header">
          <h1>My Orders</h1>
        </div>

        {error && <div className="error-message">{error}</div>}

        {orders.length === 0 ? (
          <div className="empty-history">
            <div className="empty-icon">📦</div>
            <h2>No orders yet</h2>
            <p>You haven't placed any orders yet. Start shopping to fill your history!</p>
            <Link to="/products" className="btn-primary">Start Shopping</Link>
          </div>
        ) : (
          <div className="orders-list">
            {orders.map((order) => (
              <div key={order.id} className="order-card">
                <div className="order-card-header">
                  <div className="order-info">
                    <span className="order-number">#{order.order_number}</span>
                    <span className="order-date">{formatDate(order.created_at)}</span>
                  </div>
                  <span className={`order-status ${getStatusColor(order.status)}`}>
                    {order.status.replace(/_/g, ' ')}
                  </span>
                </div>

                <div className="order-card-body">
                  <div className="order-summary">
                    <div className="summary-item">
                      <span className="label">Total Amount</span>
                      <span className="value">₹{parseFloat(order.total_amount).toFixed(2)}</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Items</span>
                      <span className="value">
                        {order.items.length} item(s)
                      </span>
                    </div>
                  </div>

                  <div className="order-items-preview">
                    {order.items.slice(0, 3).map((item, idx) => (
                      <div key={idx} className="preview-item">
                        <img 
                          src={getImageUrl(item.product_image)} 
                          alt={item.product_name}
                          className="preview-image"
                          onError={(e) => { e.target.src = '/placeholder-product.png' }}
                        />
                        <span className="item-name">
                          {item.quantity}x {item.product_name}
                        </span>
                      </div>
                    ))}
                    {order.items.length > 3 && (
                      <span className="item-more">+{order.items.length - 3} more items</span>
                    )}
                  </div>
                </div>

                <div className="order-card-footer">
                  <Link to={`/track`} state={{ orderNumber: order.order_number }} className="btn-details">
                    Track / Details
                  </Link>
                  <button 
                    onClick={() => handleViewInvoice(order.order_number)} 
                    className="btn-invoice"
                    disabled={downloadingId === order.order_number}
                  >
                    {downloadingId === order.order_number ? 'Loading...' : 'View Invoice'}
                  </button>
                  {order.can_be_cancelled && (
                    <button 
                      onClick={() => handleCancel(order.id, order.order_number)} 
                      className="btn-cancel"
                      disabled={cancellingId === order.id}
                    >
                      {cancellingId === order.id ? 'Cancelling...' : 'Cancel Order'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default OrderHistory
