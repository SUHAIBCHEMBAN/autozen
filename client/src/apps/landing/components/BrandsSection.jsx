import { useState, useEffect, useRef } from 'react'

const BrandsSection = ({ brands }) => {
  const [currentIndex, setCurrentIndex] = useState(0)
  const intervalRef = useRef(null)

  // Log brands data for debugging
  useEffect(() => {
    console.log('Brands data received:', brands);
    console.log('Number of brands:', brands?.length);
  }, [brands]);

  // Auto-slide functionality - show 6 brands at a time
  useEffect(() => {
    if (!brands || brands.length === 0) {
      console.log('No brands to display');
      return;
    }
    
    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    
    // Show 6 brands at a time for sliding effect
    const brandsToShow = 6;
    console.log('Brands to show:', brandsToShow);
    console.log('Total brands:', brands.length);
    
    // Set up interval for sliding
    intervalRef.current = setInterval(() => {
      setCurrentIndex(prevIndex => {
        console.log('Current index:', prevIndex);
        // Move to next index (sliding left to right)
        // Always slide if we have more than brandsToShow
        if (brands.length > brandsToShow) {
          const newIndex = prevIndex >= brands.length - brandsToShow ? 0 : prevIndex + 1;
          console.log('Moving to index:', newIndex);
          return newIndex;
        } else {
          // If we have fewer brands than we can show, just reset to 0 (no visible change)
          console.log('Not enough brands to slide, resetting to index: 0');
          return 0;
        }
      })
    }, 3000) // Slide every 3 seconds
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [brands])

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      console.log('Window resized, resetting carousel position');
      setCurrentIndex(0); // Reset carousel position on resize
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (!brands || brands.length === 0) {
    return null
  }

  // Show 6 brands at a time
  const brandsToShow = 6;
  const brandWidth = 100 / brandsToShow;
  
  console.log('Rendering with currentIndex:', currentIndex, 'brandWidth:', brandWidth);

  return (
    <section className="brands-section">
      <div className="container">
        <h2 className="section-title">Popular Brands</h2>
        <div className="brands-carousel-wrapper">
          <div className="brands-carousel">
            <div 
              className="brands-carousel-track"
              style={{
                transform: `translateX(-${currentIndex * brandWidth}%)`,
                transition: 'transform 0.5s ease-in-out'
              }}
            >
              {brands.map((brand, index) => (
                <div key={`${brand.id}-${index}`} className="brand-carousel-item">
                  <div className="brand-card">
                    {brand.logo ? (
                      <img 
                        src={brand.logo} 
                        alt={brand.name}
                        className="brand-logo"
                        onError={(e) => { 
                          console.log('Image load error for brand:', brand.name, 'URL:', e.target.src);
                          e.target.style.display = 'none';
                        }}
                      />
                    ) : (
                      <div className="brand-placeholder">
                        {brand.name}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

export default BrandsSection