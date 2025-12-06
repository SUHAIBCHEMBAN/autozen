import { useState, useEffect } from 'react'
import { getBrands, getVehicleModels, getParentCategories } from '../services/productsService'
import './ProductFilters.css'

function ProductFilters({ filters, onFilterChange, onClearFilters }) {
  const [brands, setBrands] = useState([])
  const [models, setModels] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadFilters = async () => {
      try {
        setLoading(true)
        const [brandsData, modelsData, categoriesData] = await Promise.all([
          getBrands(),
          getVehicleModels(),
          getParentCategories(),
        ])
        setBrands(brandsData)
        setModels(modelsData)
        setCategories(categoriesData)
      } catch (error) {
        console.error('Error loading filters:', error)
      } finally {
        setLoading(false)
      }
    }

    loadFilters()
  }, [])

  const handleFilterChange = (filterType, value) => {
    onFilterChange(filterType, value)
  }

  const hasActiveFilters = filters.brand || filters.vehicle_model || filters.part_category

  if (loading) {
    return (
      <div className="product-filters">
        <div className="filters-loading">Loading filters...</div>
      </div>
    )
  }

  return (
    <div className="product-filters">
      <div className="filters-header">
        <h3>Filters</h3>
        {hasActiveFilters && (
          <button className="clear-filters-btn" onClick={onClearFilters}>
            Clear All
          </button>
        )}
      </div>

      <div className="filters-content">
        <div className="filter-group">
          <label className="filter-label">Brand</label>
          <select
            className="filter-select"
            value={filters.brand || ''}
            onChange={(e) => handleFilterChange('brand', e.target.value || null)}
          >
            <option value="">All Brands</option>
            {brands.map((brand) => (
              <option key={brand.id} value={brand.id}>
                {brand.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Vehicle Model</label>
          <select
            className="filter-select"
            value={filters.vehicle_model || ''}
            onChange={(e) => handleFilterChange('vehicle_model', e.target.value || null)}
          >
            <option value="">All Models</option>
            {models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Category</label>
          <select
            className="filter-select"
            value={filters.part_category || ''}
            onChange={(e) => handleFilterChange('part_category', e.target.value || null)}
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Sort By</label>
          <select
            className="filter-select"
            value={filters.ordering || ''}
            onChange={(e) => handleFilterChange('ordering', e.target.value || null)}
          >
            <option value="">Default</option>
            <option value="name">Name (A-Z)</option>
            <option value="-name">Name (Z-A)</option>
            <option value="price">Price (Low to High)</option>
            <option value="-price">Price (High to Low)</option>
            <option value="-created_at">Newest First</option>
            <option value="created_at">Oldest First</option>
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.is_featured || false}
              onChange={(e) => handleFilterChange('is_featured', e.target.checked ? true : null)}
            />
            <span>Featured Only</span>
          </label>
        </div>

        <div className="filter-group">
          <label className="filter-checkbox">
            <input
              type="checkbox"
              checked={filters.in_stock || false}
              onChange={(e) => handleFilterChange('in_stock', e.target.checked ? true : null)}
            />
            <span>In Stock Only</span>
          </label>
        </div>
      </div>
    </div>
  )
}

export default ProductFilters

