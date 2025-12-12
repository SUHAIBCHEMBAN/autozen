import { Routes, Route, Navigate, Link } from 'react-router-dom'
import Navbar from './common/components/Navbar'
import Footer from './common/components/Footer'
import ProtectedRoute from './common/components/ProtectedRoute'
import AuthModal from './common/components/AuthModal'
import { useState, useEffect } from 'react'
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
import LandingPage from './apps/landing/pages/LandingPage'

// Simple component to check if user is authenticated
const isAuthenticated = () => {
  const token = sessionStorage.getItem('authToken')
  const user = sessionStorage.getItem('user')
  return !!token && !!user
}

// Component that conditionally renders protected content or redirects
function ConditionalRedirect({ children, redirectTo }) {
  return isAuthenticated() ? children : <Navigate to={redirectTo} replace />
}

// Component to show auth modal on current page
function AuthModalPage() {
  const [isModalOpen, setIsModalOpen] = useState(true)
  
  // If user becomes authenticated while modal is open, redirect to home
  useEffect(() => {
    if (isAuthenticated()) {
      window.location.href = '/'
    }
  }, [])
  
  const closeModal = () => {
    setIsModalOpen(false)
  }
  
  if (!isModalOpen) {
    // Go back to previous page when modal is closed
    window.history.back()
    return null
  }
  
  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <AuthModal 
        isOpen={isModalOpen} 
        onClose={closeModal} 
        message="You need to be logged in to access this page. Please login to continue."
      />
    </div>
  )
}

function App() {
  return (
    <div className="app-shell">
      <Navbar />

      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route
          path="/about"
          element={
            <section className="page-stack">
              <AboutPage />
            </section>
          }
        />
        <Route
          path="/privacy-policy"
          element={
            <section className="page-stack">
              <PrivacyPolicyPage />
            </section>
          }
        />
        <Route
          path="/return-refund-safety"
          element={
            <section className="page-stack">
              <ReturnRefundSafetyPage />
            </section>
          }
        />
        <Route
          path="/terms-conditions"
          element={
            <section className="page-stack">
              <TermsConditionsPage />
            </section>
          }
        />
        <Route
          path="/faqs"
          element={
            <section className="page-stack">
              <FaqsPage />
            </section>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/verify-otp" element={<VerifyOTP />} />
        <Route path="/auth-modal" element={<AuthModalPage />} />
        <Route 
          path="/profile" 
          element={
            <ConditionalRedirect redirectTo="/auth-modal">
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            </ConditionalRedirect>
          } 
        />
        <Route path="/products" element={<ProductListing />} />
        <Route path="/products/:slug" element={<ProductDetail />} />
        <Route 
          path="/cart" 
          element={
            <ConditionalRedirect redirectTo="/auth-modal">
              <ProtectedRoute>
                <Cart />
              </ProtectedRoute>
            </ConditionalRedirect>
          } 
        />
        <Route 
          path="/wishlist" 
          element={
            <ConditionalRedirect redirectTo="/auth-modal">
              <ProtectedRoute>
                <Wishlist />
              </ProtectedRoute>
            </ConditionalRedirect>
          } 
        />
        <Route 
          path="/checkout" 
          element={
            <ConditionalRedirect redirectTo="/auth-modal">
              <ProtectedRoute>
                <Checkout />
              </ProtectedRoute>
            </ConditionalRedirect>
          } 
        />
        <Route 
          path="/order-confirmation/:orderNumber" 
          element={
            <ConditionalRedirect redirectTo="/auth-modal">
              <ProtectedRoute>
                <OrderConfirmation />
              </ProtectedRoute>
            </ConditionalRedirect>
          } 
        />
        <Route 
          path="/track" 
          element={
            <ConditionalRedirect redirectTo="/auth-modal">
              <ProtectedRoute>
                <OrderTracking />
              </ProtectedRoute>
            </ConditionalRedirect>
          } 
        />
        <Route 
          path="/orders" 
          element={
            <ConditionalRedirect redirectTo="/auth-modal">
              <ProtectedRoute>
                <OrderHistory />
              </ProtectedRoute>
            </ConditionalRedirect>
          } 
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      <Footer />
    </div>
  )
}

export default App