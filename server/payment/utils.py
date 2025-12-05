"""
Utility functions for the payment system.

Provides helper functions for payment processing, transaction management,
and payment gateway integration.
"""

from decimal import Decimal
from .models import PaymentConfiguration, Transaction, Refund, PaymentGateway, TransactionStatus


def get_active_payment_gateways():
    """
    Get all active payment gateways.
    
    Retrieves all payment gateway configurations that are marked as active.
    Uses database query without caching for real-time accuracy.
    
    Returns:
        QuerySet: Active PaymentConfiguration objects
    """
    return PaymentConfiguration.objects.filter(is_active=True)


def get_payment_gateway_config(gateway):
    """
    Get configuration for a specific payment gateway.
    
    Retrieves the configuration for a specific payment gateway by its identifier.
    Uses database query without caching for real-time accuracy.
    
    Args:
        gateway (str): The payment gateway identifier
        
    Returns:
        PaymentConfiguration: The payment configuration object or None if not found
    """
    try:
        return PaymentConfiguration.objects.get(gateway=gateway)
    except PaymentConfiguration.DoesNotExist:
        return None


def create_dummy_transaction(order, user, amount=None):
    """
    Create a dummy transaction for testing.
    
    Creates a transaction using the dummy payment gateway for testing purposes.
    If the dummy gateway configuration doesn't exist, it will be created.
    
    Args:
        order (Order): The order object
        user (User): The user object
        amount (Decimal, optional): The transaction amount. Defaults to order total amount
        
    Returns:
        Transaction: The created transaction object
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
    Process a dummy payment (always succeeds for testing).
    
    Processes a payment using the dummy payment gateway, which always succeeds.
    Updates the transaction and order status accordingly.
    
    Args:
        transaction (Transaction): The transaction object to process
        
    Returns:
        bool: True if processing succeeded
        
    Raises:
        ValueError: If the transaction is not a dummy payment
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
    Create a refund for a transaction.
    
    Creates a refund record for a successful transaction and updates the
    transaction status. In a real implementation, this would call the
    payment gateway's refund API.
    
    Args:
        transaction (Transaction): The transaction to refund
        amount (Decimal, optional): The refund amount. Defaults to full transaction amount
        reason (str, optional): The reason for the refund
        
    Returns:
        Refund: The created refund object
        
    Raises:
        ValueError: If the refund amount exceeds the transaction amount
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
    Initialize the payment system with default configurations.
    
    Sets up the payment system with default configurations, particularly
    creating a dummy payment configuration for testing purposes.
    
    Returns:
        PaymentConfiguration: The dummy payment configuration object
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
    Get the status of a transaction.
    
    Retrieves the status and key details of a transaction by its identifier.
    Uses database query without caching for real-time accuracy.
    
    Args:
        transaction_id (str): The transaction identifier
        
    Returns:
        dict: Transaction status information or None if not found
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