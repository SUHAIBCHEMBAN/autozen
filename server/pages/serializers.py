from rest_framework import serializers
from .models import Page, FAQ

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'title', 'slug', 'content', 'page_type', 'is_active', 'created_at', 'updated_at']

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'is_active', 'order', 'created_at', 'updated_at']