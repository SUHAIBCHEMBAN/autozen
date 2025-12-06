import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getCart, updateCartItem, removeFromCart, clearCart } from '../services/cartService'
import CartItem from '../components/CartItem'
import './Cart.css'

function Cart() {
  const [cart, setCart] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [updatingItem, setUpdatingItem] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadCart()
  }, [])

  const loadCart = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await getCart()
      setCart(data)
    } catch (err) {
      // Check if user is not authenticated
      if (err.message.includes('401') || err.message.includes('Authentication')) {
        navigate('/login', { replace: true })
        return
      }
      setError(err.message || 'Failed to load cart')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateQuantity = async (productId, quantity) => {
    try {
      setUpdatingItem(productId)
      await updateCartItem(productId, quantity)
      await loadCart() // Reload cart to get updated data
    } catch (err) {
      alert(err.message || 'Failed to update quantity')
    } finally {
      setUpdatingItem(null)
    }
  }

  const handleRemove = async (productId) => {
    try {
      setUpdatingItem(productId)
      await removeFromCart(productId)
      await loadCart() // Reload cart to get updated data
    } catch (err) {
      alert(err.message || 'Failed to remove item')
    } finally {
      setUpdatingItem(null)
    }
  }

  const handleClearCart = async () => {
    if (!window.confirm('Are you sure you want to clear your entire cart?')) {
      return
    }

    try {
      setLoading(true)
      await clearCart()
      await loadCart()
    } catch (err) {
      alert(err.message || 'Failed to clear cart')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !cart) {
    return (
      <div className="cart-page">
        <div className="cart-container">
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading cart...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error && !cart) {
    return (
      <div className="cart-page">
        <div className="cart-container">
          <div className="error-state">
            <p>{error}</p>
            <button onClick={loadCart} className="btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  const items = cart?.items || []
  const isEmpty = items.length === 0

  return (
    <div className="cart-page">
      <div className="cart-container">
        <div className="cart-header">
          <h1>Shopping Cart</h1>
          {!isEmpty && (
            <button onClick={handleClearCart} className="btn-clear-cart" disabled={loading}>
              Clear Cart
            </button>
          )}
        </div>

        {isEmpty ? (
          <div className="cart-empty">
            <div className="empty-icon">🛒</div>
            <h2>Your cart is empty</h2>
            <p>Looks like you haven't added anything to your cart yet.</p>
            <Link to="/products" className="btn-primary">
              Start Shopping
            </Link>
          </div>
        ) : (
          <div className="cart-content">
            <div className="cart-items">
              {items.map((item) => (
                <CartItem
                  key={item.id}
                  item={item}
                  onUpdateQuantity={handleUpdateQuantity}
                  onRemove={handleRemove}
                  loading={updatingItem === item.product.id}
                />
              ))}
            </div>

            <aside className="cart-summary">
              <div className="summary-card">
                <h2>Order Summary</h2>
                <div className="summary-row">
                  <span>Items ({cart.total_quantity || items.length})</span>
                  <span>₹{parseFloat(cart.subtotal || 0).toFixed(2)}</span>
                </div>
                <div className="summary-divider"></div>
                <div className="summary-row summary-total">
                  <span>Total</span>
                  <span>₹{parseFloat(cart.subtotal || 0).toFixed(2)}</span>
                </div>
                <button className="btn-checkout" disabled={loading}>
                  Proceed to Checkout
                </button>
                <Link to="/products" className="btn-continue-shopping">
                  Continue Shopping
                </Link>
              </div>
            </aside>
          </div>
        )}
      </div>
    </div>
  )
}

export default Cart

