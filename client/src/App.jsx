import { Routes, Route, Navigate } from 'react-router-dom'
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
            <button className="btn primary">Shop now</button>
            <button className="btn ghost">Explore categories</button>
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
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      <Footer />
    </div>
  )
}

export default App
