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
  const [selectedItems, setSelectedItems] = useState(new Set())
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
      // Select all items by default
      const allItemIds = new Set(data.items.map(item => item.product.id))
      setSelectedItems(allItemIds)
    } catch (err) {
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
      setSelectedItems(new Set())
    } catch (err) {
      alert(err.message || 'Failed to clear cart')
    } finally {
      setLoading(false)
    }
  }

  const handleSelectItem = (productId, isSelected) => {
    const newSelected = new Set(selectedItems)
    if (isSelected) {
      newSelected.add(productId)
    } else {
      newSelected.delete(productId)
    }
    setSelectedItems(newSelected)
  }

  const handleCheckout = () => {
    if (selectedItems.size === 0) {
      alert('Please select at least one item to checkout')
      return
    }
    
    // Filter cart items based on selection
    const checkoutItems = cart.items.filter(item => selectedItems.has(item.product.id))
    navigate('/checkout', { state: { selectedItems: checkoutItems } })
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

  // Calculate selected totals
  const selectedCartItems = items.filter(item => selectedItems.has(item.product.id))
  const selectedSubtotal = selectedCartItems.reduce((sum, item) => sum + parseFloat(item.total_price), 0)
  const selectedQuantity = selectedCartItems.reduce((sum, item) => sum + item.quantity, 0)

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
                  isSelected={selectedItems.has(item.product.id)}
                  onSelect={handleSelectItem}
                />
              ))}
            </div>

            <aside className="cart-summary">
              <div className="summary-card">
                <h2>Order Summary</h2>
                <div className="summary-row">
                  <span>Items ({selectedQuantity})</span>
                  <span>₹{selectedSubtotal.toFixed(2)}</span>
                </div>
                <div className="summary-divider"></div>
                <div className="summary-row summary-total">
                  <span>Total</span>
                  <span>₹{selectedSubtotal.toFixed(2)}</span>
                </div>
                <button 
                  className="btn-checkout" 
                  onClick={handleCheckout}
                  disabled={loading || selectedItems.size === 0}
                >
                  Proceed to Checkout ({selectedItems.size})
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