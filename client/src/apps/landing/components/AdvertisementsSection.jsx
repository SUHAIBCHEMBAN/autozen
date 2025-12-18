import React, { useState, useEffect } from 'react';

const AdvertisementsSection = ({ advertisements }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  // Helper function to get image URL
  const getImageUrl = (image) => {
    if (!image) return '/placeholder-ad.jpg';

    if (image.startsWith('http://') || image.startsWith('https://')) {
      return image;
    }

    if (image.startsWith('/media/')) {
      return `http://localhost:8000${image}`;
    }

    if (!image.startsWith('/')) {
      return `http://localhost:8000/media/${image}`;
    }

    return `http://localhost:8000${image}`;
  };

  // Auto-slide effect
  useEffect(() => {
    if (!advertisements || advertisements.length <= 1) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % advertisements.length);
    }, 5000); // Change slide every 5 seconds

    return () => clearInterval(interval);
  }, [advertisements]);

  if (!advertisements || advertisements.length === 0) {
    return null;
  }

  const currentAd = advertisements[currentIndex];

  return (
    <section className="advertisements-section">
      <div className="ad-banner-container">
        {advertisements.map((ad, index) => (
          <a
            key={ad.id}
            href={ad.link || '/products'}
            className={`ad-banner ${index === currentIndex ? 'active' : ''}`}
            style={{
              backgroundImage: `url(${getImageUrl(ad.image)})`,
            }}
          >
            <div className="ad-overlay"></div>
            <div className="ad-content-wrapper">
              <div className="ad-text-content">
                <h1 className="ad-main-title">{ad.title}</h1>
                {ad.description && (
                  <p className="ad-description">{ad.description}</p>
                )}
                <button className="ad-shop-button">Shop Now</button>
              </div>
            </div>
          </a>
        ))}
      </div>
    </section>
  );
};

export default AdvertisementsSection;