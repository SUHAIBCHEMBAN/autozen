import { Link } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { UserIcon, PackageIcon, HeartIcon } from './Icons'

const navLinks = [
  'Select Vehicle',
  'Interior Accessories',
  'Exterior Accessories',
  'Auto Parts',
  'Lights',
  'Electronic Parts',
  'Care & Styling',
]

function Navbar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)

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

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('focus', handleStorageChange)
    }
  }, [])

  return (
    <header className="navbar">
      <div className="navbar__inner">
        <Link to="/">
          <div className="navbar__brand">
            <span className="brand-primary">Auto</span>
            <span className="brand-accent">Zen</span>
          </div>
        </Link>

        <div className="navbar__search">
          <input
            type="text"
            placeholder="Search for Seltos , Innova  etc ..."
            aria-label="Search products"
          />
        </div>

        <div className="navbar__actions">
          <Link to="/wishlist" className="icon-button" aria-label="Wishlist">
            <HeartIcon />
          </Link>
          <Link to="/cart" className="icon-button" aria-label="Cart">
            <PackageIcon />
          </Link>
          <Link
            to={isLoggedIn ? '/profile' : '/login'}
            className="icon-button"
            aria-label="Account"
          >
            <UserIcon />
          </Link>
        </div>
      </div>

      <nav className="navbar__links" aria-label="Primary">
        {navLinks.map((link) => (
          <a key={link} href="#">
            {link}
          </a>
        ))}
      </nav>
    </header>
  )
}

export default Navbar