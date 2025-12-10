import { useState } from 'react'
import { Link } from 'react-router-dom'

function ProfileSection({ user, editMode, setEditMode, formData, handleInputChange, handleSaveProfile, handleImageChange, previewImage, error, success, saving, setSuccess, setError }) {
  const handleCancelEdit = (userData) => {
    setEditMode(false)
    setSuccess('')
    setError('')
  }

  const getImageUrl = (image) => {
    if (!image) return '/placeholder-product.png'
    if (image.startsWith('http')) return image
    return `http://localhost:8000${image}`
  }

  return (
    <div className="profile-section">
      <div className="section-header">
        <h2>Personal Information</h2>
        {!editMode && (
          <button
            className="btn-edit"
            onClick={() => {
              setEditMode(true)
              setError('')
              setSuccess('')
            }}
          >
            Edit Profile
          </button>
        )}
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

      {success && (
        <div className="alert alert-success" role="alert">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
          <span>{success}</span>
        </div>
      )}

      {editMode ? (
        <form onSubmit={handleSaveProfile} className="profile-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleInputChange}
              placeholder="Choose a username"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              placeholder="your@email.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="phone_number">Phone Number</label>
            <input
              type="tel"
              id="phone_number"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleInputChange}
              placeholder="+1234567890"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="profile">Profile Bio</label>
            <textarea
              id="profile"
              name="profile"
              value={formData.profile}
              onChange={handleInputChange}
              placeholder="Tell us about yourself..."
              rows="4"
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={() => {
                setEditMode(false)
                setSuccess('')
                setError('')
              }}
              disabled={saving}
            >
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? (
                <>
                  <span className="spinner-small"></span>
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </form>
      ) : (
        <div className="profile-details">
          <div className="detail-item">
            <span className="detail-label">Username</span>
            <span className="detail-value">
              {user.username || <span className="text-muted">Not set</span>}
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Email</span>
            <span className="detail-value">
              {user.email || <span className="text-muted">Not provided</span>}
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Phone Number</span>
            <span className="detail-value">
              {user.phone_number || <span className="text-muted">Not provided</span>}
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Bio</span>
            <span className="detail-value">
              {user.profile || <span className="text-muted">No bio provided</span>}
            </span>
          </div>
          <div className="detail-item">
            <span className="detail-label">User ID</span>
            <span className="detail-value">#{user.id}</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default ProfileSection