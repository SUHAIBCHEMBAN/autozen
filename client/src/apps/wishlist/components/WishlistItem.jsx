import { Link } from 'react-router-dom'
import './WishlistItem.css'

function WishlistItem({ item, onRemove, onAddToCart, loading }) {
  const { product } = item

  const getImageUrl = (image) => {
    if (!image) return null
    if (image.startsWith('http://') || image.startsWith('https://')) {
      return image
    }
    if (image.startsWith('/media/')) {
      return `http://localhost:8000${image}`
    }
    if (!image.startsWith('/')) {
      return `http://localhost:8000/media/${image}`
    }
    return `http://localhost:8000${image}`
  }

  const imageUrl = getImageUrl(product.featured_image) || '/placeholder-product.png'

  const handleRemove = () => {
    if (window.confirm('Are you sure you want to remove this item from your wishlist?')) {
      onRemove(product.id)
    }
  }

  const handleAddToCart = () => {
    onAddToCart(product.id)
  }

  return (
    <div className="wishlist-item">
      <Link to={`/products/${product.slug}`} className="wishlist-item__image-link">
        <img
          src={imageUrl}
          alt={product.name}
          className="wishlist-item__image"
          loading="lazy"
          onError={(e) => {
            if (e.target.src !== '/placeholder-product.png') {
              e.target.src = '/placeholder-product.png'
            }
          }}
        />
        {product.discount_percentage > 0 && (
          <span className="wishlist-item__badge">-{product.discount_percentage}%</span>
        )}
      </Link>

      <div className="wishlist-item__details">
        <Link to={`/products/${product.slug}`} className="wishlist-item__name">
          {product.name}
        </Link>
        {product.short_description && (
          <p className="wishlist-item__description">{product.short_description}</p>
        )}
        <div className="wishlist-item__meta">
          {product.brand_name && (
            <span className="wishlist-item__brand">{product.brand_name}</span>
          )}
          {product.model_name && (
            <span className="wishlist-item__model">{product.model_name}</span>
          )}
        </div>
        {product.sku && (
          <p className="wishlist-item__sku">SKU: {product.sku}</p>
        )}
      </div>

      <div className="wishlist-item__pricing">
        <span className="wishlist-item__price">₹{parseFloat(product.price).toFixed(2)}</span>
        {product.compare_price && product.compare_price > product.price && (
          <>
            <span className="wishlist-item__compare-price">₹{parseFloat(product.compare_price).toFixed(2)}</span>
            {product.amount_saved > 0 && (
              <span className="wishlist-item__savings">Save ₹{parseFloat(product.amount_saved).toFixed(2)}</span>
            )}
          </>
        )}
      </div>

      <div className="wishlist-item__stock">
        {product.is_in_stock ? (
          <span className="stock-badge stock-badge--in">In Stock</span>
        ) : (
          <span className="stock-badge stock-badge--out">Out of Stock</span>
        )}
      </div>

      <div className="wishlist-item__actions">
        {product.is_in_stock ? (
          <button
            className="btn-add-to-cart"
            onClick={handleAddToCart}
            disabled={loading}
          >
            Add to Cart
          </button>
        ) : (
          <button className="btn-add-to-cart btn-disabled" disabled>
            Out of Stock
          </button>
        )}
        <button
          className="btn-remove"
          onClick={handleRemove}
          disabled={loading}
          title="Remove from wishlist"
        >
          Remove
        </button>
      </div>
    </div>
  )
}

export default WishlistItem

