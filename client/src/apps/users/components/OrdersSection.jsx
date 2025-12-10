import { Link } from 'react-router-dom'
import { PackageIcon } from '../../../common/components/Icons'

function OrdersSection({ orders, ordersLoading, ordersError, fetchUserOrders }) {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
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

  const getImageUrl = (image) => {
    if (!image) return '/placeholder-product.png'
    if (image.startsWith('http')) return image
    return `http://localhost:8000${image}`
  }

  return (
    <div className="profile-section">
      <div className="section-header">
        <h2>Recent Orders</h2>
      </div>
      
      {ordersLoading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading orders...</p>
        </div>
      ) : ordersError ? (
        <div className="error-state">
          <p>{ordersError}</p>
          <button onClick={fetchUserOrders} className="btn-primary">
            Try Again
          </button>
        </div>
      ) : orders.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon"><PackageIcon size={64} /></div>
          <h3>No orders yet</h3>
          <p>When you place an order, it will appear here.</p>
          <Link to="/products" className="btn-primary">
            Start Shopping
          </Link>
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
                  onClick={() => window.open(`http://localhost:8000/api/orders/orders/${order.order_number}/invoice/`, '_blank')} 
                  className="btn-invoice"
                >
                  View Invoice
                </button>
              </div>
            </div>
          ))}
          
          <div className="view-all-orders">
            <Link to="/orders/history" className="btn-secondary">
              View All Orders
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default OrdersSection