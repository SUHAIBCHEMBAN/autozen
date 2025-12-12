import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getWishlist, removeFromWishlist, clearWishlist } from '../services/wishlistService'
import { addToCart } from '../../cart/services/cartService'
import WishlistItem from '../components/WishlistItem'
import './Wishlist.css'

function Wishlist() {
  const [wishlist, setWishlist] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [updatingItem, setUpdatingItem] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadWishlist()
  }, [])

  const loadWishlist = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await getWishlist()
      setWishlist(data)
    } catch (err) {
      setError(err.message || 'Failed to load wishlist')
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (productId) => {
    try {
      setUpdatingItem(productId)
      await removeFromWishlist(productId)
      await loadWishlist() // Reload wishlist to get updated data
    } catch (err) {
      alert(err.message || 'Failed to remove item')
    } finally {
      setUpdatingItem(null)
    }
  }

  const handleAddToCart = async (productId) => {
    try {
      setUpdatingItem(productId)
      await addToCart(productId, 1)
      alert('Product added to cart!')
      // Optionally remove from wishlist after adding to cart
      // await removeFromWishlist(productId)
      // await loadWishlist()
    } catch (err) {
      alert(err.message || 'Failed to add to cart')
    } finally {
      setUpdatingItem(null)
    }
  }

  const handleClearWishlist = async () => {
    if (!window.confirm('Are you sure you want to clear your entire wishlist?')) {
      return
    }

    try {
      setLoading(true)
      await clearWishlist()
      await loadWishlist()
    } catch (err) {
      alert(err.message || 'Failed to clear wishlist')
    } finally {
      setLoading(false)
    }
  }

  if (loading && !wishlist) {
    return (
      <div className="wishlist-page">
        <div className="wishlist-container">
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading wishlist...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error && !wishlist) {
    return (
      <div className="wishlist-page">
        <div className="wishlist-container">
          <div className="error-state">
            <p>{error}</p>
            <button onClick={loadWishlist} className="btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  const items = wishlist?.items || []
  const isEmpty = items.length === 0

  return (
    <div className="wishlist-page">
      <div className="wishlist-container">
        <div className="wishlist-header">
          <h1>My Wishlist</h1>
          {!isEmpty && (
            <button onClick={handleClearWishlist} className="btn-clear-wishlist" disabled={loading}>
              Clear Wishlist
            </button>
          )}
        </div>

        {isEmpty ? (
          <div className="wishlist-empty">
            <div className="empty-icon">❤️</div>
            <h2>Your wishlist is empty</h2>
            <p>Save items you love for later by adding them to your wishlist.</p>
            <Link to="/products" className="btn-primary">
              Browse Products
            </Link>
          </div>
        ) : (
          <div className="wishlist-content">
            <div className="wishlist-info">
              <p className="items-count">
                {items.length} {items.length === 1 ? 'item' : 'items'} in your wishlist
              </p>
            </div>
            <div className="wishlist-items">
              {items.map((item) => (
                <WishlistItem
                  key={item.id}
                  item={item}
                  onRemove={handleRemove}
                  onAddToCart={handleAddToCart}
                  loading={updatingItem === item.product.id}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Wishlist