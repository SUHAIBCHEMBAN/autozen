import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import './Profile.css'
import { getUserProfile, updateUserProfile } from '../services/authService'
import { UserIcon, PackageIcon, HeartIcon, LocationIcon, SettingsIcon } from '../../../common/components/Icons'

function Profile() {
  const [activeTab, setActiveTab] = useState('profile')
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    phone_number: '',
    username: '',
    profile: '',
  })
  const [profileImage, setProfileImage] = useState(null)
  const [previewImage, setPreviewImage] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [saving, setSaving] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    // Load user data from sessionStorage
    const userData = sessionStorage.getItem('user')
    
    if (!userData) {
      // If no user data, redirect to login
      navigate('/login', { replace: true })
      return
    }

    try {
      const parsedUser = JSON.parse(userData)
      setUser(parsedUser)
      setFormData({
        email: parsedUser.email || '',
        phone_number: parsedUser.phone_number || '',
        username: parsedUser.username || '',
        profile: parsedUser.profile || '',
      })
    } catch (err) {
      navigate('/login', { replace: true })
    } finally {
      setLoading(false)
    }
  }, [navigate])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setError('')
    setSuccess('')
  }

  const handleImageChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setProfileImage(file)
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreviewImage(reader.result)
      }
      reader.readAsDataURL(file)
    }
    setError('')
    setSuccess('')
  }

  const handleSaveProfile = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setSaving(true)

    // Validation
    if (!formData.email && !formData.phone_number) {
      setError('Please provide either an email or phone number')
      setSaving(false)
      return
    }

    try {
      // Prepare data for submission
      const profileData = {
        username: formData.username,
        email: formData.email,
        phone_number: formData.phone_number,
        profile: formData.profile,
      }
      
      // Call the API to update profile
      const updatedUser = await updateUserProfile(profileData)
      
      // Update session storage
      const currentUser = JSON.parse(sessionStorage.getItem('user') || '{}')
      const newUser = {
        ...currentUser,
        ...updatedUser,
      }
      sessionStorage.setItem('user', JSON.stringify(newUser))
      setUser(newUser)
      setEditMode(false)
      setSuccess('Profile updated successfully!')
    } catch (err) {
      setError(err.message || 'Failed to update profile. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleLogout = () => {
    // Clear all session data
    sessionStorage.removeItem('user')
    sessionStorage.removeItem('authToken')
    sessionStorage.removeItem('auth_identifier')
    // Also clear from localStorage if exists
    localStorage.removeItem('authToken')
    navigate('/login', { replace: true })
  }

  if (loading) {
    return (
      <div className="profile-page">
        <div className="profile-container">
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading profile...</p>
          </div>
        </div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const tabs = [
    { id: 'profile', label: 'Profile', icon: <UserIcon /> },
    { id: 'orders', label: 'Orders', icon: <PackageIcon /> },
    { id: 'wishlist', label: 'Wishlist', icon: <HeartIcon /> },
    { id: 'addresses', label: 'Addresses', icon: <LocationIcon /> },
    { id: 'settings', label: 'Settings', icon: <SettingsIcon /> },
  ]

  return (
    <div className="profile-page">
      <div className="profile-container">
        <div className="profile-header">
          <div className="profile-avatar">
            {previewImage || user.profile_image ? (
              <img 
                src={previewImage || user.profile_image} 
                alt="Profile" 
                className="avatar-image"
              />
            ) : (
              <div className="avatar-circle">
                {formData.username ? 
                  formData.username.charAt(0).toUpperCase() :
                  (user.email ? 
                    user.email.charAt(0).toUpperCase() :
                    (user.phone_number ? 
                      user.phone_number.slice(-1) : 
                      'U'))
                }
              </div>
            )}
            {editMode && (
              <label className="change-avatar-btn" htmlFor="profile-image">
                Change Photo
              </label>
            )}
            <input
              type="file"
              id="profile-image"
              accept="image/*"
              onChange={handleImageChange}
              style={{ display: 'none' }}
              disabled={!editMode}
            />
          </div>
          <div className="profile-info">
            <h1>
              {formData.username || user.username || 'My Account'}
            </h1>
            <p className="profile-identifier">
              {user.email || user.phone_number || 'User'}
            </p>
            <p className="profile-meta">Member since {new Date().toLocaleDateString()}</p>
          </div>
        </div>

        <div className="profile-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="profile-content">
          {activeTab === 'profile' && (
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
                        setFormData({
                          email: user.email || '',
                          phone_number: user.phone_number || '',
                          username: user.username || '',
                          profile: user.profile || '',
                        })
                        setPreviewImage(null)
                        setError('')
                        setSuccess('')
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
                    <span className="detail-value">#{user.user_id}</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'orders' && (
            <div className="profile-section">
              <div className="section-header">
                <h2>Order History</h2>
              </div>
              <div className="empty-state">
                <div className="empty-icon"><PackageIcon size={64} /></div>
                <h3>No orders yet</h3>
                <p>When you place an order, it will appear here.</p>
                <Link to="/products" className="btn-primary">
                  Start Shopping
                </Link>
              </div>
            </div>
          )}

          {activeTab === 'wishlist' && (
            <div className="profile-section">
              <div className="section-header">
                <h2>My Wishlist</h2>
              </div>
              <div className="empty-state">
                <div className="empty-icon"><HeartIcon size={64} /></div>
                <h3>Your wishlist is empty</h3>
                <p>Save items you love for later.</p>
                <Link to="/products" className="btn-primary">
                  Browse Products
                </Link>
              </div>
            </div>
          )}

          {activeTab === 'addresses' && (
            <div className="profile-section">
              <div className="section-header">
                <h2>Saved Addresses</h2>
                <button className="btn-primary">Add Address</button>
              </div>
              <div className="empty-state">
                <div className="empty-icon"><LocationIcon size={64} /></div>
                <h3>No saved addresses</h3>
                <p>Add an address for faster checkout.</p>
                <button className="btn-primary">Add Your First Address</button>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="profile-section">
              <div className="section-header">
                <h2>Account Settings</h2>
              </div>
              <div className="settings-list">
                <div className="setting-item">
                  <div className="setting-info">
                    <h3>Notifications</h3>
                    <p>Manage your email and push notifications</p>
                  </div>
                  <button className="btn-secondary">Manage</button>
                </div>
                <div className="setting-item">
                  <div className="setting-info">
                    <h3>Privacy</h3>
                    <p>Control your privacy settings</p>
                  </div>
                  <button className="btn-secondary">Manage</button>
                </div>
                <div className="setting-item">
                  <div className="setting-info">
                    <h3>Security</h3>
                    <p>Update your security preferences</p>
                  </div>
                  <button className="btn-secondary">Manage</button>
                </div>
                <div className="setting-item danger">
                  <div className="setting-info">
                    <h3>Logout</h3>
                    <p>Sign out of your account</p>
                  </div>
                  <button className="btn-danger" onClick={handleLogout}>
                    Logout
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Profile