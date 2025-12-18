import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

const CategoriesSection = ({ categories }) => {
  const [parentCategories, setParentCategories] = useState([])
  const [activeParent, setActiveParent] = useState(null)
  const [childCategories, setChildCategories] = useState([])

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

  // Extract parent categories and set the first one as active by default
  useEffect(() => {
    console.log('Categories data received:', categories);
    
    if (categories && categories.length > 0) {
      // Filter for parent categories (those without a parent in the PartCategory model)
      const parents = categories.filter(cat => cat.category && cat.category.parent === null)
      console.log('Parent categories identified:', parents);
      setParentCategories(parents)
      
      // Set first parent as active by default
      if (parents.length > 0 && !activeParent) {
        setActiveParent(parents[0])
        console.log('Setting first parent as active:', parents[0]);
      }
    } else {
      console.log('No categories data available');
    }
  }, [categories])

  // When active parent changes, fetch its child categories
  useEffect(() => {
    console.log('Active parent changed:', activeParent);
    
    if (activeParent && categories) {
      // Find child categories for the active parent
      const children = categories.filter(cat => 
        cat.category && cat.category.parent === activeParent.category.id
      )
      console.log('Child categories found:', children);
      setChildCategories(children)
    } else {
      setChildCategories([])
    }
  }, [activeParent, categories])

  const handleParentClick = (parent) => {
    console.log('Parent clicked:', parent);
    setActiveParent(parent)
  }

  // If no categories data, show a message for debugging
  if (!categories) {
    return (
      <section className="categories-section">
        <div className="container">
          <p>No categories data available</p>
        </div>
      </section>
    )
  }

  if (categories.length === 0) {
    return (
      <section className="categories-section">
        <div className="container">
          <p>No categories found</p>
        </div>
      </section>
    )
  }

  return (
    <section className="categories-section">
      <div className="container">
        {/* Debug info */}
        <div style={{ display: 'none' }}>
          <p>Total categories: {categories.length}</p>
          <p>Parent categories: {parentCategories.length}</p>
          <p>Child categories: {childCategories.length}</p>
        </div>
        
        {/* Parent Categories Bar with | separators */}
        {parentCategories.length > 0 ? (
          <div className="parent-categories-bar">
            {parentCategories.slice(0, 7).map((parent, index) => (
              <span key={parent.id}>
                <button
                  className={`parent-category ${activeParent && activeParent.id === parent.id ? 'active' : ''}`}
                  onClick={() => handleParentClick(parent)}
                >
                  {parent.title}
                </button>
                {index < parentCategories.slice(0, 7).length - 1 && <span className="separator"> | </span>}
              </span>
            ))}
          </div>
        ) : (
          <p>No parent categories found</p>
        )}

        {/* Child Categories Grid */}
        {childCategories.length > 0 && (
          <div className="child-categories-grid">
            {childCategories.map((child) => (
              <Link 
                key={child.id} 
                to={`/products?part_category=${child.category.id}`}
                className="category-card"
              >
                {child.image ? (
                  <img 
                    src={getImageUrl(child.image)} 
                    alt={child.title}
                    className="category-image"
                    onError={(e) => { e.target.src = '/placeholder-category.jpg' }}
                  />
                ) : child.icon ? (
                  <img 
                    src={getImageUrl(child.icon)} 
                    alt={child.title}
                    className="category-icon"
                    onError={(e) => { e.target.src = '/placeholder-icon.png' }}
                  />
                ) : (
                  <div className="category-placeholder">
                    <span>{child.title.charAt(0)}</span>
                  </div>
                )}
                <h3 className="category-title">{child.title}</h3>
                {child.description && (
                  <p className="category-description">{child.description}</p>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </section>
  )
}

export default CategoriesSection