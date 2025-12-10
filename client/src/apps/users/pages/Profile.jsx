import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import './Profile.css'
import { getUserProfile, updateUserProfile, getUserOrders, getUserWishlist, getUserAddresses, createUserAddress, updateUserAddress, deleteUserAddress } from '../services/authService'
import { UserIcon, PackageIcon, HeartIcon, LocationIcon, SettingsIcon } from '../../../common/components/Icons'
import ProfileSection from '../components/ProfileSection'
import OrdersSection from '../components/OrdersSection'
import WishlistSection from '../components/WishlistSection'
import AddressesSection from '../components/AddressesSection'
import SettingsSection from '../components/SettingsSection'

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
  
  // Orders and wishlist states
  const [orders, setOrders] = useState([])
  const [wishlistItems, setWishlistItems] = useState([])
  const [ordersLoading, setOrdersLoading] = useState(false)
  const [wishlistLoading, setWishlistLoading] = useState(false)
  const [ordersError, setOrdersError] = useState('')
  const [wishlistError, setWishlistError] = useState('')
  
  // Addresses states
  const [addresses, setAddresses] = useState([])
  const [addressesLoading, setAddressesLoading] = useState(false)
  const [addressesError, setAddressesError] = useState('')
  const [showAddAddressForm, setShowAddAddressForm] = useState(false)
  const [editingAddressId, setEditingAddressId] = useState(null)
  const [addressFormData, setAddressFormData] = useState({
    title: '',
    first_name: '',
    last_name: '',
    company: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postal_code: '',
    country: 'India',
    phone_number: '',
    is_default: false
  })
  
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

  // Fetch orders when orders tab is active
  useEffect(() => {
    if (activeTab === 'orders' && user) {
      fetchUserOrders()
    }
  }, [activeTab, user])

  // Fetch wishlist when wishlist tab is active
  useEffect(() => {
    if (activeTab === 'wishlist' && user) {
      fetchUserWishlist()
    }
  }, [activeTab, user])

  // Fetch addresses when addresses tab is active
  useEffect(() => {
    if (activeTab === 'addresses' && user) {
      fetchUserAddresses()
    }
  }, [activeTab, user])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
    setError('')
    setSuccess('')
  }

  const handleAddressInputChange = (e) => {
    const { name, value, type, checked } = e.target
    const newValue = type === 'checkbox' ? checked : value
    setAddressFormData((prev) => ({
      ...prev,
      [name]: newValue,
    }))
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

  const fetchUserOrders = async () => {
    if (ordersLoading) return
    
    setOrdersLoading(true)
    setOrdersError('')
    
    try {
      const ordersData = await getUserOrders()
      setOrders(ordersData)
    } catch (err) {
      setOrdersError(err.message || 'Failed to load orders')
    } finally {
      setOrdersLoading(false)
    }
  }

  const fetchUserWishlist = async () => {
    if (wishlistLoading) return
    
    setWishlistLoading(true)
    setWishlistError('')
    
    try {
      const wishlistData = await getUserWishlist()
      setWishlistItems(wishlistData)
    } catch (err) {
      setWishlistError(err.message || 'Failed to load wishlist')
    } finally {
      setWishlistLoading(false)
    }
  }

  const fetchUserAddresses = async () => {
    if (addressesLoading) return
    
    setAddressesLoading(true)
    setAddressesError('')
    
    try {
      const addressesData = await getUserAddresses()
      setAddresses(addressesData)
    } catch (err) {
      setAddressesError(err.message || 'Failed to load addresses')
    } finally {
      setAddressesLoading(false)
    }
  }

  const handleAddAddress = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    
    try {
      const newAddress = await createUserAddress(addressFormData)
      setAddresses([...addresses, newAddress])
      setShowAddAddressForm(false)
      setAddressFormData({
        title: '',
        first_name: '',
        last_name: '',
        company: '',
        address_line1: '',
        address_line2: '',
        city: '',
        state: '',
        postal_code: '',
        country: 'India',
        phone_number: '',
        is_default: false
      })
      setSuccess('Address added successfully!')
    } catch (err) {
      setError(err.message || 'Failed to add address. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleUpdateAddress = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    
    try {
      const updatedAddress = await updateUserAddress(editingAddressId, addressFormData)
      setAddresses(addresses.map(addr => addr.id === editingAddressId ? updatedAddress : addr))
      setEditingAddressId(null)
      setAddressFormData({
        title: '',
        first_name: '',
        last_name: '',
        company: '',
        address_line1: '',
        address_line2: '',
        city: '',
        state: '',
        postal_code: '',
        country: 'India',
        phone_number: '',
        is_default: false
      })
      setSuccess('Address updated successfully!')
    } catch (err) {
      setError(err.message || 'Failed to update address. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteAddress = async (addressId) => {
    if (!window.confirm('Are you sure you want to delete this address?')) {
      return
    }
    
    try {
      await deleteUserAddress(addressId)
      setAddresses(addresses.filter(addr => addr.id !== addressId))
      setSuccess('Address deleted successfully!')
    } catch (err) {
      setError(err.message || 'Failed to delete address. Please try again.')
    }
  }

  const handleEditAddress = (address) => {
    setEditingAddressId(address.id)
    setAddressFormData({
      title: address.title || '',
      first_name: address.first_name || '',
      last_name: address.last_name || '',
      company: address.company || '',
      address_line1: address.address_line1 || '',
      address_line2: address.address_line2 || '',
      city: address.city || '',
      state: address.state || '',
      postal_code: address.postal_code || '',
      country: address.country || 'India',
      phone_number: address.phone_number || '',
      is_default: address.is_default || false
    })
  }

  const handleCancelEditAddress = () => {
    setEditingAddressId(null)
    setAddressFormData({
      title: '',
      first_name: '',
      last_name: '',
      company: '',
      address_line1: '',
      address_line2: '',
      city: '',
      state: '',
      postal_code: '',
      country: 'India',
      phone_number: '',
      is_default: false
    })
  }

  const getImageUrl = (image) => {
    if (!image) return '/placeholder-product.png'
    if (image.startsWith('http')) return image
    return `http://localhost:8000${image}`
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'delivered': return 'status-success'
      case 'shipped': return 'status-info'
      case 'processing': return 'status-warning'
      case 'cancelled': return 'status-danger'
      default: return 'status-default'
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
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
            <ProfileSection
              user={user}
              editMode={editMode}
              setEditMode={setEditMode}
              formData={formData}
              handleInputChange={handleInputChange}
              handleSaveProfile={handleSaveProfile}
              handleImageChange={handleImageChange}
              previewImage={previewImage}
              error={error}
              success={success}
              saving={saving}
              setSuccess={setSuccess}
              setError={setError}
            />
          )}

          {activeTab === 'orders' && (
            <OrdersSection
              orders={orders}
              ordersLoading={ordersLoading}
              ordersError={ordersError}
              fetchUserOrders={fetchUserOrders}
            />
          )}

          {activeTab === 'wishlist' && (
            <WishlistSection
              wishlistItems={wishlistItems}
              wishlistLoading={wishlistLoading}
              wishlistError={wishlistError}
              fetchUserWishlist={fetchUserWishlist}
            />
          )}

          {activeTab === 'addresses' && (
            <AddressesSection
              addresses={addresses}
              addressesLoading={addressesLoading}
              addressesError={addressesError}
              fetchUserAddresses={fetchUserAddresses}
              handleAddAddress={handleAddAddress}
              handleUpdateAddress={handleUpdateAddress}
              handleDeleteAddress={handleDeleteAddress}
              handleEditAddress={handleEditAddress}
              setShowAddAddressForm={setShowAddAddressForm}
              showAddAddressForm={showAddAddressForm}
              editingAddressId={editingAddressId}
              addressFormData={addressFormData}
              handleAddressInputChange={handleAddressInputChange}
              handleCancelEditAddress={handleCancelEditAddress}
              saving={saving}
              error={error}
              success={success}
              setError={setError}
              setSuccess={setSuccess}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsSection
              handleLogout={handleLogout}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default Profile