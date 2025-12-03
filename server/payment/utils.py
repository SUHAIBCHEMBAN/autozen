"""
Utility functions for the payment system
"""

from decimal import Decimal
from .models import PaymentConfiguration, Transaction, Refund, PaymentGateway, TransactionStatus


def get_active_payment_gateways():
    """
    Get all active payment gateways
    """
    return PaymentConfiguration.objects.filter(is_active=True)


def get_payment_gateway_config(gateway):
    """
    Get configuration for a specific payment gateway
    """
    try:
        return PaymentConfiguration.objects.get(gateway=gateway)
    except PaymentConfiguration.DoesNotExist:
        return None


def create_dummy_transaction(order, user, amount=None):
    """
    Create a dummy transaction for testing
    """
    if amount is None:
        amount = order.total_amount
    
    config = get_payment_gateway_config(PaymentGateway.DUMMY)
    if not config:
        # Create dummy config if it doesn't exist
        config, created = PaymentConfiguration.objects.get_or_create(
            gateway=PaymentGateway.DUMMY,
            defaults={
                'is_active': True,
                'currency': 'USD'
            }
        )
    
    transaction = Transaction.objects.create(
        order=order,
        user=user,
        gateway=PaymentGateway.DUMMY,
        amount=amount,
        currency=config.currency or 'USD'
    )
    
    return transaction


def process_dummy_payment(transaction):
    """
    Process a dummy payment (always succeeds for testing)
    """
    if transaction.gateway != PaymentGateway.DUMMY:
        raise ValueError("This function only processes dummy payments")
    
    transaction.status = TransactionStatus.SUCCESS
    transaction.metadata.update({'payment_method': 'dummy'})
    transaction.save()
    
    # Update order payment status
    transaction.order.payment_status = True
    transaction.order.status = 'confirmed'
    transaction.order.save()
    
    return True


def create_refund(transaction, amount=None, reason=''):
    """
    Create a refund for a transaction
    """
    if amount is None:
        amount = transaction.amount
    
    if amount > transaction.amount:
        raise ValueError("Refund amount cannot exceed transaction amount")
    
    # Create refund
    refund = Refund.objects.create(
        transaction=transaction,
        amount=amount,
        currency=transaction.currency,
        reason=reason,
        status=TransactionStatus.PENDING
    )
    
    # Update refund status (in a real implementation, you would call the gateway API)
    refund.status = TransactionStatus.REFUNDED
    refund.save()
    
    # Update transaction status
    transaction.status = TransactionStatus.REFUNDED
    transaction.save()
    
    return refund


def initialize_payment_system():
    """
    Initialize the payment system with default configurations
    """
    # Create dummy payment configuration for testing
    dummy_config, created = PaymentConfiguration.objects.get_or_create(
        gateway=PaymentGateway.DUMMY,
        defaults={
            'is_active': True,
            'merchant_id': 'dummy_merchant',
            'public_key': 'dummy_public_key',
            'secret_key': 'dummy_secret_key',
            'currency': 'USD'
        }
    )
    
    return dummy_config


def get_transaction_status(transaction_id):
    """
    Get the status of a transaction
    """
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id)
        return {
            'transaction_id': transaction.transaction_id,
            'status': transaction.status,
            'amount': transaction.amount,
            'currency': transaction.currency,
            'gateway': transaction.gateway
        }
    except Transaction.DoesNotExist:
        return None