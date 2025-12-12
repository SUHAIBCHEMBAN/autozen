import { useNavigate } from 'react-router-dom'
import './AuthModal.css'

function AuthModal({ isOpen, onClose, message = "You need to be logged in to access this page." }) {
  const navigate = useNavigate()

  if (!isOpen) return null

  const handleLoginRedirect = () => {
    navigate('/login')
  }

  const handleGoBack = () => {
    // Go back to previous page
    window.history.back()
  }

  // Prevent closing when clicking on the overlay
  const handleOverlayClick = (e) => {
    // Only close if clicking directly on the overlay, not on the modal content
    if (e.target === e.currentTarget) {
      // Don't close on overlay click, but we can still provide feedback
      // For now, we'll just ignore the click
    }
  }

  return (
    <div className="auth-modal-overlay" onClick={handleOverlayClick}>
      <div className="auth-modal" onClick={e => e.stopPropagation()}>
        <div className="auth-modal-header">
          <h2>Authentication Required</h2>
        </div>
        <div className="auth-modal-body">
          <p>{message}</p>
        </div>
        <div className="auth-modal-footer">
          <button className="btn secondary" onClick={handleGoBack}>
            Go Back
          </button>
          <button className="btn primary" onClick={handleLoginRedirect}>
            Login
          </button>
        </div>
      </div>
    </div>
  )
}

export default AuthModal