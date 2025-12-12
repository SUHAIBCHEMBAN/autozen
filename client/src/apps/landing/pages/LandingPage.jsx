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
      setContent(data)
    } catch (err) {
      setError(err.message || 'Failed to load landing page content')
    } finally {
      setLoading(false)
    }
  }

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

  return (
    <div className="landing-page">
      <HeroCarousel banners={content.hero_banners} />
      <CategoriesSection categories={content.categories} />
      <FeaturedProductsSection products={content.featured_products} />
      <AdvertisementsSection advertisements={content.advertisements} />
      <TestimonialsSection testimonials={content.testimonials} />
      <BrandsSection brands={content.featured_brands} />
    </div>
  )
}

export default LandingPage