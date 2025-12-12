import { Link, useNavigate } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import { UserIcon, PackageIcon, HeartIcon } from './Icons'
import { searchProducts } from '../../apps/products/services/productsService'
import { getParentCategories } from '../../apps/products/services/productsService'

function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [showSearchResults, setShowSearchResults] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [categories, setCategories] = useState([])
  const [loadingCategories, setLoadingCategories] = useState(true)
  const searchTimeoutRef = useRef(null)
  const searchContainerRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    // Check if user is logged in
    const user = sessionStorage.getItem('user')
    setIsLoggedIn(!!user)

    // Listen for storage changes (when user logs in/out in another tab)
    const handleStorageChange = () => {
      const user = sessionStorage.getItem('user')
      setIsLoggedIn(!!user)
    }

    window.addEventListener('storage', handleStorageChange)
    // Also check on focus (for same-tab updates)
    window.addEventListener('focus', handleStorageChange)

    // Load categories
    loadCategories()

    // Cleanup event listeners
    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('focus', handleStorageChange)
      // Clear timeout if component unmounts
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current)
      }
    }
  }, [])

  // Close search results when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        setShowSearchResults(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const loadCategories = async () => {
    try {
      const data = await getParentCategories()
      setCategories(Array.isArray(data) ? data : [])
    } catch (error) {
      console.error('Failed to load categories:', error)
      setCategories([])
    } finally {
      setLoadingCategories(false)
    }
  }

  const handleCategoryClick = (categoryId, categoryName) => {
    // Navigate to products page with category filter
    navigate(`/products?part_category=${categoryId}`)
  }

  const handleProfileClick = (e) => {
    // Prevent default navigation
    e.preventDefault()
    
    // If user is logged in, navigate to profile
    if (isLoggedIn) {
      navigate('/profile')
    } else {
      // For unauthenticated users, navigate to auth modal
      navigate('/auth-modal')
    }
  }

  const handleCartClick = (e) => {
    // Prevent default navigation for unauthenticated users
    if (!isLoggedIn) {
      e.preventDefault()
      navigate('/auth-modal')
    }
  }

  const handleWishlistClick = (e) => {
    // Prevent default navigation for unauthenticated users
    if (!isLoggedIn) {
      e.preventDefault()
      navigate('/auth-modal')
    }
  }

  const handleSearchChange = (e) => {
    const query = e.target.value
    setSearchQuery(query)
    
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current)
    }
    
    // If query is empty, hide results
    if (!query.trim()) {
      setSearchResults([])
      setShowSearchResults(false)
      return
    }
    
    // Set timeout to debounce search
    searchTimeoutRef.current = setTimeout(async () => {
      await performSearch(query)
    }, 300)
  }

  const performSearch = async (query) => {
    if (!query.trim()) return
    
    setIsSearching(true)
    try {
      const results = await searchProducts(query)
      setSearchResults(results.slice(0, 5)) // Limit to 5 results
      setShowSearchResults(true)
    } catch (error) {
      console.error('Search error:', error)
      setSearchResults([])
    } finally {
      setIsSearching(false)
    }
  }

  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return null
    
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

  const handleSearchResultClick = (slug) => {
    setSearchQuery('')
    setSearchResults([])
    setShowSearchResults(false)
    navigate(`/products/${slug}`)
  }

  const handleSeeAllResults = () => {
    if (searchQuery.trim()) {
      const query = searchQuery.trim()
      setSearchQuery('')
      setSearchResults([])
      setShowSearchResults(false)
      navigate(`/products?q=${encodeURIComponent(query)}`)
    }
  }

  const handleSearchSubmit = (e) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      const query = searchQuery.trim()
      setSearchQuery('')
      setSearchResults([])
      setShowSearchResults(false)
      navigate(`/products?q=${encodeURIComponent(query)}`)
    }
  }

  return (
    <header className="navbar">
      <div className="navbar__inner">
        <Link to="/">
          <div className="navbar__brand">
            <span className="brand-primary">Auto</span>
            <span className="brand-accent">Zen</span>
          </div>
        </Link>

        <div className="navbar__search" ref={searchContainerRef}>
          <form onSubmit={handleSearchSubmit}>
            <input
              type="text"
              placeholder="Search for Seltos, Innova etc..."
              aria-label="Search products"
              value={searchQuery}
              onChange={handleSearchChange}
              onFocus={() => searchQuery.trim() && setShowSearchResults(true)}
            />
          </form>
          
          {showSearchResults && (
            <div className="search-results-dropdown">
              {isSearching ? (
                <div className="search-loading">Searching...</div>
              ) : searchResults.length > 0 ? (
                <>
                  <ul className="search-results-list">
                    {searchResults.map((product) => (
                      <li 
                        key={product.id} 
                        className="search-result-item"
                        onClick={() => handleSearchResultClick(product.slug)}
                      >
                        <div className="search-result-image">
                          {product.featured_image ? (
                            <img 
                              src={getImageUrl(product.featured_image)} 
                              alt={product.name}
                              onError={(e) => { e.target.src = '/placeholder-product.png' }}
                            />
                          ) : (
                            <div className="placeholder-image">No Image</div>
                          )}
                        </div>
                        <div className="search-result-info">
                          <div className="search-result-name">{product.name}</div>
                          <div className="search-result-price">₹{product.price}</div>
                        </div>
                      </li>
                    ))}
                  </ul>
                  <div className="search-results-footer">
                    <button 
                      className="see-all-results-btn"
                      onClick={handleSeeAllResults}
                    >
                      See all results ({searchResults.length}+)
                    </button>
                  </div>
                </>
              ) : (
                <div className="search-no-results">No products found</div>
              )}
            </div>
          )}
        </div>

        <div className="navbar__actions">
          <a
            href="/wishlist"
            onClick={handleWishlistClick}
            className="icon-button"
            aria-label="Wishlist"
          >
            <HeartIcon />
          </a>
          <a
            href="/cart"
            onClick={handleCartClick}
            className="icon-button"
            aria-label="Cart"
          >
            <PackageIcon />
          </a>
          <a
            href="/profile"
            onClick={handleProfileClick}
            className="icon-button"
            aria-label="Account"
          >
            <UserIcon />
          </a>
        </div>
      </div>

      <nav className="navbar__links" aria-label="Primary">
        {loadingCategories ? (
          <a href="#">Loading categories...</a>
        ) : categories.length > 0 ? (
          categories.map((category) => (
            <a 
              key={category.id} 
              onClick={(e) => {
                e.preventDefault();
                handleCategoryClick(category.id, category.name);
              }}
              href="#"
            >
              {category.name}
            </a>
          ))
        ) : (
          // Fallback to hardcoded categories if API fails
          ['Select Vehicle', 'Interior Accessories', 'Exterior Accessories', 'Auto Parts', 'Lights', 'Electronic Parts', 'Care & Styling'].map((link) => (
            <a key={link} href="#">
              {link}
            </a>
          ))
        )}
      </nav>
    </header>
  )
}

export default Navbar