/**
 * Authentication service for handling login and OTP verification
 */

const API_BASE_URL = 'http://localhost:8000/api/auth'

/**
 * Test function to check if token is stored
 */
export const testToken = () => {
  const token = sessionStorage.getItem('authToken')
  return token
}

/**
 * Send OTP to user's email or phone
 * @param {string} emailOrPhone - User's email address or phone number
 * @returns {Promise<{message: string, identifier: string}>}
 */
export const sendOTP = async (emailOrPhone) => {
  try {
    const response = await fetch(`${API_BASE_URL}/send-otp/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email_or_phone: emailOrPhone,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || data.email_or_phone?.[0] || 'Failed to send OTP')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Verify OTP code
 * @param {string} emailOrPhone - User's email address or phone number
 * @param {string} otp - 6-digit OTP code
 * @returns {Promise<{message: string, user_id: number, email: string, phone_number: string}>}
 */
export const verifyOTP = async (emailOrPhone, otp) => {
  try {
    const response = await fetch(`${API_BASE_URL}/verify-otp/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email_or_phone: emailOrPhone,
        otp: otp,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || data.otp?.[0] || data.email_or_phone?.[0] || 'OTP verification failed')
    }

    // Store token in sessionStorage
    if (data.token) {
      sessionStorage.setItem('authToken', data.token)
      // Add a small delay to ensure token is properly stored
      await new Promise(resolve => setTimeout(resolve, 100))
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Get user profile
 * @returns {Promise<Object>}
 */
export const getUserProfile = async () => {
  try {
    const token = sessionStorage.getItem('authToken')
    
    if (!token) {
      throw new Error('No authentication token found')
    }
    
    const response = await fetch(`${API_BASE_URL}/profile/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token}`,
      },
      credentials: 'include',
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Failed to fetch profile')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}

/**
 * Update user profile
 * @param {Object} profileData - Profile data to update
 * @returns {Promise<Object>}
 */
export const updateUserProfile = async (profileData) => {
  try {
    // Check if token exists before proceeding
    const token = sessionStorage.getItem('authToken')
    
    if (!token) {
      // Try to get token from localStorage as fallback
      const localStorageToken = localStorage.getItem('authToken')
      
      if (!localStorageToken) {
        throw new Error('No authentication token found')
      }
      
      // If found in localStorage, move it to sessionStorage
      sessionStorage.setItem('authToken', localStorageToken)
      localStorage.removeItem('authToken')
    }
    
    const response = await fetch(`${API_BASE_URL}/profile/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Token ${token || localStorageToken}`,
      },
      credentials: 'include',
      body: JSON.stringify(profileData),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Failed to update profile')
    }

    return data
  } catch (error) {
    throw new Error(error.message || 'Network error. Please try again.')
  }
}