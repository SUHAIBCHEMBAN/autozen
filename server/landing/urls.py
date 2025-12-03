from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    # Main landing page content
    path('', views.LandingPageContentView.as_view(), name='landing-page'),
    
    # Individual sections
    path('hero-banners/', views.HeroBannerListView.as_view(), name='hero-banners'),
    path('categories/', views.CategorySectionListView.as_view(), name='categories'),
    path('new-arrivals/', views.NewArrivalsListView.as_view(), name='new-arrivals'),
    path('advertisements/', views.AdvertisementBannerListView.as_view(), name='advertisements'),
    path('testimonials/', views.TestimonialListView.as_view(), name='testimonials'),
    path('featured-brands/', views.FeaturedBrandsListView.as_view(), name='featured-brands'),
]