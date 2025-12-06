/**
 * Wishlist service for handling wishlist-related API calls
 */

const API_BASE_URL = 'http://localhost:8000/api/wishlist'

/**
 * Get authentication headers
 */
const getAuthHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
  }
  
  // Try to get token from sessionStorage
  const token = sessionStorage.getItem('authToken')
  if (token) {
    headers['Authorization'] = `Token ${token}`
  }
  
  return headers
}

/**
 * Get fetch options with credentials and auth headers
 */
const getFetchOptions = (method = 'GET', body = null) => {
  const options = {
    method,
    headers: getAuthHeaders(),
    credentials: 'include', // Include cookies for session-based auth
  }
  
  if (body) {
    options.body = JSON.stringify(body)
  }
  
  return options
}

/**
 * Get user's wishlist
 * @returns {Promise<Object>}
 */
export const getWishlist = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/`, getFetchOptions('GET'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to fetch wishlist')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get wishlist items
 * @returns {Promise<Array>}
 */
export const getWishlistItems = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/items/`, getFetchOptions('GET'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to fetch wishlist items')
    }

    return Array.isArray(data) ? data : []
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Add item to wishlist
 * @param {number} productId - Product ID
 * @returns {Promise<Object>}
 */
export const addToWishlist = async (productId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/add_item/`, getFetchOptions('POST', {
      product_id: productId,
    }))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || data.product_id?.[0] || 'Failed to add item to wishlist')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Remove item from wishlist
 * @param {number} productId - Product ID
 * @returns {Promise<Object>}
 */
export const removeFromWishlist = async (productId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/remove_item/`, getFetchOptions('POST', {
      product_id: productId,
    }))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || data.product_id?.[0] || 'Failed to remove item from wishlist')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Clear entire wishlist
 * @returns {Promise<Object>}
 */
export const clearWishlist = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/clear/`, getFetchOptions('DELETE'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to clear wishlist')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Check if product is in wishlist
 * @param {number} productId - Product ID
 * @returns {Promise<boolean>}
 */
export const isInWishlist = async (productId) => {
  try {
    const wishlist = await getWishlist()
    if (wishlist && wishlist.items) {
      return wishlist.items.some((item) => item.product.id === productId)
    }
    return false
  } catch (error) {
    return false
  }
}

