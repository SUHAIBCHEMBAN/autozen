from django.db import models
from django.utils.text import slugify

class Page(models.Model):
    PAGE_TYPES = [
        ('about', 'About'),
        ('terms', 'Terms & Conditions'),
        ('refund', 'Return, Refund & Safety Tips'),
        ('privacy', 'Privacy Policy'),
        ('faq', 'FAQs'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    content = models.TextField()
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        
    def __str__(self):
        return self.question