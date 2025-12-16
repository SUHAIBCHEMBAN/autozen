import { useState, useEffect } from 'react'

const TestimonialsSection = ({ testimonials }) => {
  const [currentIndex, setCurrentIndex] = useState(0)

  // Auto-slide functionality - show one testimonial at a time
  useEffect(() => {
    if (!testimonials || testimonials.length <= 1) return
    
    const interval = setInterval(() => {
      setCurrentIndex(prevIndex => (prevIndex + 1) % testimonials.length)
    }, 5000) // Slide every 5 seconds
    
    return () => clearInterval(interval)
  }, [testimonials])

  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-avatar.png'
    
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

  if (!testimonials || testimonials.length === 0) {
    return null
  }

  const currentTestimonial = testimonials[currentIndex]

  return (
    <section className="testimonials-section">
      <div className="container">
        <h2 className="section-title">What Our Customers Say</h2>
        <div className="testimonials-container">
          <div className="testimonial-card">
            <p className="testimonial-text">"{currentTestimonial.content}"</p>
            <div className="testimonial-author">
              {currentTestimonial.avatar && (
                <img 
                  src={getImageUrl(currentTestimonial.avatar)} 
                  alt={currentTestimonial.name}
                  className="author-avatar"
                  onError={(e) => { e.target.src = '/placeholder-avatar.png' }}
                />
              )}
              <div className="author-info">
                <h4 className="author-name">{currentTestimonial.name}</h4>
                {currentTestimonial.role && (
                  <p className="author-role">
                    {currentTestimonial.role}
                    {currentTestimonial.company && `, ${currentTestimonial.company}`}
                  </p>
                )}
              </div>
            </div>
            <div className="testimonial-rating">
              {[...Array(5)].map((_, i) => (
                <span 
                  key={i} 
                  className={`star ${i < currentTestimonial.rating ? 'filled' : ''}`}
                >
                  ★
                </span>
              ))}
            </div>
          </div>
          
          {/* Dots indicator */}
          {testimonials.length > 1 && (
            <div className="testimonial-dots">
              {testimonials.map((_, index) => (
                <span 
                  key={index}
                  className={`dot ${index === currentIndex ? 'active' : ''}`}
                  onClick={() => setCurrentIndex(index)}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}

export default TestimonialsSection