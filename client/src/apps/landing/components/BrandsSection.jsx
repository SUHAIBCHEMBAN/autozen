const BrandsSection = ({ brands }) => {
  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-brand.png'
    
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

  if (!brands || brands.length === 0) {
    return null
  }

  return (
    <section className="brands-section">
      <div className="container">
        <h2 className="section-title">Popular Brands</h2>
        <div className="brands-grid">
          {brands.map((brand) => (
            <div key={brand.id} className="brand-card">
              {brand.logo ? (
                <img 
                  src={getImageUrl(brand.logo)} 
                  alt={brand.name}
                  className="brand-logo"
                  onError={(e) => { e.target.src = '/placeholder-brand.png' }}
                />
              ) : (
                <div className="brand-name">{brand.name}</div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default BrandsSection