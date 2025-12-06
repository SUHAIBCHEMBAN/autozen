import { Link } from 'react-router-dom'

const footerColumns = [
  {
    title: 'Quick Links',
    items: [
      { label: 'Home', href: '/' },
      { label: 'About', href: '/about' },
      { label: 'Shop', href: '/products' },
      { label: 'Login', href: '/login' },
    ],
  },
  {
    title: 'Support Links',
    items: [
      { label: 'Privacy & Policy', href: '/privacy-policy' },
      { label: 'Terms & Conditions', href: '/terms-conditions' },
      { label: 'Return & Refund', href: '/return-refund-safety' },
      { label: 'FAQs', href: '/faqs' },
    ],
  },
  {
    title: 'Market Place',
    items: [
      { label: 'Cart', href: '/cart' },
      { label: 'Wishlist', href: '/wishlist' },
      { label: 'Order Tracking', href: '/order-tracking' },
      { label: 'My Account', href: '/profile' },
    ],
  },
]

const socialIcons = [
  { label: 'Facebook', href: '#', icon: 'facebook' },
  { label: 'Instagram', href: '#', icon: 'instagram' },
  { label: 'LinkedIn', href: '#', icon: 'linkedin' },
  { label: 'WhatsApp', href: '#', icon: 'whatsapp' },
]

function SocialIcon({ type }) {
  const paths = {
    facebook: (
      <path
        d="M14 9h2V6h-2c-1.7 0-3 1.3-3 3v2H8v3h3v6h3v-6h2.5L17 11h-3V9c0-.5.5-1 1-1Z"
        fill="currentColor"
      />
    ),
    instagram: (
      <>
        <rect x="6" y="6" width="12" height="12" rx="3" fill="none" stroke="currentColor" strokeWidth="1.6" />
        <circle cx="12" cy="12" r="3" fill="none" stroke="currentColor" strokeWidth="1.6" />
        <circle cx="16.5" cy="7.5" r="1" fill="currentColor" />
      </>
    ),
    linkedin: (
      <>
        <path d="M7.5 10h2v7.5h-2z" fill="currentColor" />
        <circle cx="8.5" cy="7" r="1.1" fill="currentColor" />
        <path
          d="M12 10h1.9v1h.1c.3-.6 1.1-1.2 2.2-1.2 2.3 0 2.8 1.4 2.8 3.3v4.4H17v-3.9c0-.9 0-2-1.2-2-1.2 0-1.4.9-1.4 2v3.9H12z"
          fill="currentColor"
        />
      </>
    ),
    whatsapp: (
      <>
        <path
          d="M19 12a7 7 0 0 1-10.2 6.2l-2.1.7.7-2A7 7 0 1 1 19 12Z"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
        />
        <path
          d="M9.6 9.2c-.1-.3-.3-.6-.6-.6s-.7.1-.7.7c0 .6.4 1.4 1 2 .6.7 1.7 1.6 3.2 2.2 1.6.6 1.9.4 2.3.1.3-.3.4-.8.3-1l-.8-.3c-.3-.1-.7-.3-.9.1-.3.4-.5.7-.9.6-.5-.1-1.5-.6-2.2-1.2-.7-.6-1.1-1.3-1.2-1.5-.1-.2 0-.3.1-.4s.2-.2.3-.4c.1-.1.1-.3.1-.5l-.1-.8Z"
          fill="currentColor"
        />
      </>
    ),
  }

  return (
    <svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" className="icon">
      {paths[type]}
    </svg>
  )
}

function Footer() {
  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__brand">
          <div className="brand">
            <span className="brand-primary">Auto</span>
            <span className="brand-accent">Zen</span>
          </div>
          <p>
            Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a
            galley of type and scrambled it to make a type specimen book.
          </p>
          <p>
            Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a
            galley of type and scrambled it to make a type specimen book.
          </p>

          <div className="store-badges">
            <a className="badge" href="#">
              <span className="badge__sub">Download on the</span>
              <span className="badge__title">App Store</span>
            </a>
            <a className="badge" href="#">
              <span className="badge__sub">Get it on</span>
              <span className="badge__title">Google Play</span>
            </a>
          </div>
        </div>

        <div className="footer__links">
          {footerColumns.map((col) => (
            <div key={col.title} className="footer__column">
              <h4>{col.title}</h4>
              <ul>
                {col.items.map((item) => (
                  <li key={item.label}>
                    {item.href.startsWith('/') ? (
                      <Link to={item.href}>{item.label}</Link>
                    ) : (
                      <a href={item.href}>{item.label}</a>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="footer__bottom">
        <span>Copyright 2026 All Right reserved AutoZen</span>
        <div className="footer__social">
          {socialIcons.map((icon) => (
            <a key={icon.icon} href={icon.href} aria-label={icon.label}>
              <SocialIcon type={icon.icon} />
            </a>
          ))}
        </div>
      </div>
    </footer>
  )
}

export default Footer
