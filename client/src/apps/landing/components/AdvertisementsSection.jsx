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
        <div className="ads-grid">
          {advertisements.map((ad) => (
            <Link 
              key={ad.id} 
              to={ad.link || '/products'} 
              className="ad-card"
            >
              {ad.image && (
                <img 
                  src={getImageUrl(ad.image)} 
                  alt={ad.title}
                  onError={(e) => { e.target.src = '/placeholder-ad.jpg' }}
                />
              )}
              <div className="ad-content">
                <h3 className="ad-title">{ad.title}</h3>
                {ad.subtitle && <p className="ad-subtitle">{ad.subtitle}</p>}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}

export default AdvertisementsSection