/**
 * Landing service for handling landing page API calls
 */

const API_BASE_URL = 'http://localhost:8000/api/landing'

/**
 * Get all landing page content
 * @returns {Promise<Object>}
 */
export const getLandingPageContent = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch landing page content')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get hero banners
 * @returns {Promise<Array>}
 */
export const getHeroBanners = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/hero-banners/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch hero banners')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get category sections
 * @returns {Promise<Array>}
 */
export const getCategorySections = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/category-sections/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch category sections')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get new arrival products
 * @returns {Promise<Array>}
 */
export const getNewArrivals = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/new-arrivals/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch new arrivals')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get advertisement banners
 * @returns {Promise<Array>}
 */
export const getAdvertisements = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/advertisements/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch advertisements')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get testimonials
 * @returns {Promise<Array>}
 */
export const getTestimonials = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/testimonials/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch testimonials')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get featured brands
 * @returns {Promise<Array>}
 */
export const getFeaturedBrands = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/featured-brands/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch featured brands')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}