import { Link } from 'react-router-dom'

const AdvertisementsSection = ({ advertisements }) => {
  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-ad.jpg'
    
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

  if (!advertisements || advertisements.length === 0) {
    return null
  }

  return (
    <section className="advertisements-section">
      <div className="container">
        <h2 className="section-title">Special Offers</h2>
        <div className="ads-carousel">
          <div className="ads-grid">
            {advertisements.map((ad) => (
              <Link 
                key={ad.id} 
                to={ad.link || '/products'} 
                className="ad-card"
              >
                <div className="ad-image-container">
                  {ad.image && (
                    <img 
                      src={getImageUrl(ad.image)} 
                      alt={ad.title}
                      className="ad-image"
                      onError={(e) => { 
                        e.target.src = '/placeholder-ad.jpg'
                      }}
                    />
                  )}
                </div>
                <div className="ad-content">
                  <h3 className="ad-title">{ad.title}</h3>
                  {ad.subtitle && <p className="ad-subtitle">{ad.subtitle}</p>}
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

export default AdvertisementsSection