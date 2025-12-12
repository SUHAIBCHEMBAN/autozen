const TestimonialsSection = ({ testimonials }) => {
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

  return (
    <section className="testimonials-section">
      <div className="container">
        <h2 className="section-title">What Our Customers Say</h2>
        <div className="testimonials-slider">
          {testimonials.map((testimonial) => (
            <div key={testimonial.id} className="testimonial-card">
              <div className="testimonial-content">
                <p className="testimonial-text">"{testimonial.content}"</p>
                <div className="testimonial-author">
                  {testimonial.avatar && (
                    <img 
                      src={getImageUrl(testimonial.avatar)} 
                      alt={testimonial.name}
                      className="author-avatar"
                      onError={(e) => { e.target.src = '/placeholder-avatar.png' }}
                    />
                  )}
                  <div className="author-info">
                    <h4 className="author-name">{testimonial.name}</h4>
                    {testimonial.role && (
                      <p className="author-role">
                        {testimonial.role}
                        {testimonial.company && `, ${testimonial.company}`}
                      </p>
                    )}
                  </div>
                </div>
                <div className="testimonial-rating">
                  {[...Array(5)].map((_, i) => (
                    <span 
                      key={i} 
                      className={`star ${i < testimonial.rating ? 'filled' : ''}`}
                    >
                      ★
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default TestimonialsSection