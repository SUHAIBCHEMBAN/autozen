"""
Cache utilities for the payment app
Provides optimized caching functions for payment configurations, transactions, and refunds with Redis
"""

import logging
from django.core.cache import cache
from django.conf import settings

# Cache timeout settings
PAYMENT_CONFIG_CACHE_TIMEOUT = getattr(settings, 'PAYMENT_CONFIG_CACHE_TIMEOUT', 60 * 60)  # 1 hour
TRANSACTION_CACHE_TIMEOUT = getattr(settings, 'TRANSACTION_CACHE_TIMEOUT', 60 * 15)  # 15 minutes
REFUND_CACHE_TIMEOUT = getattr(settings, 'REFUND_CACHE_TIMEOUT', 60 * 15)  # 15 minutes

logger = logging.getLogger(__name__)


def get_payment_config_cache_key(gateway):
    """
    Generate cache key for payment configuration
    
    Args:
        gateway (str): The payment gateway identifier
        
    Returns:
        str: Formatted cache key
    """
    return f"payment_config_{gateway}"


def get_transaction_cache_key(transaction_id):
    """
    Generate cache key for a transaction
    
    Args:
        transaction_id (str): The transaction identifier
        
    Returns:
        str: Formatted cache key
    """
    return f"transaction_{transaction_id}"


def get_user_transactions_cache_key(user_id):
    """
    Generate cache key for user's transactions list
    
    Args:
        user_id (int): The user ID
        
    Returns:
        str: Formatted cache key
    """
    return f"user_transactions_{user_id}"


def get_refund_cache_key(refund_id):
    """
    Generate cache key for a refund
    
    Args:
        refund_id (str): The refund identifier
        
    Returns:
        str: Formatted cache key
    """
    return f"refund_{refund_id}"


def get_cached_payment_config(gateway):
    """
    Get payment configuration with caching
    
    Args:
        gateway (str): The payment gateway identifier
        
    Returns:
        PaymentConfiguration: The payment configuration instance or None if not found
    """
    from .models import PaymentConfiguration  # Import here to avoid circular import
    
    cache_key = get_payment_config_cache_key(gateway)
    cached_config = cache.get(cache_key)
    
    if cached_config is not None:
        return cached_config
        
    try:
        config = PaymentConfiguration.objects.get(gateway=gateway)
        cache.set(cache_key, config, PAYMENT_CONFIG_CACHE_TIMEOUT)
        return config
    except PaymentConfiguration.DoesNotExist:
        return None


def get_cached_active_payment_configs():
    """
    Get all active payment configurations with caching
    
    Returns:
        list: Cached list of active payment configurations
    """
    from .models import PaymentConfiguration  # Import here to avoid circular import
    
    cache_key = "active_payment_configs"
    cached_configs = cache.get(cache_key)
    
    if cached_configs is not None:
        return cached_configs
        
    configs = list(PaymentConfiguration.objects.filter(is_active=True))
    cache.set(cache_key, configs, PAYMENT_CONFIG_CACHE_TIMEOUT)
    return configs


def get_cached_transaction(transaction_id):
    """
    Get a transaction by ID with caching
    
    Args:
        transaction_id (str): The transaction identifier
        
    Returns:
        Transaction: The transaction instance or None if not found
    """
    from .models import Transaction  # Import here to avoid circular import
    
    cache_key = get_transaction_cache_key(transaction_id)
    cached_transaction = cache.get(cache_key)
    
    if cached_transaction is not None:
        return cached_transaction
        
    try:
        transaction = Transaction.objects.select_related('order', 'user').get(transaction_id=transaction_id)
        cache.set(cache_key, transaction, TRANSACTION_CACHE_TIMEOUT)
        return transaction
    except Transaction.DoesNotExist:
        return None


def get_cached_user_transactions(user_id):
    """
    Get all transactions for a user with caching
    
    Args:
        user_id (int): The user ID
        
    Returns:
        list: Cached list of user transactions
    """
    from .models import Transaction  # Import here to avoid circular import
    
    cache_key = get_user_transactions_cache_key(user_id)
    cached_transactions = cache.get(cache_key)
    
    if cached_transactions is not None:
        return cached_transactions
        
    transactions = list(Transaction.objects.filter(user_id=user_id).select_related('order').order_by('-created_at'))
    cache.set(cache_key, transactions, TRANSACTION_CACHE_TIMEOUT)
    return transactions


def get_cached_refund(refund_id):
    """
    Get a refund by ID with caching
    
    Args:
        refund_id (str): The refund identifier
        
    Returns:
        Refund: The refund instance or None if not found
    """
    from .models import Refund  # Import here to avoid circular import
    
    cache_key = get_refund_cache_key(refund_id)
    cached_refund = cache.get(cache_key)
    
    if cached_refund is not None:
        return cached_refund
        
    try:
        refund = Refund.objects.select_related('transaction').get(refund_id=refund_id)
        cache.set(cache_key, refund, REFUND_CACHE_TIMEOUT)
        return refund
    except Refund.DoesNotExist:
        return None


def invalidate_payment_config_cache(gateway):
    """
    Invalidate cache for a payment configuration
    
    Args:
        gateway (str): The payment gateway identifier
    """
    cache_key = get_payment_config_cache_key(gateway)
    cache.delete(cache_key)
    # Also invalidate the active configs cache
    cache.delete("active_payment_configs")
    logger.info(f"Invalidated cache for payment config {gateway}")


def invalidate_transaction_cache(transaction_id):
    """
    Invalidate cache for a transaction
    
    Args:
        transaction_id (str): The transaction identifier
    """
    cache_key = get_transaction_cache_key(transaction_id)
    cache.delete(cache_key)
    logger.info(f"Invalidated cache for transaction {transaction_id}")


def invalidate_user_transactions_cache(user_id):
    """
    Invalidate cache for user's transactions
    
    Args:
        user_id (int): The user ID
    """
    cache_key = get_user_transactions_cache_key(user_id)
    cache.delete(cache_key)
    logger.info(f"Invalidated cache for user {user_id} transactions")


def invalidate_refund_cache(refund_id):
    """
    Invalidate cache for a refund
    
    Args:
        refund_id (str): The refund identifier
    """
    cache_key = get_refund_cache_key(refund_id)
    cache.delete(cache_key)
    logger.info(f"Invalidated cache for refund {refund_id}")


def invalidate_all_payment_cache():
    """
    Invalidate all payment-related cache entries
    This should be called when bulk operations affect payments
    """
    # This is a more aggressive invalidation that clears all payment caches
    cache.delete_pattern("payment_config_*")
    cache.delete_pattern("transaction_*")
    cache.delete_pattern("user_transactions_*")
    cache.delete_pattern("refund_*")
    cache.delete("active_payment_configs")
    logger.info("Invalidated all payment-related cache entries")