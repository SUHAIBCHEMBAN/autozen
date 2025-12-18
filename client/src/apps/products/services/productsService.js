/**
 * Products service for handling product-related API calls
 */

const API_BASE_URL = 'http://localhost:8000/api/products'

// Cache for parent categories
let parentCategoriesCache = null
let parentCategoriesCacheTime = 0
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

/**
 * Get all products with optional filters
 * @param {Object} params - Query parameters (brand, vehicle_model, part_category, is_featured, ordering, search)
 * @returns {Promise<Array>}
 */
export const getProducts = async (params = {}) => {
  try {
    const queryString = new URLSearchParams(params).toString()
    const url = `${API_BASE_URL}/products/${queryString ? `?${queryString}` : ''}`

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch products')
    }

    return data.results || data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get a single product by slug
 * @param {string} slug - Product slug
 * @returns {Promise<Object>}
 */
export const getProductBySlug = async (slug) => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/${slug}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Product not found')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get featured products
 * @returns {Promise<Array>}
 */
export const getFeaturedProducts = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/featured/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch featured products')
    }

    return data.results || data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Search products
 * @param {string} query - Search query
 * @returns {Promise<Array>}
 */
export const searchProducts = async (query) => {
  try {
    const response = await fetch(`${API_BASE_URL}/products/search/?q=${encodeURIComponent(query)}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Search failed')
    }

    return data.results || data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get all brands
 * @returns {Promise<Array>}
 */
export const getBrands = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/brands/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch brands')
    }

    return data.results || data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get all vehicle models
 * @param {number} brandId - Optional brand ID to filter models
 * @returns {Promise<Array>}
 */
export const getVehicleModels = async (brandId = null) => {
  try {
    const url = brandId
      ? `${API_BASE_URL}/models/?brand=${brandId}`
      : `${API_BASE_URL}/models/`

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch vehicle models')
    }

    return data.results || data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get all categories
 * @returns {Promise<Array>}
 */
export const getCategories = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/categories/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch categories')
    }

    return data.results || data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get parent categories only with caching to prevent rate limiting
 * @returns {Promise<Array>}
 */
export const getParentCategories = async () => {
  const now = Date.now()

  // Return cached data if it's still valid (less than 5 minutes old)
  if (parentCategoriesCache && (now - parentCategoriesCacheTime) < CACHE_DURATION) {
    return parentCategoriesCache
  }

  try {
    const response = await fetch(`${API_BASE_URL}/categories/parents/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch parent categories')
    }

    // Cache the result
    parentCategoriesCache = data.results || data
    parentCategoriesCacheTime = now

    return parentCategoriesCache
  } catch (error) {
    // On error, clear cache and rethrow
    parentCategoriesCache = null
    parentCategoriesCacheTime = 0
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get child categories only (categories that have a parent)
 * @returns {Promise<Array>}
 */
export const getChildCategories = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/categories/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to fetch categories')
    }

    const allCategories = data.results || data

    // Filter for only child categories (those with a parent)
    const childCategories = allCategories.filter(category => category.parent !== null)

    return childCategories
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}