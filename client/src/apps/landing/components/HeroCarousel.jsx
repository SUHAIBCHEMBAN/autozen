import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const HeroCarousel = ({ banners }) => {
  const [currentSlide, setCurrentSlide] = useState(0)
  const [hoveredCard, setHoveredCard] = useState(null)

  // Auto-scroll functionality
  useEffect(() => {
    if (!banners || banners.length <= 1) return
    
    const interval = setInterval(() => {
      setCurrentSlide(prev => (prev + 1) % banners.length)
    }, 6000) // Change slide every 6 seconds
    
    return () => clearInterval(interval)
  }, [banners])

  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-banner.jpg'
    
    // If already a full URL, return as is
    if (image.startsWith('http://') || image.startsWith('https://')) {
      return image
    }
    
    // If starts with /media/, add base URL
    if (image.startsWith('/media/')) {
      return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${image}`
    }
    
    // If doesn't start with /, add /media/ prefix
    if (!image.startsWith('/')) {
      return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/media/${image}`
    }
    
    // Otherwise, add base URL
    return `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${image}`
  }

  if (!banners || banners.length === 0) {
    return null
  }

  const currentBanner = banners[currentSlide]

  return (
    <section className="modern-hero-section">
      <div className="hero-carousel-container">
        {/* Background Image with Slides */}
        <div className="hero-background-wrapper">
          {banners.map((banner, index) => (
            <div
              key={banner.id}
              className={`hero-background-slide ${index === currentSlide ? 'active' : ''}`}
              style={{
                backgroundImage: `url(${getImageUrl(banner.image || banner.background_image)})`,
              }}
            >
              <div className="hero-overlay"></div>
            </div>
          ))}
        </div>

        {/* Content Container */}
        <div className="hero-content-container">
          {/* Title and Description */}
          <div className="hero-text-content">
            <h3 className="hero-main-title">{currentBanner.title}</h3>
            {currentBanner.subtitle && (
              <p className="hero-main-subtitle">{currentBanner.subtitle}</p>
            )}
          </div>

          {/* Featured Vehicle Cards */}
          {currentBanner.featured_vehicles && currentBanner.featured_vehicles.length > 0 && (
            <div className="featured-vehicles-grid">
              {currentBanner.featured_vehicles.map((vehicle, index) => (
                <Link
                  key={vehicle.id}
                  to={vehicle.link || '/products'}
                  className="vehicle-card"
                  onMouseEnter={() => setHoveredCard(vehicle.id)}
                  onMouseLeave={() => setHoveredCard(null)}
                >
                  <div className="vehicle-card-inner">
                    <div className={`vehicle-image ${hoveredCard === vehicle.id ? 'blurred' : ''}`}>
                      <img 
                        src={getImageUrl(vehicle.image || vehicle.featured_image)} 
                        alt={vehicle.name || vehicle.title || 'Vehicle'}
                        onError={(e) => { e.target.src = '/placeholder-car.jpg' }}
                      />
                    </div>
                    
                    {/* Hover Content */}
                    <div className={`vehicle-hover-content ${hoveredCard === vehicle.id ? 'visible' : ''}`}>
                      <h3 className="vehicle-hover-title">
                        {vehicle.hover_title || vehicle.name || vehicle.title || 'Vehicle'}
                      </h3>
                      {vehicle.hover_description && (
                        <p className="vehicle-hover-description">
                          {vehicle.hover_description}
                        </p>
                      )}
                      <span className="vehicle-hover-link">View Details →</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Carousel Navigation Dots */}
        {banners.length > 1 && (
          <div className="carousel-navigation">
            {banners.map((_, index) => (
              <button
                key={index}
                className={`nav-dot ${index === currentSlide ? 'active' : ''}`}
                onClick={() => setCurrentSlide(index)}
                aria-label={`Go to slide ${index + 1}`}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

export default HeroCarousel