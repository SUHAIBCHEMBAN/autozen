import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { sendOTP } from '../services/authService'
import './Login.css'

function Login() {
  const [emailOrPhone, setEmailOrPhone] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const validateInput = (value) => {
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    // Basic phone validation (10-15 digits, optional + at start)
    const phoneRegex = /^\+?[1-9]\d{9,14}$/

    if (!value.trim()) {
      return 'Please enter your email or phone number'
    }

    if (!emailRegex.test(value) && !phoneRegex.test(value)) {
      return 'Please enter a valid email or phone number'
    }

    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const validationError = validateInput(emailOrPhone)
    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)

    try {
      const response = await sendOTP(emailOrPhone.trim())
      
      // Store identifier in sessionStorage for OTP verification page
      sessionStorage.setItem('auth_identifier', emailOrPhone.trim())
      
      // Navigate to OTP verification page
      navigate('/verify-otp', { 
        state: { 
          identifier: emailOrPhone.trim(),
          message: response.message 
        } 
      })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>Welcome Back</h1>
          <p>Enter your email or phone number to receive a login code</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && (
            <div className="auth-error" role="alert">
              <svg
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="emailOrPhone">Email or Phone Number</label>
            <input
              type="text"
              id="emailOrPhone"
              value={emailOrPhone}
              onChange={(e) => {
                setEmailOrPhone(e.target.value)
                setError('')
              }}
              placeholder="example@email.com or +1234567890"
              disabled={loading}
              autoComplete="email"
              autoFocus
            />
          </div>

          <button
            type="submit"
            className="btn-auth-primary"
            disabled={loading || !emailOrPhone.trim()}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Sending OTP...
              </>
            ) : (
              'Send OTP'
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account? <Link to="/signup">Sign up</Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login

