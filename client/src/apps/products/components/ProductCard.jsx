import { Link } from 'react-router-dom'
import './ProductCard.css'

function ProductCard({ product }) {
  const {
    id,
    name,
    slug,
    short_description,
    featured_image,
    price,
    compare_price,
    amount_saved,
    discount_percentage,
    is_in_stock,
    brand_name,
    model_name,
    category_name,
    url,
  } = product

  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return null
    
    // If already a full URL, return as is
    if (image.startsWith('http://') || image.startsWith('https://')) {
      return image
    }
    
    // If starts with /media/, add base URL
    if (image.startsWith('/media/')) {
      return `http://localhost:8000${image}`
    }
    
    // If doesn't start with /, add /media/ prefix
    if (!image.startsWith('/')) {
      return `http://localhost:8000/media/${image}`
    }
    
    // Otherwise, add base URL
    return `http://localhost:8000${image}`
  }

  const imageUrl = getImageUrl(featured_image) || '/placeholder-product.png'

  return (
    <div className="product-card">
      <Link to={`/products/${slug}`} className="product-card__link">
        <div className="product-card__image-wrapper">
          {discount_percentage > 0 && (
            <span className="product-card__badge">-{discount_percentage}%</span>
          )}
          {!is_in_stock && (
            <span className="product-card__badge product-card__badge--out-of-stock">
              Out of Stock
            </span>
          )}
          <img
            src={imageUrl}
            alt={name}
            className="product-card__image"
            loading="lazy"
            onError={(e) => {
              // Prevent infinite loop if placeholder also fails
              if (e.target.src !== '/placeholder-product.png' && !e.target.src.includes('placeholder')) {
                e.target.src = '/placeholder-product.png'
              }
            }}
          />
        </div>

        <div className="product-card__content">
          <div className="product-card__meta">
            {brand_name && <span className="product-card__brand">{brand_name}</span>}
            {model_name && <span className="product-card__model">{model_name}</span>}
          </div>

          <h3 className="product-card__title">{name}</h3>

          {short_description && (
            <p className="product-card__description">{short_description}</p>
          )}

          {category_name && (
            <span className="product-card__category">{category_name}</span>
          )}

          <div className="product-card__pricing">
            <span className="product-card__price">₹{parseFloat(price).toFixed(2)}</span>
            {compare_price && compare_price > price && (
              <>
                <span className="product-card__compare-price">₹{parseFloat(compare_price).toFixed(2)}</span>
                {amount_saved > 0 && (
                  <span className="product-card__savings">Save ₹{parseFloat(amount_saved).toFixed(2)}</span>
                )}
              </>
            )}
          </div>

          <div className="product-card__stock">
            {is_in_stock ? (
              <span className="product-card__stock--in">In Stock</span>
            ) : (
              <span className="product-card__stock--out">Out of Stock</span>
            )}
          </div>
        </div>
      </Link>
    </div>
  )
}

export default ProductCard

