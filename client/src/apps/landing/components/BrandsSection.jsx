import { useState, useEffect, useRef } from 'react'

const BrandsSection = ({ brands }) => {
  const trackRef = useRef(null)
  const intervalRef = useRef(null)
  const [isHovered, setIsHovered] = useState(false)
  const [itemsToShow, setItemsToShow] = useState(6)
  const [index, setIndex] = useState(0)

  // Duplicate brands for infinite loop
  const infiniteBrands = [...brands, ...brands]

  // Responsive items count
  useEffect(() => {
    const updateItems = () => {
      if (window.innerWidth < 640) setItemsToShow(2)
      else if (window.innerWidth < 1024) setItemsToShow(4)
      else setItemsToShow(6)
    }

    updateItems()
    window.addEventListener('resize', updateItems)
    return () => window.removeEventListener('resize', updateItems)
  }, [])

  // Auto slide
  useEffect(() => {
    if (isHovered || brands.length === 0) return

    intervalRef.current = setInterval(() => {
      setIndex(prev => prev + 1)
    }, 2500)

    return () => clearInterval(intervalRef.current)
  }, [isHovered, brands])

  // Reset position seamlessly
  useEffect(() => {
    if (index === brands.length) {
      setTimeout(() => {
        trackRef.current.style.transition = 'none'
        setIndex(0)
        trackRef.current.style.transform = `translateX(0)`
      }, 500)
    } else {
      trackRef.current.style.transition = 'transform 0.5s ease-in-out'
    }
  }, [index, brands.length])

  if (!brands || brands.length === 0) return null

  const itemWidth = 100 / itemsToShow

  return (
    <section className="brands-section">
      <h2 className="section-title">Popular Brands</h2>

      <div
        className="brands-carousel-wrapper"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        <div className="brands-carousel">
          <div
            ref={trackRef}
            className="brands-carousel-track"
            style={{
              transform: `translateX(-${index * itemWidth}%)`,
            }}
          >
            {infiniteBrands.map((brand, i) => (
              <div
                key={`${brand.id}-${i}`}
                className="brand-carousel-item"
                style={{ width: `${itemWidth}%` }}
              >
                <div className="brand-card">
                  {brand.logo ? (
                    <img
                      src={brand.logo}
                      alt={brand.name}
                      className="brand-logo"
                    />
                  ) : (
                    <div className="brand-placeholder">{brand.name}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

export default BrandsSection
