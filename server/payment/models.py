from django.db import models
from django.conf import settings
from decimal import Decimal
from order.models import Order


class PaymentGateway(models.TextChoices):
    """Supported payment gateways"""
    STRIPE = 'stripe', 'Stripe'
    PAYPAL = 'paypal', 'PayPal'
    RAZORPAY = 'razorpay', 'Razorpay'
    FLUTTERWAVE = 'flutterwave', 'Flutterwave'
    DUMMY = 'dummy', 'Dummy Gateway'


class TransactionStatus(models.TextChoices):
    """Transaction status choices"""
    PENDING = 'pending', 'Pending'
    SUCCESS = 'success', 'Success'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    REFUNDED = 'refunded', 'Refunded'


class PaymentConfiguration(models.Model):
    """
    Configuration for payment gateways
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


class Transaction(models.Model):
    """
    Represents a payment transaction
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
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def generate_transaction_id(self):
        """Generate a unique transaction ID"""
        import uuid
        return f"TXN-{uuid.uuid4().hex[:12].upper()}"
    
    @property
    def is_successful(self):
        return self.status == TransactionStatus.SUCCESS
    
    @property
    def is_pending(self):
        return self.status == TransactionStatus.PENDING
    
    @property
    def is_failed(self):
        return self.status == TransactionStatus.FAILED


class Refund(models.Model):
    """
    Represents a refund transaction
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
        if not self.refund_id:
            self.refund_id = self.generate_refund_id()
        super().save(*args, **kwargs)
    
    def generate_refund_id(self):
        """Generate a unique refund ID"""
        import uuid
        return f"REF-{uuid.uuid4().hex[:12].upper()}"