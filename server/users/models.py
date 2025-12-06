"""
Models for the users app.

This module defines the custom user model and manager for the application.
It includes authentication fields and cache invalidation signals.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache


class CustomUserManager(BaseUserManager):
    """
    Custom manager for the User model.
    
    Provides methods for creating regular users and superusers with email/phone authentication.
    """
    
    def create_user(self, email=None, phone_number=None, username=None, password=None, **extra_fields):
        """
        Create and return a regular user with an email or phone number.
        
        Args:
            email (str, optional): User's email address
            phone_number (str, optional): User's phone number
            username (str, optional): User's username
            password (str): User's password
            **extra_fields: Additional fields for the user model
            
        Returns:
            User: The created user instance
            
        Raises:
            ValueError: If neither email nor phone number is provided
        """
        if not email and not phone_number:
            raise ValueError('The Email or Phone Number must be set')
        
        email = self.normalize_email(email) if email else None
        user = self.model(email=email, phone_number=phone_number, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, phone_number=None, username=None, password=None, **extra_fields):
        """
        Create and return a superuser with an email or phone number.
        
        Args:
            email (str, optional): Superuser's email address
            phone_number (str, optional): Superuser's phone number
            username (str, optional): Superuser's username
            password (str): Superuser's password
            **extra_fields: Additional fields for the superuser model
            
        Returns:
            User: The created superuser instance
            
        Raises:
            ValueError: If is_staff or is_superuser is not set to True
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, phone_number, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports authentication with email or phone number.
    
    Attributes:
        email (EmailField): Unique email address (optional)
        phone_number (CharField): Unique phone number (optional)
        username (CharField): Username for the user (optional)
        profile (TextField): Profile information for the user (optional)
        is_active (BooleanField): Whether the user account is active
        is_staff (BooleanField): Whether the user can access the admin site
        date_joined (DateTimeField): When the user account was created
    """
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(
        max_length=15, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')]
    )
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)
    profile = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    def __str__(self):
        """
        Return a string representation of the user.
        
        Returns:
            str: User's email, phone number, username, or ID
        """
        if self.email:
            return self.email
        elif self.phone_number:
            return self.phone_number
        elif self.username:
            return self.username
        return f"User {self.id}"

    class Meta:
        db_table = 'users'


@receiver(post_save, sender=User)
@receiver(post_delete, sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    """
    Signal handler to invalidate user cache when user data is saved or deleted.
    
    This ensures that cached user data stays consistent with database records.
    
    Args:
        sender: The model class
        instance: The actual instance being saved or deleted
        **kwargs: Additional keyword arguments
    """
    if instance.email:
        cache.delete(f"user_{instance.email}")
    if instance.phone_number:
        cache.delete(f"user_{instance.phone_number}")
    if instance.username:
        cache.delete(f"user_{instance.username}")