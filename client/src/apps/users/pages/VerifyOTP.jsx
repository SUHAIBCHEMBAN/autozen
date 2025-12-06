import { useState, useEffect, useRef } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { verifyOTP, sendOTP } from '../services/authService'
import './VerifyOTP.css'

function VerifyOTP() {
  const [otp, setOtp] = useState(['', '', '', '', '', ''])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [resendLoading, setResendLoading] = useState(false)
  const [resendCooldown, setResendCooldown] = useState(0)
  const [identifier, setIdentifier] = useState('')
  const navigate = useNavigate()
  const location = useLocation()
  const inputRefs = useRef([])

  useEffect(() => {
    // Get identifier from location state or sessionStorage
    const stateIdentifier = location.state?.identifier
    const storedIdentifier = sessionStorage.getItem('auth_identifier')
    const id = stateIdentifier || storedIdentifier

    if (!id) {
      // If no identifier, redirect to login
      navigate('/login', { replace: true })
      return
    }

    setIdentifier(id)
    // Start cooldown timer
    setResendCooldown(60)
  }, [location, navigate])

  useEffect(() => {
    // Cooldown timer
    if (resendCooldown > 0) {
      const timer = setTimeout(() => setResendCooldown(resendCooldown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [resendCooldown])

  const handleOtpChange = (index, value) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) return

    const newOtp = [...otp]
    newOtp[index] = value
    setOtp(newOtp)
    setError('')

    // Move to next input if value is entered
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index, e) => {
    // Move to previous input on backspace if current input is empty
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
  }

  const handlePaste = (e) => {
    e.preventDefault()
    const pasteData = e.clipboardData.getData('text')
    const cleanedData = pasteData.replace(/\D/g, '').slice(0, 6)
    
    if (cleanedData.length === 6) {
      const newOtp = cleanedData.split('')
      setOtp(newOtp)
      // Focus on the last input
      inputRefs.current[5]?.focus()
    } else {
      // Handle partial paste or invalid data
      const newOtp = [...otp]
      for (let i = 0; i < Math.min(cleanedData.length, 6); i++) {
        newOtp[i] = cleanedData[i]
      }
      setOtp(newOtp)
      // Focus on the next empty input or last input
      const nextIndex = Math.min(cleanedData.length, 5)
      inputRefs.current[nextIndex]?.focus()
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const otpString = otp.join('')
    if (otpString.length !== 6) {
      setError('Please enter the complete 6-digit OTP')
      return
    }

    setLoading(true)

    try {
      const response = await verifyOTP(identifier, otpString)
      
      // Clear session storage
      sessionStorage.removeItem('auth_identifier')
      
      // Store authentication token
      if (response.token) {
        sessionStorage.setItem('authToken', response.token)
      }
      
      // Store user data
      sessionStorage.setItem('user', JSON.stringify({
        user_id: response.user_id,
        email: response.email,
        phone_number: response.phone_number,
        username: response.username,
        profile: response.profile,
      }))

      // Navigate to profile page
      navigate('/profile', { replace: true })
    } catch (err) {
      setError(err.message)
      // Clear OTP on error
      setOtp(['', '', '', '', '', ''])
      inputRefs.current[0]?.focus()
    } finally {
      setLoading(false)
    }
  }

  const handleResendOTP = async () => {
    if (resendCooldown > 0 || resendLoading) return

    setResendLoading(true)
    setError('')

    try {
      await sendOTP(identifier)
      setResendCooldown(60)
      setError('')
    } catch (err) {
      setError(err.message)
    } finally {
      setResendLoading(false)
    }
  }

  return (
    <div className="verify-otp-page">
      <div className="verify-otp-container">
        <div className="verify-otp-header">
          <h1>Verify Your Identity</h1>
          <p>We've sent a 6-digit code to <strong>{identifier}</strong></p>
        </div>

        <form onSubmit={handleSubmit} className="verify-otp-form">
          <div className="otp-input-group">
            <label htmlFor="otp-input">Enter OTP Code</label>
            <div className="otp-inputs">
              {otp.map((digit, index) => (
                <input
                  key={index}
                  ref={(el) => (inputRefs.current[index] = el)}
                  type="text"
                  inputMode="numeric"
                  maxLength="1"
                  value={digit}
                  onChange={(e) => handleOtpChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  onPaste={handlePaste}
                  className="otp-input"
                  disabled={loading}
                  id={index === 0 ? "otp-input" : undefined}
                />
              ))}
            </div>
          </div>

          {error && (
            <div className="alert alert-error" role="alert">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner-small"></span>
                Verifying...
              </>
            ) : (
              'Verify & Continue'
            )}
          </button>
        </form>

        <div className="resend-section">
          <p>Didn't receive the code?</p>
          <button
            onClick={handleResendOTP}
            className="btn-link"
            disabled={resendCooldown > 0 || resendLoading || loading}
          >
            {resendLoading ? (
              <>
                <span className="spinner-small"></span>
                Sending...
              </>
            ) : resendCooldown > 0 ? (
              `Resend in ${resendCooldown}s`
            ) : (
              'Resend OTP'
            )}
          </button>
        </div>

        <div className="back-to-login">
          <Link to="/login" className="btn-secondary">
            ← Back to Login
          </Link>
        </div>
      </div>
    </div>
  )
}

export default VerifyOTP