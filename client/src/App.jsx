import { Routes, Route, Navigate, Link } from 'react-router-dom'
import Navbar from './common/components/Navbar'
import Footer from './common/components/Footer'
import './App.css'
import {
  AboutPage,
  PrivacyPolicyPage,
  ReturnRefundSafetyPage,
  TermsConditionsPage,
  FaqsPage,
} from './apps/pages/pages'
import { Login, VerifyOTP, Profile } from './apps/users/pages'
import { ProductListing, ProductDetail } from './apps/products/pages'
import { Cart } from './apps/cart/pages'
import { Wishlist } from './apps/wishlist/pages'
import { Checkout, OrderConfirmation, OrderTracking, OrderHistory } from './apps/order/pages'

function HomePage() {
  return (
    <main className="page-content">
      <section className="hero">
        <div className="hero-text">
          <p className="eyebrow">Premium aftermarket parts</p>
          <h1>Everything your vehicle needs, in one place.</h1>
          <p className="subtext">
            Browse interior, exterior, electrical, and performance parts tailored to your vehicle. Smooth ordering, easy
            returns, and tracked delivery.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn primary">Shop now</Link>
            <Link to="/products" className="btn ghost">Explore categories</Link>
          </div>
        </div>
        <div className="hero-card">
          <div className="hero-card__badge">New</div>
          <h3>Featured: Seltos LED Headlamps</h3>
          <p>Plug-and-play kits with CANBUS support and 1-year warranty.</p>
          <div className="pill-group">
            <span className="pill">Easy install</span>
            <span className="pill">Free shipping</span>
            <span className="pill">Cash on delivery</span>
          </div>
        </div>
      </section>
    </main>
  )
}

function PageShell({ children }) {
  return <section className="page-stack">{children}</section>
}

function App() {
  return (
    <div className="app-shell">
      <Navbar />

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route
          path="/about"
          element={
            <PageShell>
              <AboutPage />
            </PageShell>
          }
        />
        <Route
          path="/privacy-policy"
          element={
            <PageShell>
              <PrivacyPolicyPage />
            </PageShell>
          }
        />
        <Route
          path="/return-refund-safety"
          element={
            <PageShell>
              <ReturnRefundSafetyPage />
            </PageShell>
          }
        />
        <Route
          path="/terms-conditions"
          element={
            <PageShell>
              <TermsConditionsPage />
            </PageShell>
          }
        />
        <Route
          path="/faqs"
          element={
            <PageShell>
              <FaqsPage />
            </PageShell>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/products" element={<ProductListing />} />
        <Route path="/products/:slug" element={<ProductDetail />} />
        <Route path="/cart" element={<Cart />} />
        <Route path="/wishlist" element={<Wishlist />} />
        <Route path="/checkout" element={<Checkout />} />
        <Route path="/order-confirmation/:orderNumber" element={<OrderConfirmation />} />
        <Route path="/track" element={<OrderTracking />} />
        <Route path="/orders" element={<OrderHistory />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      <Footer />
    </div>
  )
}

export default App
