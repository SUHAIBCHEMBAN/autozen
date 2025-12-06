import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { getProductBySlug } from '../services/productsService'
import { addToCart } from '../../cart/services/cartService'
import { addToWishlist, removeFromWishlist, isInWishlist } from '../../wishlist/services/wishlistService'
import './ProductDetail.css'

function ProductDetail() {
  const { slug } = useParams()
  const navigate = useNavigate()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedImage, setSelectedImage] = useState(0)
  const [quantity, setQuantity] = useState(1)
  const [isWishlisted, setIsWishlisted] = useState(false)
  const [cartLoading, setCartLoading] = useState(false)
  const [wishlistLoading, setWishlistLoading] = useState(false)

  useEffect(() => {
    loadProduct()
  }, [slug])

  useEffect(() => {
    // Check if product is in wishlist when product loads
    if (product) {
      checkWishlistStatus()
    }
  }, [product])

  const loadProduct = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await getProductBySlug(slug)
      setProduct(data)
      setSelectedImage(0)
    } catch (err) {
      setError(err.message || 'Product not found')
    } finally {
      setLoading(false)
    }
  }

  const handleQuantityChange = (delta) => {
    setQuantity((prev) => {
      const newQuantity = prev + delta
      if (newQuantity < 1) return 1
      if (product && newQuantity > product.stock_quantity) return prev
      return newQuantity
    })
  }

  const checkWishlistStatus = async () => {
    try {
      const inWishlist = await isInWishlist(product.id)
      setIsWishlisted(inWishlist)
    } catch (error) {
      // Silently fail - user might not be logged in
      setIsWishlisted(false)
    }
  }

  const handleAddToCart = async () => {
    try {
      setCartLoading(true)
      await addToCart(product.id, quantity)
      alert('Product added to cart!')
    } catch (err) {
      if (err.message.includes('401') || err.message.includes('Authentication')) {
        navigate('/login', { state: { returnTo: `/products/${slug}` } })
      } else {
        alert(err.message || 'Failed to add to cart')
      }
    } finally {
      setCartLoading(false)
    }
  }

  const handleAddToWishlist = async () => {
    try {
      setWishlistLoading(true)
      if (isWishlisted) {
        await removeFromWishlist(product.id)
        setIsWishlisted(false)
        alert('Product removed from wishlist')
      } else {
        await addToWishlist(product.id)
        setIsWishlisted(true)
        alert('Product added to wishlist!')
      }
    } catch (err) {
      if (err.message.includes('401') || err.message.includes('Authentication')) {
        navigate('/login', { state: { returnTo: `/products/${slug}` } })
      } else {
        alert(err.message || 'Failed to update wishlist')
      }
    } finally {
      setWishlistLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="product-detail-page">
        <div className="product-detail-container">
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading product...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !product) {
    return (
      <div className="product-detail-page">
        <div className="product-detail-container">
          <div className="error-state">
            <p>{error || 'Product not found'}</p>
            <button onClick={() => navigate('/products')} className="btn-primary">
              Back to Products
            </button>
          </div>
        </div>
      </div>
    )
  }

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

  const imageUrl = getImageUrl(product.featured_image) || '/placeholder-product.png'

  const breadcrumbs = [
    { label: 'Home', path: '/' },
    { label: 'Products', path: '/products' },
    { label: product.brand_name || 'Product', path: `/products?brand=${product.brand}` },
    { label: product.name, path: null },
  ]

  return (
    <div className="product-detail-page">
      <div className="product-detail-container">
        {/* Breadcrumbs */}
        <nav className="breadcrumbs">
          {breadcrumbs.map((crumb, index) => (
            <span key={index} className="breadcrumb-item">
              {crumb.path ? (
                <Link to={crumb.path}>{crumb.label}</Link>
              ) : (
                <span>{crumb.label}</span>
              )}
              {index < breadcrumbs.length - 1 && <span className="breadcrumb-separator">/</span>}
            </span>
          ))}
        </nav>

        <div className="product-detail-content">
          {/* Product Images */}
          <div className="product-images">
            <div className="product-main-image">
              <img
                src={imageUrl}
                alt={product.name}
                loading="lazy"
                onError={(e) => {
                  // Prevent infinite loop if placeholder also fails
                  if (e.target.src !== '/placeholder-product.png' && !e.target.src.includes('placeholder')) {
                    e.target.src = '/placeholder-product.png'
                  }
                }}
              />
              {product.discount_percentage > 0 && (
                <span className="product-badge">-{product.discount_percentage}%</span>
              )}
            </div>
          </div>

          {/* Product Info */}
          <div className="product-info">
            <div className="product-meta">
              {product.brand_name && (
                <Link to={`/products?brand=${product.brand}`} className="product-brand">
                  {product.brand_name}
                </Link>
              )}
              {product.model_name && (
                <span className="product-model">{product.model_name}</span>
              )}
            </div>

            <h1 className="product-title">{product.name}</h1>

            {product.short_description && (
              <p className="product-short-description">{product.short_description}</p>
            )}

            <div className="product-pricing">
              <span className="product-price">₹{parseFloat(product.price).toFixed(2)}</span>
              {product.compare_price && product.compare_price > product.price && (
                <>
                  <span className="product-compare-price">₹{parseFloat(product.compare_price).toFixed(2)}</span>
                  {product.amount_saved > 0 && (
                    <span className="product-savings">
                      You save ₹{parseFloat(product.amount_saved).toFixed(2)}
                    </span>
                  )}
                </>
              )}
            </div>

            <div className="product-stock-info">
              {product.is_in_stock ? (
                <span className="stock-badge stock-badge--in">
                  ✓ In Stock ({product.stock_quantity} available)
                </span>
              ) : (
                <span className="stock-badge stock-badge--out">Out of Stock</span>
              )}
            </div>

            {product.sku && (
              <div className="product-sku">
                <span className="sku-label">SKU:</span>
                <span className="sku-value">{product.sku}</span>
              </div>
            )}

            {product.category_name && (
              <div className="product-category">
                <span className="category-label">Category:</span>
                <Link to={`/products?part_category=${product.part_category}`} className="category-value">
                  {product.category_name}
                </Link>
              </div>
            )}

            {/* Quantity Selector */}
            {product.is_in_stock && (
              <div className="quantity-selector">
                <label htmlFor="quantity">Quantity:</label>
                <div className="quantity-controls">
                  <button
                    type="button"
                    className="quantity-btn"
                    onClick={() => handleQuantityChange(-1)}
                    disabled={quantity <= 1}
                  >
                    −
                  </button>
                  <input
                    type="number"
                    id="quantity"
                    min="1"
                    max={product.stock_quantity}
                    value={quantity}
                    onChange={(e) => {
                      const val = parseInt(e.target.value) || 1
                      if (val >= 1 && val <= product.stock_quantity) {
                        setQuantity(val)
                      }
                    }}
                    className="quantity-input"
                  />
                  <button
                    type="button"
                    className="quantity-btn"
                    onClick={() => handleQuantityChange(1)}
                    disabled={quantity >= product.stock_quantity}
                  >
                    +
                  </button>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="product-actions">
              {product.is_in_stock ? (
                <button
                  className="btn-add-to-cart"
                  onClick={handleAddToCart}
                  disabled={quantity < 1 || cartLoading}
                >
                  {cartLoading ? 'Adding...' : 'Add to Cart'}
                </button>
              ) : (
                <button className="btn-add-to-cart btn-disabled" disabled>
                  Out of Stock
                </button>
              )}

              <button
                className={`btn-add-to-wishlist ${isWishlisted ? 'btn-wishlisted' : ''}`}
                onClick={handleAddToWishlist}
                disabled={wishlistLoading}
                title={isWishlisted ? 'Remove from Wishlist' : 'Add to Wishlist'}
              >
                <span className="btn-icon">{isWishlisted ? '❤️' : '🤍'}</span>
                {wishlistLoading ? 'Updating...' : isWishlisted ? 'Remove from Wishlist' : 'Add to Wishlist'}
              </button>
            </div>

            {/* Product Description */}
            {product.description && (
              <div className="product-description">
                <h2>Description</h2>
                <div className="description-content">
                  {product.description.split('\n').map((para, index) => (
                    <p key={index}>{para}</p>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProductDetail

