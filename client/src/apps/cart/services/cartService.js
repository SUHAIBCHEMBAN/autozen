/**
 * Cart service for handling cart-related API calls
 */

const API_BASE_URL = 'http://localhost:8000/api/cart'

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
 * Get user's cart
 * @returns {Promise<Object>}
 */
export const getCart = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/cart/`, getFetchOptions('GET'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to fetch cart')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get cart items
 * @returns {Promise<Array>}
 */
export const getCartItems = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/cart/items/`, getFetchOptions('GET'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to fetch cart items')
    }

    return Array.isArray(data) ? data : []
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Add item to cart
 * @param {number} productId - Product ID
 * @param {number} quantity - Quantity (default: 1)
 * @returns {Promise<Object>}
 */
export const addToCart = async (productId, quantity = 1) => {
  try {
    const response = await fetch(`${API_BASE_URL}/cart/add_item/`, getFetchOptions('POST', {
      product_id: productId,
      quantity: quantity,
    }))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || data.product_id?.[0] || data.quantity?.[0] || 'Failed to add item to cart')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Update cart item quantity
 * @param {number} productId - Product ID
 * @param {number} quantity - New quantity
 * @returns {Promise<Object>}
 */
export const updateCartItem = async (productId, quantity) => {
  try {
    const response = await fetch(`${API_BASE_URL}/cart/update_item/`, getFetchOptions('PUT', {
      product_id: productId,
      quantity: quantity,
    }))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || data.product_id?.[0] || data.quantity?.[0] || 'Failed to update cart item')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Remove item from cart
 * @param {number} productId - Product ID
 * @returns {Promise<Object>}
 */
export const removeFromCart = async (productId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/cart/remove_item/`, getFetchOptions('POST', {
      product_id: productId,
    }))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || data.product_id?.[0] || 'Failed to remove item from cart')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Clear entire cart
 * @returns {Promise<Object>}
 */
export const clearCart = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/cart/clear/`, getFetchOptions('DELETE'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to clear cart')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

