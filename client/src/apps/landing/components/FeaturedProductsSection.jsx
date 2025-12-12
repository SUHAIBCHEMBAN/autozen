import { Link } from 'react-router-dom'

const FeaturedProductsSection = ({ products }) => {
  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-product.png'
    
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

  if (!products || products.length === 0) {
    return null
  }

  return (
    <section className="featured-products-section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Featured Products</h2>
          <Link to="/products" className="btn btn-secondary">
            View All Products
          </Link>
        </div>
        <div className="products-grid">
          {products.map((product) => (
            <div key={product.id} className="product-card">
              <Link to={`/products/${product.slug}`} className="product-link">
                <div className="product-image">
                  {product.featured_image ? (
                    <img 
                      src={getImageUrl(product.featured_image)} 
                      alt={product.name}
                      onError={(e) => { e.target.src = '/placeholder-product.png' }}
                    />
                  ) : (
                    <div className="product-placeholder">
                      <span>No Image</span>
                    </div>
                  )}
                </div>
                <div className="product-info">
                  <h3 className="product-name">{product.name}</h3>
                  <p className="product-price">₹{product.price}</p>
                </div>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default FeaturedProductsSection