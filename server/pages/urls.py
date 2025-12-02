from django.urls import path
from .views import (
    PageDetailView, PageByTypeView, 
    FaqListView, PageListView
)

app_name = 'pages'

urlpatterns = [
    # Page API endpoints
    path('', PageListView.as_view(), name='page_list'),
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail'),
    path('type/<str:page_type>/', PageByTypeView.as_view(), name='page_by_type'),
    
    # FAQ API endpoints
    path('faq/list/', FaqListView.as_view(), name='faq_list'),
]