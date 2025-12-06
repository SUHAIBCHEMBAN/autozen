import { Link } from 'react-router-dom'
import { useState } from 'react'
import './CartItem.css'

function CartItem({ item, onUpdateQuantity, onRemove, loading }) {
  const { product, quantity, price, total_price } = item

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

  const handleQuantityChange = (delta) => {
    const newQuantity = quantity + delta
    if (newQuantity >= 1 && newQuantity <= product.stock_quantity) {
      onUpdateQuantity(product.id, newQuantity)
    }
  }

  const handleRemove = () => {
    if (window.confirm('Are you sure you want to remove this item from your cart?')) {
      onRemove(product.id)
    }
  }

  return (
    <div className="cart-item">
      <Link to={`/products/${product.slug}`} className="cart-item__image-link">
        <img
          src={imageUrl}
          alt={product.name}
          className="cart-item__image"
          loading="lazy"
          onError={(e) => {
            if (e.target.src !== '/placeholder-product.png') {
              e.target.src = '/placeholder-product.png'
            }
          }}
        />
      </Link>

      <div className="cart-item__details">
        <Link to={`/products/${product.slug}`} className="cart-item__name">
          {product.name}
        </Link>
        {product.brand_name && (
          <p className="cart-item__brand">{product.brand_name}</p>
        )}
        {product.sku && (
          <p className="cart-item__sku">SKU: {product.sku}</p>
        )}
        {!product.is_in_stock && (
          <span className="cart-item__stock-warning">Out of Stock</span>
        )}
      </div>

      <div className="cart-item__quantity">
        <label htmlFor={`quantity-${item.id}`} className="quantity-label">Qty:</label>
        <div className="quantity-controls">
          <button
            type="button"
            className="quantity-btn"
            onClick={() => handleQuantityChange(-1)}
            disabled={loading || quantity <= 1}
          >
            −
          </button>
          <input
            type="number"
            id={`quantity-${item.id}`}
            min="1"
            max={product.stock_quantity}
            value={quantity}
            onChange={(e) => {
              const val = parseInt(e.target.value) || 1
              if (val >= 1 && val <= product.stock_quantity) {
                onUpdateQuantity(product.id, val)
              }
            }}
            className="quantity-input"
            disabled={loading}
          />
          <button
            type="button"
            className="quantity-btn"
            onClick={() => handleQuantityChange(1)}
            disabled={loading || quantity >= product.stock_quantity}
          >
            +
          </button>
        </div>
      </div>

      <div className="cart-item__pricing">
        <span className="cart-item__unit-price">₹{parseFloat(price).toFixed(2)}</span>
        <span className="cart-item__total-price">₹{parseFloat(total_price).toFixed(2)}</span>
      </div>

      <button
        className="cart-item__remove"
        onClick={handleRemove}
        disabled={loading}
        title="Remove item"
      >
        ×
      </button>
    </div>
  )
}

export default CartItem

