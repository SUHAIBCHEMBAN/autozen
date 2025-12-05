from django.db import models
from django.conf import settings
from decimal import Decimal
from order.models import Order


class PaymentGateway(models.TextChoices):
    """
    Supported payment gateways enumeration.
    
    Defines the available payment gateway options that can be used for processing payments.
    """
    STRIPE = 'stripe', 'Stripe'
    PAYPAL = 'paypal', 'PayPal'
    RAZORPAY = 'razorpay', 'Razorpay'
    FLUTTERWAVE = 'flutterwave', 'Flutterwave'
    DUMMY = 'dummy', 'Dummy Gateway'


class TransactionStatus(models.TextChoices):
    """
    Transaction status choices enumeration.
    
    Defines the possible statuses that a payment transaction can have during its lifecycle.
    """
    PENDING = 'pending', 'Pending'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    REFUNDED = 'refunded', 'Refunded'


class PaymentConfiguration(models.Model):
    """
    Configuration for payment gateways.
    
    Stores configuration details for different payment gateways including
    API keys, merchant IDs, and other gateway-specific settings.
    """
    gateway = models.CharField(max_length=20, choices=PaymentGateway.choices, unique=True)
    is_active = models.BooleanField(default=False)
    merchant_id = models.CharField(max_length=255, blank=True)
    public_key = models.CharField(max_length=500, blank=True)
    secret_key = models.CharField(max_length=500, blank=True)
    webhook_secret = models.CharField(max_length=500, blank=True)
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_configurations'
        verbose_name = 'Payment Configuration'
        verbose_name_plural = 'Payment Configurations'
    
    def __str__(self):
        return f"{self.gateway} Configuration"
    
    def save(self, *args, **kwargs):
        """
        Override save method to invalidate cache when payment configuration is updated.
        
        This ensures that any cached configurations are refreshed when changes are made.
        """
        # Import here to avoid circular import
        from .cache_utils import invalidate_payment_config_cache
        
        # Call the original save method
        super().save(*args, **kwargs)
        
        # Invalidate cache for this gateway
        invalidate_payment_config_cache(self.gateway)


class Transaction(models.Model):
    """
    Represents a payment transaction.
    
    Stores all details related to a payment transaction including the order,
    user, amount, gateway used, status, and metadata.
    """
    # Transaction identification
    transaction_id = models.CharField(max_length=100, unique=True, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    
    # Gateway information
    gateway = models.CharField(max_length=20, choices=PaymentGateway.choices)
    gateway_transaction_id = models.CharField(max_length=255, blank=True)
    
    # Amount details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_transactions'
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['order']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['gateway']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.status}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate transaction ID if not set and invalidate cache.
        
        Ensures that a unique transaction ID is generated when creating a new transaction
        and invalidates related caches when updating existing transactions.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Import here to avoid circular import
        from .cache_utils import invalidate_transaction_cache, invalidate_user_transactions_cache
        
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        
        # Call the original save method
        super().save(*args, **kwargs)
        
        # Invalidate cache for this transaction
        if self.transaction_id:
            invalidate_transaction_cache(self.transaction_id)
        
        # Invalidate user transactions cache
        if hasattr(self, 'user_id') and self.user_id:
            invalidate_user_transactions_cache(self.user_id)
    
    def generate_transaction_id(self):
        """
        Generate a unique transaction ID.
        
        Creates a unique identifier for the transaction using UUID.
        
        Returns:
            str: A unique transaction identifier prefixed with 'TXN-'
        """
        import uuid
        return f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    @property
    def is_successful(self):
        """
        Check if transaction is successful.
        
        Returns:
            bool: True if transaction status is SUCCESS, False otherwise
        """
        return self.status == TransactionStatus.SUCCESS
    
    @property
    def is_pending(self):
        """
        Check if transaction is pending.
        
        Returns:
            bool: True if transaction status is PENDING, False otherwise
        """
        return self.status == TransactionStatus.PENDING
    
    @property
    def is_failed(self):
        """
        Check if transaction has failed.
        
        Returns:
            bool: True if transaction status is FAILED, False otherwise
        """
        return self.status == TransactionStatus.FAILED


class Refund(models.Model):
    """
    Represents a refund transaction.
    
    Stores all details related to a refund including the original transaction,
    amount, reason, status, and gateway-specific refund identifier.
    """
    # Refund identification
    refund_id = models.CharField(max_length=100, unique=True, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='refunds')
    
    # Amount details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # Status
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.PENDING)
    
    # Reason
    reason = models.TextField(blank=True)
    
    # Gateway information
    gateway_refund_id = models.CharField(max_length=255, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_refunds'
        verbose_name = 'Refund'
        verbose_name_plural = 'Refunds'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund {self.refund_id} - {self.status}"
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate refund ID if not set and invalidate cache.
        
        Ensures that a unique refund ID is generated when creating a new refund
        and invalidates related caches when updating existing refunds.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        # Import here to avoid circular import
        from .cache_utils import invalidate_refund_cache
        
        if not self.refund_id:
            self.refund_id = self.generate_refund_id()
        
        # Call the original save method
        super().save(*args, **kwargs)
        
        # Invalidate cache for this refund
        if self.refund_id:
            invalidate_refund_cache(self.refund_id)
    
    def generate_refund_id(self):
        """
        Generate a unique refund ID.
        
        Creates a unique identifier for the refund using UUID.
        
        Returns:
            str: A unique refund identifier prefixed with 'REF-'
        """
        import uuid
        return f"REF-{uuid.uuid4().hex[:12].upper()}"