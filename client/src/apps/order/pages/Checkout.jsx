import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { getCartItems } from '../../cart/services/cartService'
import { checkout } from '../services/orderService'
import { getUserProfile } from '../../users/services/authService'
import { getUserAddresses } from '../../users/services/authService'
import './Checkout.css'

function Checkout() {
  const navigate = useNavigate()
  const location = useLocation()
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [cartItems, setCartItems] = useState([])
  const [user, setUser] = useState(null)
  const [savedAddresses, setSavedAddresses] = useState([])
  const [showSavedAddresses, setShowSavedAddresses] = useState(false)
  
  // Form state
  const [formData, setFormData] = useState({
    // Customer info
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    
    // Billing address
    billing_address_line1: '',
    billing_address_line2: '',
    billing_city: '',
    billing_state: '',
    billing_postal_code: '',
    billing_country: 'India',
    
    // Shipping address
    shipping_address_line1: '',
    shipping_address_line2: '',
    shipping_city: '',
    shipping_state: '',
    shipping_postal_code: '',
    shipping_country: 'India',
    use_same_address: true,
    
    // Payment
    payment_method: 'cash_on_delivery',
    
    // Notes
    notes: '',
  })

  useEffect(() => {
    loadCheckoutData()
  }, [])

  useEffect(() => {
    // Auto-fill shipping address if use_same_address is true
    if (formData.use_same_address) {
      setFormData(prev => ({
        ...prev,
        shipping_address_line1: prev.billing_address_line1,
        shipping_address_line2: prev.billing_address_line2,
        shipping_city: prev.billing_city,
        shipping_state: prev.billing_state,
        shipping_postal_code: prev.billing_postal_code,
        shipping_country: prev.billing_country,
      }))
    }
  }, [formData.use_same_address, formData.billing_address_line1, formData.billing_city, formData.billing_state, formData.billing_postal_code, formData.billing_country])

  const loadCheckoutData = async () => {
    try {
      setLoading(true)
      setError('')
      
      // Load cart items from state (selective checkout) or fetch all
      if (location.state?.selectedItems) {
        setCartItems(location.state.selectedItems)
      } else {
        const items = await getCartItems()
        setCartItems(items)
      }
      
      // Load user profile if available
      try {
        const userData = sessionStorage.getItem('user')
        if (userData) {
          const parsedUser = JSON.parse(userData)
          setUser(parsedUser)
          
          // Pre-fill form with user data
          setFormData(prev => ({
            ...prev,
            first_name: parsedUser.first_name || '',
            last_name: parsedUser.last_name || '',
            email: parsedUser.email || '',
            phone_number: parsedUser.phone_number || '',
          }))
        }
      } catch (err) {
        console.error('Failed to load user data:', err)
      }
      
      // Load saved addresses
      try {
        const addresses = await getUserAddresses()
        setSavedAddresses(addresses)
        if (addresses.length > 0) {
          setShowSavedAddresses(true)
        }
      } catch (err) {
        console.error('Failed to load saved addresses:', err)
      }
    } catch (err) {
      if (err.message.includes('401') || err.message.includes('Authentication')) {
        navigate('/login', { state: { from: '/checkout' } })
        return
      }
      setError(err.message || 'Failed to load checkout data')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
    setError('')
  }

  const handleAddressSelect = (address) => {
    // Populate both billing and shipping addresses with the selected address
    setFormData(prev => ({
      ...prev,
      // Billing address
      first_name: address.first_name,
      last_name: address.last_name,
      billing_address_line1: address.address_line1,
      billing_address_line2: address.address_line2,
      billing_city: address.city,
      billing_state: address.state,
      billing_postal_code: address.postal_code,
      billing_country: address.country,
      phone_number: address.phone_number,
      
      // Shipping address
      shipping_address_line1: address.address_line1,
      shipping_address_line2: address.address_line2,
      shipping_city: address.city,
      shipping_state: address.state,
      shipping_postal_code: address.postal_code,
      shipping_country: address.country,
    }))
    
    setShowSavedAddresses(false)
  }

  // Calculate order totals
  const calculateTotals = () => {
    const subtotal = cartItems.reduce((sum, item) => {
      return sum + (parseFloat(item.price) * item.quantity)
    }, 0)
    
    const VAT_RATE = 0.12 // 12% VAT
    const taxAmount = subtotal * VAT_RATE
    const shippingCost = 0 // Free shipping for now, can be calculated based on address
    const totalAmount = subtotal + taxAmount + shippingCost
    
    return {
      subtotal,
      taxAmount,
      shippingCost,
      totalAmount,
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    // Validation
    if (cartItems.length === 0) {
      setError('Your cart is empty. Please add items to your cart first.')
      setSubmitting(false)
      return
    }

    if (!formData.first_name || !formData.last_name || !formData.email || !formData.phone_number) {
      setError('Please fill in all required customer information fields.')
      setSubmitting(false)
      return
    }

    if (!formData.billing_address_line1 || !formData.billing_city || !formData.billing_state || !formData.billing_postal_code) {
      setError('Please fill in all required billing address fields.')
      setSubmitting(false)
      return
    }

    if (!formData.use_same_address) {
      if (!formData.shipping_address_line1 || !formData.shipping_city || !formData.shipping_state || !formData.shipping_postal_code) {
        setError('Please fill in all required shipping address fields.')
        setSubmitting(false)
        return
      }
    }

    try {
      const totals = calculateTotals()
      
      // Prepare checkout data
      const checkoutData = {
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        phone_number: formData.phone_number,
        billing_address_line1: formData.billing_address_line1,
        billing_address_line2: formData.billing_address_line2 || '',
        billing_city: formData.billing_city,
        billing_state: formData.billing_state,
        billing_postal_code: formData.billing_postal_code,
        billing_country: formData.billing_country,
        shipping_address_line1: formData.shipping_address_line1,
        shipping_address_line2: formData.shipping_address_line2 || '',
        shipping_city: formData.shipping_city,
        shipping_state: formData.shipping_state,
        shipping_postal_code: formData.shipping_postal_code,
        shipping_country: formData.shipping_country,
        payment_method: formData.payment_method,
        notes: formData.notes || '',
        items: cartItems.map(item => ({
          product_id: item.product.id,
          quantity: item.quantity,
        })),
      }

      const response = await checkout(checkoutData)
      
      // Redirect to order confirmation page
      navigate(`/order-confirmation/${response.order_number}`, { replace: true })
    } catch (err) {
      setError(err.message || 'Failed to place order. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="checkout-page">
        <div className="checkout-container">
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading checkout...</p>
          </div>
        </div>
      </div>
    )
  }

  if (cartItems.length === 0) {
    return (
      <div className="checkout-page">
        <div className="checkout-container">
          <div className="empty-cart">
            <h2>Your cart is empty</h2>
            <p>Please add items to your cart before checkout.</p>
            <button onClick={() => navigate('/cart')} className="btn-primary">
              Go to Cart
            </button>
          </div>
        </div>
      </div>
    )
  }

  const totals = calculateTotals()

  return (
    <div className="checkout-page">
      <div className="checkout-container">
        <h1>Checkout</h1>

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

        <form onSubmit={handleSubmit} className="checkout-form">
          <div className="checkout-content">
            <div className="checkout-main">
              {/* Saved Addresses Section */}
              {showSavedAddresses && savedAddresses.length > 0 && (
                <section className="checkout-section">
                  <h2>Saved Addresses</h2>
                  <div className="saved-addresses-list">
                    {savedAddresses.map((address) => (
                      <div key={address.id} className="saved-address-card" onClick={() => handleAddressSelect(address)}>
                        <div className="saved-address-header">
                          <h3>{address.title}</h3>
                          {address.is_default && <span className="default-badge">Default</span>}
                        </div>
                        <div className="saved-address-body">
                          <p className="saved-address-name">{address.first_name} {address.last_name}</p>
                          <p className="saved-address-street">{address.address_line1}</p>
                          {address.address_line2 && <p className="saved-address-street">{address.address_line2}</p>}
                          <p className="saved-address-city">
                            {address.city}, {address.state} {address.postal_code}
                          </p>
                          <p className="saved-address-country">{address.country}</p>
                          <p className="saved-address-phone">{address.phone_number}</p>
                        </div>
                        <div className="saved-address-select">
                          <span>Use this address</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <button 
                    type="button" 
                    className="btn-secondary"
                    onClick={() => setShowSavedAddresses(false)}
                  >
                    Enter Address Manually
                  </button>
                </section>
              )}

              {/* Customer Information */}
              <section className="checkout-section">
                <h2>Customer Information</h2>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="first_name">First Name *</label>
                    <input
                      type="text"
                      id="first_name"
                      name="first_name"
                      value={formData.first_name}
                      onChange={handleInputChange}
                      required
                      disabled={submitting}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="last_name">Last Name *</label>
                    <input
                      type="text"
                      id="last_name"
                      name="last_name"
                      value={formData.last_name}
                      onChange={handleInputChange}
                      required
                      disabled={submitting}
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="email">Email *</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      required
                      disabled={submitting}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="phone_number">Phone Number *</label>
                    <input
                      type="tel"
                      id="phone_number"
                      name="phone_number"
                      value={formData.phone_number}
                      onChange={handleInputChange}
                      required
                      disabled={submitting}
                    />
                  </div>
                </div>
              </section>

              {/* Billing Address */}
              <section className="checkout-section">
                <h2>Billing Address</h2>
                <div className="form-group">
                  <label htmlFor="billing_address_line1">Address Line 1 *</label>
                  <input
                    type="text"
                    id="billing_address_line1"
                    name="billing_address_line1"
                    value={formData.billing_address_line1}
                    onChange={handleInputChange}
                    required
                    disabled={submitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="billing_address_line2">Address Line 2</label>
                  <input
                    type="text"
                    id="billing_address_line2"
                    name="billing_address_line2"
                    value={formData.billing_address_line2}
                    onChange={handleInputChange}
                    disabled={submitting}
                  />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="billing_city">City *</label>
                    <input
                      type="text"
                      id="billing_city"
                      name="billing_city"
                      value={formData.billing_city}
                      onChange={handleInputChange}
                      required
                      disabled={submitting}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="billing_state">State *</label>
                    <input
                      type="text"
                      id="billing_state"
                      name="billing_state"
                      value={formData.billing_state}
                      onChange={handleInputChange}
                      required
                      disabled={submitting}
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="billing_postal_code">Postal Code *</label>
                    <input
                      type="text"
                      id="billing_postal_code"
                      name="billing_postal_code"
                      value={formData.billing_postal_code}
                      onChange={handleInputChange}
                      required
                      disabled={submitting}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="billing_country">Country *</label>
                    <input
                      type="text"
                      id="billing_country"
                      name="billing_country"
                      value={formData.billing_country}
                      onChange={handleInputChange}
                      required
                      disabled={submitting}
                    />
                  </div>
                </div>
              </section>

              {/* Shipping Address */}
              <section className="checkout-section">
                <h2>Shipping Address</h2>
                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      name="use_same_address"
                      checked={formData.use_same_address}
                      onChange={handleInputChange}
                      disabled={submitting}
                    />
                    <span>Use same address as billing</span>
                  </label>
                </div>
                <div className="form-group">
                  <label htmlFor="shipping_address_line1">Address Line 1 *</label>
                  <input
                    type="text"
                    id="shipping_address_line1"
                    name="shipping_address_line1"
                    value={formData.shipping_address_line1}
                    onChange={handleInputChange}
                    required
                    disabled={submitting || formData.use_same_address}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="shipping_address_line2">Address Line 2</label>
                  <input
                    type="text"
                    id="shipping_address_line2"
                    name="shipping_address_line2"
                    value={formData.shipping_address_line2}
                    onChange={handleInputChange}
                    disabled={submitting || formData.use_same_address}
                  />
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="shipping_city">City *</label>
                    <input
                      type="text"
                      id="shipping_city"
                      name="shipping_city"
                      value={formData.shipping_city}
                      onChange={handleInputChange}
                      required
                      disabled={submitting || formData.use_same_address}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="shipping_state">State *</label>
                    <input
                      type="text"
                      id="shipping_state"
                      name="shipping_state"
                      value={formData.shipping_state}
                      onChange={handleInputChange}
                      required
                      disabled={submitting || formData.use_same_address}
                    />
                  </div>
                </div>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="shipping_postal_code">Postal Code *</label>
                    <input
                      type="text"
                      id="shipping_postal_code"
                      name="shipping_postal_code"
                      value={formData.shipping_postal_code}
                      onChange={handleInputChange}
                      required
                      disabled={submitting || formData.use_same_address}
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="shipping_country">Country *</label>
                    <input
                      type="text"
                      id="shipping_country"
                      name="shipping_country"
                      value={formData.shipping_country}
                      onChange={handleInputChange}
                      required
                      disabled={submitting || formData.use_same_address}
                    />
                  </div>
                </div>
              </section>

              {/* Payment Method */}
              <section className="checkout-section">
                <h2>Payment Method</h2>
                <div className="payment-methods">
                  <label className="payment-option">
                    <input
                      type="radio"
                      name="payment_method"
                      value="cash_on_delivery"
                      checked={formData.payment_method === 'cash_on_delivery'}
                      onChange={handleInputChange}
                      disabled={submitting}
                    />
                    <div className="payment-option-content">
                      <span className="payment-option-title">Cash on Delivery (COD)</span>
                      <span className="payment-option-desc">Pay when you receive your order</span>
                    </div>
                  </label>
                  <label className="payment-option">
                    <input
                      type="radio"
                      name="payment_method"
                      value="bank_transfer"
                      checked={formData.payment_method === 'bank_transfer'}
                      onChange={handleInputChange}
                      disabled={submitting}
                    />
                    <div className="payment-option-content">
                      <span className="payment-option-title">Bank Transfer</span>
                      <span className="payment-option-desc">Transfer funds directly to our bank account</span>
                    </div>
                  </label>
                </div>
              </section>

              {/* Order Notes */}
              <section className="checkout-section">
                <h2>Order Notes (Optional)</h2>
                <div className="form-group">
                  <textarea
                    id="notes"
                    name="notes"
                    value={formData.notes}
                    onChange={handleInputChange}
                    rows="4"
                    placeholder="Any special instructions for your order..."
                    disabled={submitting}
                  />
                </div>
              </section>
            </div>

            {/* Order Summary */}
            <aside className="checkout-summary">
              <div className="summary-card">
                <h2>Order Summary</h2>
                <div className="summary-items">
                  {cartItems.map((item) => (
                    <div key={item.id} className="summary-item">
                      <div className="summary-item-info">
                        <span className="summary-item-name">{item.product_name}</span>
                        <span className="summary-item-qty">Qty: {item.quantity}</span>
                      </div>
                      <span className="summary-item-price">
                        ₹{(parseFloat(item.price) * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
                <div className="summary-divider"></div>
                <div className="summary-row">
                  <span>Subtotal</span>
                  <span>₹{totals.subtotal.toFixed(2)}</span>
                </div>
                <div className="summary-row">
                  <span>VAT (12%)</span>
                  <span>₹{totals.taxAmount.toFixed(2)}</span>
                </div>
                <div className="summary-row">
                  <span>Shipping</span>
                  <span>₹{totals.shippingCost.toFixed(2)}</span>
                </div>
                <div className="summary-divider"></div>
                <div className="summary-row summary-total">
                  <span>Total</span>
                  <span>₹{totals.totalAmount.toFixed(2)}</span>
                </div>
                <button
                  type="submit"
                  className="btn-place-order"
                  disabled={submitting}
                >
                  {submitting ? (
                    <>
                      <span className="spinner-small"></span>
                      Placing Order...
                    </>
                  ) : (
                    'Place Order'
                  )}
                </button>
              </div>
            </aside>
          </div>
        </form>
      </div>
    </div>
  )
}

export default Checkout