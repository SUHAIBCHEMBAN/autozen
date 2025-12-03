from django.contrib import admin
from .models import PaymentConfiguration, Transaction, Refund


@admin.register(PaymentConfiguration)
class PaymentConfigurationAdmin(admin.ModelAdmin):
    """Admin for payment configurations"""
    list_display = ['gateway', 'is_active', 'currency', 'created_at', 'updated_at']
    list_filter = ['gateway', 'is_active', 'currency', 'created_at']
    search_fields = ['gateway', 'merchant_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['gateway']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin for transactions"""
    list_display = ['transaction_id', 'order', 'user', 'gateway', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['gateway', 'status', 'currency', 'created_at']
    search_fields = ['transaction_id', 'gateway_transaction_id', 'order__order_number', 'user__email']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    # Allow filtering by date range
    date_hierarchy = 'created_at'


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Admin for refunds"""
    list_display = ['refund_id', 'transaction', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['refund_id', 'gateway_refund_id', 'transaction__transaction_id']
    readonly_fields = ['refund_id', 'created_at', 'updated_at']
    ordering = ['-created_at']