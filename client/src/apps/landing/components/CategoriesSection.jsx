import { Link } from 'react-router-dom'

const CategoriesSection = ({ categories }) => {
  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-category.jpg'
    
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

  if (!categories || categories.length === 0) {
    return null
  }

  return (
    <section className="categories-section">
      <div className="container">
        <h2 className="section-title">Shop by Category</h2>
        <div className="categories-grid">
          {categories.map((category) => (
            <Link 
              key={category.id} 
              to={`/products?part_category=${category.category.id}`}
              className="category-card"
            >
              {category.image ? (
                <img 
                  src={getImageUrl(category.image)} 
                  alt={category.title}
                  className="category-image"
                  onError={(e) => { e.target.src = '/placeholder-category.jpg' }}
                />
              ) : category.icon ? (
                <img 
                  src={getImageUrl(category.icon)} 
                  alt={category.title}
                  className="category-icon"
                  onError={(e) => { e.target.src = '/placeholder-icon.png' }}
                />
              ) : (
                <div className="category-placeholder">
                  <span>{category.title.charAt(0)}</span>
                </div>
              )}
              <h3 className="category-title">{category.title}</h3>
              {category.description && (
                <p className="category-description">{category.description}</p>
              )}
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}

export default CategoriesSection