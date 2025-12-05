const navLinks = [
  'Select Vehicle',
  'Interior Accessories',
  'Exterior Accessories',
  'Auto Parts',
  'Lights',
  'Electronic Parts',
  'Care & Styling',
]

function IconCart() {
  return (
    <svg
      aria-hidden="true"
      focusable="false"
      viewBox="0 0 24 24"
      className="icon"
    >
      <path
        d="M4 5h2l1.5 10h9l1.5-7h-12"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="10" cy="18.5" r="1.1" fill="currentColor" />
      <circle cx="16" cy="18.5" r="1.1" fill="currentColor" />
    </svg>
  )
}

function IconUser() {
  return (
    <svg
      aria-hidden="true"
      focusable="false"
      viewBox="0 0 24 24"
      className="icon"
    >
      <circle
        cx="12"
        cy="8.2"
        r="3.2"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
      />
      <path
        d="M6.5 18.8c.8-2.1 2.9-3.5 5.5-3.5s4.7 1.4 5.5 3.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  )
}

function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar__inner">
        <div className="navbar__brand">
          <span className="brand-primary">Auto</span>
          <span className="brand-accent">Zen</span>
        </div>

        <div className="navbar__search">
          <input
            type="text"
            placeholder="Search for Seltos , Innova  etc ..."
            aria-label="Search products"
          />
        </div>

        <div className="navbar__actions">
          <button className="icon-button" aria-label="Cart">
            <IconCart />
          </button>
          <button className="icon-button" aria-label="Account">
            <IconUser />
          </button>
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
