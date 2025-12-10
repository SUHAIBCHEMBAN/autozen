import { Link } from 'react-router-dom'
import { HeartIcon } from '../../../common/components/Icons'

function WishlistSection({ wishlistItems, wishlistLoading, wishlistError, fetchUserWishlist }) {
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-product.png'
    if (image.startsWith('http')) return image
    return `http://localhost:8000${image}`
  }

  return (
    <div className="profile-section">
      <div className="section-header">
        <h2>My Wishlist</h2>
      </div>
      
      {wishlistLoading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading wishlist...</p>
        </div>
      ) : wishlistError ? (
        <div className="error-state">
          <p>{wishlistError}</p>
          <button onClick={fetchUserWishlist} className="btn-primary">
            Try Again
          </button>
        </div>
      ) : wishlistItems.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon"><HeartIcon size={64} /></div>
          <h3>Your wishlist is empty</h3>
          <p>Save items you love for later.</p>
          <Link to="/products" className="btn-primary">
            Browse Products
          </Link>
        </div>
      ) : (
        <div className="wishlist-content">
          <div className="wishlist-items">
            {wishlistItems.slice(0, 3).map((item) => (
              <div key={item.id} className="wishlist-item">
                <Link to={`/products/${item.product.slug}`} className="wishlist-item__image-link">
                  <img
                    src={getImageUrl(item.product.featured_image) || '/placeholder-product.png'}
                    alt={item.product.name}
                    className="wishlist-item__image"
                    loading="lazy"
                    onError={(e) => {
                      if (e.target.src !== '/placeholder-product.png') {
                        e.target.src = '/placeholder-product.png'
                      }
                    }}
                  />
                  {item.product.discount_percentage > 0 && (
                    <span className="wishlist-item__badge">-{item.product.discount_percentage}%</span>
                  )}
                </Link>

                <div className="wishlist-item__details">
                  <Link to={`/products/${item.product.slug}`} className="wishlist-item__name">
                    {item.product.name}
                  </Link>
                  {item.product.short_description && (
                    <p className="wishlist-item__description">{item.product.short_description}</p>
                  )}
                  <div className="wishlist-item__meta">
                    {item.product.brand_name && (
                      <span className="wishlist-item__brand">{item.product.brand_name}</span>
                    )}
                  </div>
                </div>

                <div className="wishlist-item__pricing">
                  <span className="wishlist-item__price">₹{parseFloat(item.product.price).toFixed(2)}</span>
                  {item.product.compare_price && item.product.compare_price > item.product.price && (
                    <span className="wishlist-item__compare-price">₹{parseFloat(item.product.compare_price).toFixed(2)}</span>
                  )}
                </div>

                <div className="wishlist-item__stock">
                  {item.product.is_in_stock ? (
                    <span className="stock-badge stock-badge--in">In Stock</span>
                  ) : (
                    <span className="stock-badge stock-badge--out">Out of Stock</span>
                  )}
                </div>
              </div>
            ))}
            
            {wishlistItems.length > 3 && (
              <div className="wishlist-view-more">
                <span>+{wishlistItems.length - 3} more items in your wishlist</span>
              </div>
            )}
          </div>
          
          <div className="view-all-wishlist">
            <Link to="/wishlist" className="btn-secondary">
              View Full Wishlist
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default WishlistSection