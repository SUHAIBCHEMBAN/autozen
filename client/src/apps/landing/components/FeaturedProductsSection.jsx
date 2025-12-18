import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import './FeaturedProductsSection.css'

const FeaturedProductsSection = ({ products }) => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const intervalRef = useRef(null)

  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-product.png'

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

  // Create extended array for infinite loop effect
  const getExtendedProducts = () => {
    if (!products || products.length === 0) return []
    
    // If we have 4 or fewer products, duplicate them to enable sliding
    if (products.length <= 4) {
      return [...products, ...products, ...products]
    }
    
    // For more than 4 products, add copies at the end for seamless loop
    return [...products, ...products.slice(0, 4)]
  }

  const extendedProducts = getExtendedProducts()

  // Auto-slide functionality with infinite loop
  useEffect(() => {
    if (!products || products.length === 0) return

    intervalRef.current = setInterval(() => {
      setIsTransitioning(true)
      setCurrentIndex(prevIndex => prevIndex + 1)
    }, 4000) // Slide every 4 seconds

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [products])

  // Handle infinite loop reset
  useEffect(() => {
    if (!isTransitioning) return

    const timer = setTimeout(() => {
      // If we've reached the duplicated section, reset to the beginning without transition
      if (currentIndex >= products.length) {
        setIsTransitioning(false)
        setCurrentIndex(0)
      }
    }, 500) // Match the transition duration

    return () => clearTimeout(timer)
  }, [currentIndex, isTransitioning, products])

  if (!products || products.length === 0) {
    return (
      <section className="featured-products-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title no-underline">Featured Products</h2>
          </div>
          <p>No featured products available</p>
        </div>
      </section>
    )
  }

  return (
    <section className="featured-products-section">
      {/* <div className="container"> */}
        <div className="section-header">
          <h2 className="section-title no-underline">Featured Products</h2>
        </div>

        <div className="products-carousel-wrapper">
          <div className="products-carousel">
            <div 
              className="products-carousel-track"
              style={{
                transform: `translateX(-${currentIndex * 25}%)`,
                transition: isTransitioning ? 'transform 0.5s ease-in-out' : 'none'
              }}
            >
              {extendedProducts.map((product, index) => {
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
                  category_name
                } = product

                const imageUrl = getImageUrl(featured_image)

                return (
                  <div key={`product-${index}`} className="product-card-carousel-item">
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
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      {/* </div> */}
    </section>
  )
}

export default FeaturedProductsSection