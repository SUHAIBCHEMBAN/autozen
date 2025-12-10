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


class Address(models.Model):
    """
    User address model for storing shipping/billing addresses.
    
    Attributes:
        user (ForeignKey): Reference to the user who owns this address
        title (CharField): Short title for the address (e.g., "Home", "Work")
        first_name (CharField): First name of the recipient
        last_name (CharField): Last name of the recipient
        company (CharField): Company name (optional)
        address_line1 (CharField): Street address line 1
        address_line2 (CharField): Street address line 2 (optional)
        city (CharField): City
        state (CharField): State or province
        postal_code (CharField): Postal or ZIP code
        country (CharField): Country
        phone_number (CharField): Contact phone number
        is_default (BooleanField): Whether this is the default address
        created_at (DateTimeField): When the address was created
        updated_at (DateTimeField): When the address was last updated
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=100, help_text="Short title for this address (e.g., Home, Work)")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company = models.CharField(max_length=100, blank=True)
    address_line1 = models.CharField(max_length=255, verbose_name="Address Line 1")
    address_line2 = models.CharField(max_length=255, blank=True, verbose_name="Address Line 2")
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="India")
    phone_number = models.CharField(max_length=15, validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$')])
    is_default = models.BooleanField(default=False, help_text="Make this your default address")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_addresses'
        verbose_name = 'User Address'
        verbose_name_plural = 'User Addresses'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.first_name} {self.last_name}, {self.city}, {self.state}"

    def save(self, *args, **kwargs):
        # If this is set as default, unset other defaults for this user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        """Return the full name of the recipient."""
        return f"{self.first_name} {self.last_name}"

    @property
    def formatted_address(self):
        """Return a formatted address string."""
        address_parts = [
            self.address_line1,
            self.address_line2,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country
        ]
        return ", ".join([part for part in address_parts if part])


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