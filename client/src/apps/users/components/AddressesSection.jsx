import { useState } from 'react'
import { LocationIcon } from '../../../common/components/Icons'

function AddressesSection({ 
  addresses, 
  addressesLoading, 
  addressesError, 
  fetchUserAddresses,
  handleAddAddress,
  handleUpdateAddress,
  handleDeleteAddress,
  handleEditAddress,
  setShowAddAddressForm,
  showAddAddressForm,
  editingAddressId,
  addressFormData,
  handleAddressInputChange,
  handleCancelEditAddress,
  saving,
  error,
  success,
  setError,
  setSuccess
}) {
  return (
    <div className="profile-section">
      <div className="section-header">
        <h2>Saved Addresses</h2>
        <button 
          className="btn-primary" 
          onClick={() => {
            setShowAddAddressForm(true)
            setSuccess('')
            setError('')
          }}
        >
          Add Address
        </button>
      </div>

      {(error || success) && (
        <div className={`alert ${error ? 'alert-error' : 'alert-success'}`} role="alert">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {error ? (
              <>
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </>
            ) : (
              <>
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </>
            )}
          </svg>
          <span>{error || success}</span>
        </div>
      )}

      {showAddAddressForm || editingAddressId ? (
        <form 
          onSubmit={editingAddressId ? handleUpdateAddress : handleAddAddress} 
          className="address-form"
        >
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="title">Address Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={addressFormData.title}
                onChange={handleAddressInputChange}
                placeholder="e.g., Home, Work"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="is_default">
                <input
                  type="checkbox"
                  id="is_default"
                  name="is_default"
                  checked={addressFormData.is_default}
                  onChange={handleAddressInputChange}
                />
                Set as default address
              </label>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="first_name">First Name *</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={addressFormData.first_name}
                onChange={handleAddressInputChange}
                placeholder="First name"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="last_name">Last Name *</label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={addressFormData.last_name}
                onChange={handleAddressInputChange}
                placeholder="Last name"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="company">Company (Optional)</label>
            <input
              type="text"
              id="company"
              name="company"
              value={addressFormData.company}
              onChange={handleAddressInputChange}
              placeholder="Company name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="address_line1">Address Line 1 *</label>
            <input
              type="text"
              id="address_line1"
              name="address_line1"
              value={addressFormData.address_line1}
              onChange={handleAddressInputChange}
              placeholder="Street address"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="address_line2">Address Line 2 (Optional)</label>
            <input
              type="text"
              id="address_line2"
              name="address_line2"
              value={addressFormData.address_line2}
              onChange={handleAddressInputChange}
              placeholder="Apartment, suite, etc."
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="city">City *</label>
              <input
                type="text"
                id="city"
                name="city"
                value={addressFormData.city}
                onChange={handleAddressInputChange}
                placeholder="City"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="state">State *</label>
              <input
                type="text"
                id="state"
                name="state"
                value={addressFormData.state}
                onChange={handleAddressInputChange}
                placeholder="State"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="postal_code">Postal Code *</label>
              <input
                type="text"
                id="postal_code"
                name="postal_code"
                value={addressFormData.postal_code}
                onChange={handleAddressInputChange}
                placeholder="Postal code"
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="country">Country *</label>
              <select
                id="country"
                name="country"
                value={addressFormData.country}
                onChange={handleAddressInputChange}
                required
              >
                <option value="India">India</option>
                <option value="United States">United States</option>
                <option value="United Kingdom">United Kingdom</option>
                <option value="Canada">Canada</option>
                <option value="Australia">Australia</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="phone_number">Phone Number *</label>
            <input
              type="tel"
              id="phone_number"
              name="phone_number"
              value={addressFormData.phone_number}
              onChange={handleAddressInputChange}
              placeholder="+1234567890"
              required
            />
          </div>

          <div className="form-actions">
            <button
              type="button"
              className="btn-secondary"
              onClick={handleCancelEditAddress}
              disabled={saving}
            >
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? (
                <>
                  <span className="spinner-small"></span>
                  {editingAddressId ? 'Updating...' : 'Adding...'}
                </>
              ) : (
                editingAddressId ? 'Update Address' : 'Add Address'
              )}
            </button>
          </div>
        </form>
      ) : addressesLoading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading addresses...</p>
        </div>
      ) : addressesError ? (
        <div className="error-state">
          <p>{addressesError}</p>
          <button onClick={fetchUserAddresses} className="btn-primary">
            Try Again
          </button>
        </div>
      ) : addresses.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon"><LocationIcon size={64} /></div>
          <h3>No saved addresses</h3>
          <p>Add an address for faster checkout.</p>
          <button 
            className="btn-primary"
            onClick={() => setShowAddAddressForm(true)}
          >
            Add Your First Address
          </button>
        </div>
      ) : (
        <div className="addresses-list">
          {addresses.map((address) => (
            <div key={address.id} className="address-card">
              <div className="address-card-header">
                <h3>{address.title}</h3>
                {address.is_default && (
                  <span className="default-badge">Default</span>
                )}
              </div>
              <div className="address-card-body">
                <p className="address-name">{address.first_name} {address.last_name}</p>
                {address.company && <p className="address-company">{address.company}</p>}
                <p className="address-street">{address.address_line1}</p>
                {address.address_line2 && <p className="address-street">{address.address_line2}</p>}
                <p className="address-city">
                  {address.city}, {address.state} {address.postal_code}
                </p>
                <p className="address-country">{address.country}</p>
                <p className="address-phone">{address.phone_number}</p>
              </div>
              <div className="address-card-footer">
                <button 
                  className="btn-secondary"
                  onClick={() => handleEditAddress(address)}
                >
                  Edit
                </button>
                <button 
                  className="btn-danger"
                  onClick={() => handleDeleteAddress(address.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AddressesSection