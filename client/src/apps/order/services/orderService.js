/**
 * Order service for handling order-related API calls
 */

const API_BASE_URL = 'http://localhost:8000/api/orders'

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
 * Process checkout and create order
 * @param {Object} checkoutData - Checkout data including customer info, addresses, payment method, and items
 * @returns {Promise<Object>} Order creation response
 */
export const checkout = async (checkoutData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/orders/checkout/`, getFetchOptions('POST', checkoutData))

    const data = await response.json()

    if (!response.ok) {
      // Handle validation errors
      if (data.items) {
        throw new Error(data.items[0] || 'Invalid items data')
      }
      throw new Error(data.detail || data.error || Object.values(data).flat().join(', ') || 'Failed to create order')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get all orders for the current user
 * @returns {Promise<Array>} List of orders
 */
export const getOrders = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/orders/`, getFetchOptions('GET'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to fetch orders')
    }

    // Handle paginated response
    if (data.results) {
      return data.results
    }

    // Handle array response
    return Array.isArray(data) ? data : []
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get order by order number
 * @param {string} orderNumber - Order number
 * @returns {Promise<Object>} Order details
 */
export const getOrderByNumber = async (orderNumber) => {
  try {
    const response = await fetch(`${API_BASE_URL}/orders/${orderNumber}/`, getFetchOptions('GET'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to fetch order')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get order history for the current user
 * @returns {Promise<Array>} List of orders
 */
export const getOrderHistory = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/orders/history/`, getFetchOptions('GET'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to fetch order history')
    }

    // Handle paginated response
    if (data.results) {
      return data.results
    }

    // Handle array response
    if (data.orders) {
      return data.orders
    }

    return Array.isArray(data) ? data : []
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Track an order by order number (public)
 * @param {string} orderNumber - Order number
 * @param {string} email - Optional email for verification
 * @returns {Promise<Object>} Order details
 */
export const trackOrder = async (orderNumber, email = null) => {
  try {
    const body = { order_number: orderNumber }
    if (email) body.email = email

    const response = await fetch(`${API_BASE_URL}/orders/track/`, getFetchOptions('POST', body))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to track order')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

export const cancelOrder = async (orderNumber) => {
  try {
    const response = await fetch(`${API_BASE_URL}/orders/${orderNumber}/cancel/`, getFetchOptions('POST'))

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || data.error || 'Failed to cancel order')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

export const downloadInvoice = async (orderNumber) => {
  try {
    const response = await fetch(`${API_BASE_URL}/orders/${orderNumber}/invoice/`, getFetchOptions('GET'))

    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      throw new Error(data.detail || 'Failed to download invoice')
    }

    return await response.blob()
  } catch (error) {
    throw new Error(error.message || 'Network error')
  }
}


