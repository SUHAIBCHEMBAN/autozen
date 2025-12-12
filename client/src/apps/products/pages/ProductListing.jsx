import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { getProducts, searchProducts } from '../services/productsService'
import ProductCard from '../components/ProductCard'
import ProductFilters from '../components/ProductFilters'
import './ProductListing.css'

function ProductListing() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '')
  
  const [filters, setFilters] = useState({
    brand: searchParams.get('brand') || null,
    vehicle_model: searchParams.get('vehicle_model') || null,
    part_category: searchParams.get('part_category') || null,
    is_featured: searchParams.get('is_featured') === 'true' ? true : null,
    in_stock: searchParams.get('in_stock') === 'true' ? true : null,
    ordering: searchParams.get('ordering') || null,
  })

  // Update searchQuery when URL changes
  useEffect(() => {
    const query = searchParams.get('q') || ''
    setSearchQuery(query)
  }, [searchParams])

  useEffect(() => {
    loadProducts()
  }, [filters, searchQuery])

  const loadProducts = async () => {
    try {
      setLoading(true)
      setError('')

      let data
      if (searchQuery) {
        data = await searchProducts(searchQuery)
      } else {
        // Build query params
        const params = {}
        if (filters.brand) params.brand = filters.brand
        if (filters.vehicle_model) params.vehicle_model = filters.vehicle_model
        if (filters.part_category) params.part_category = filters.part_category
        if (filters.is_featured) params.is_featured = true
        if (filters.ordering) params.ordering = filters.ordering

        data = await getProducts(params)
      }

      // Filter in stock if needed
      if (filters.in_stock && !searchQuery) {
        data = data.filter((product) => product.is_in_stock)
      }

      setProducts(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Failed to load products')
      setProducts([])
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (filterType, value) => {
    setFilters((prev) => ({
      ...prev,
      [filterType]: value,
    }))

    // Update URL params
    const newParams = new URLSearchParams(searchParams)
    if (value) {
      newParams.set(filterType, value)
    } else {
      newParams.delete(filterType)
    }
    setSearchParams(newParams)
  }

  const handleClearFilters = () => {
    setFilters({
      brand: null,
      vehicle_model: null,
      part_category: null,
      is_featured: null,
      in_stock: null,
      ordering: null,
    })
    setSearchQuery('')
    setSearchParams({})
  }

  const handleSearch = (e) => {
    e.preventDefault()
    const newParams = new URLSearchParams(searchParams)
    if (searchQuery) {
      newParams.set('q', searchQuery)
    } else {
      newParams.delete('q')
    }
    setSearchParams(newParams)
  }

  return (
    <div className="product-listing-page">
      <div className="product-listing-container">
        {/* <div className="listing-header">
          <h1>Products</h1>
          <p>Browse our collection of automotive parts and accessories</p>
        </div> */}

        <form onSubmit={handleSearch} className="search-bar">
          <input
            type="text"
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button">
            Search
          </button>
        </form>

        <div className="listing-content">
          <aside className="filters-sidebar">
            <ProductFilters
              filters={filters}
              onFilterChange={handleFilterChange}
              onClearFilters={handleClearFilters}
            />
          </aside>

          <main className="products-grid-wrapper">
            {loading ? (
              <div className="loading-state">
                <div className="spinner"></div>
                <p>Loading products...</p>
              </div>
            ) : error ? (
              <div className="error-state">
                <p>{error}</p>
                <button onClick={loadProducts} className="btn-primary">
                  Try Again
                </button>
              </div>
            ) : products.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">🔍</div>
                <h3>No products found</h3>
                <p>Try adjusting your filters or search query</p>
                <button onClick={handleClearFilters} className="btn-primary">
                  Clear Filters
                </button>
              </div>
            ) : (
              <>
                <div className="results-header">
                  <p className="results-count">
                    {products.length} {products.length === 1 ? 'product' : 'products'} found
                  </p>
                </div>
                <div className="products-grid">
                  {products.map((product) => (
                    <ProductCard key={product.id} product={product} />
                  ))}
                </div>
              </>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}

export default ProductListing

