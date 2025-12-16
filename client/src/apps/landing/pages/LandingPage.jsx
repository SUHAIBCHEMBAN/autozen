import { useState, useEffect } from 'react'
import { getLandingPageContent } from '../services/landingService'
import HeroCarousel from '../components/HeroCarousel'
import CategoriesSection from '../components/CategoriesSection'
import FeaturedProductsSection from '../components/FeaturedProductsSection'
import AdvertisementsSection from '../components/AdvertisementsSection'
import TestimonialsSection from '../components/TestimonialsSection'
import BrandsSection from '../components/BrandsSection'
import './LandingPage.css'

function LandingPage() {
  const [content, setContent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadLandingContent()
  }, [])

  const loadLandingContent = async () => {
    try {
      setLoading(true)
      setError('')
      const data = await getLandingPageContent()
      console.log('Landing page content received:', data);
      setContent(data)
    } catch (err) {
      console.error('Error loading landing page content:', err);
      setError(err.message || 'Failed to load landing page content')
    } finally {
      setLoading(false)
    }
  }

  // Add a timeout to prevent infinite loading
  useEffect(() => {
    const timer = setTimeout(() => {
      if (loading) {
        setError('Loading took too long. Please try again.')
        setLoading(false)
      }
    }, 15000) // 15 second timeout

    return () => clearTimeout(timer)
  }, [loading])

  if (loading) {
    return (
      <div className="landing-page">
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="landing-page">
        <div className="error-state">
          <p>{error}</p>
          <button onClick={loadLandingContent} className="btn-primary">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!content) {
    return (
      <div className="landing-page">
        <div className="empty-state">
          <p>No content available</p>
        </div>
      </div>
    )
  }

  // Safely render components with fallbacks
  return (
    <div className="landing-page">
      {content.hero_banners && <HeroCarousel banners={content.hero_banners} />}
      {content.categories && <CategoriesSection categories={content.categories} />}
      {content.featured_products && <FeaturedProductsSection products={content.featured_products} />}
      {content.advertisements && <AdvertisementsSection advertisements={content.advertisements} />}
      {content.testimonials && <TestimonialsSection testimonials={content.testimonials} />}
      {content.featured_brands && <BrandsSection brands={content.featured_brands} />}
    </div>
  )
}

export default LandingPage