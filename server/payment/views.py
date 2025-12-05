from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from decimal import Decimal
from .models import PaymentConfiguration, Transaction, Refund, PaymentGateway, TransactionStatus
from .serializers import (
    PaymentConfigurationSerializer, TransactionSerializer, 
    TransactionCreateSerializer, RefundSerializer, PaymentIntentSerializer
)
from .cache_utils import (
    get_cached_active_payment_configs, get_cached_user_transactions,
    get_cached_transaction, invalidate_transaction_cache,
    invalidate_user_transactions_cache
)
from order.models import Order


class PaymentConfigurationListView(APIView):
    """
    View to list payment configurations.
    
    Provides a list of all active payment configurations with caching for improved performance.
    Requires authentication to access.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get all active payment configurations using caching.
        
        Retrieves payment configurations from cache if available, otherwise fetches from
        database and caches the results for future requests.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: Serialized payment configurations data
            
        Example:
            GET /api/payment/configurations/
            Response: [{"id": 1, "gateway": "stripe", "is_active": true, ...}]
        """
        configs = get_cached_active_payment_configs()
        serializer = PaymentConfigurationSerializer(configs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionListView(APIView):
    """
    View to list user transactions.
    
    Provides a list of all transactions for the authenticated user with caching for improved performance.
    Requires authentication to access.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get user transactions using caching.
        
        Retrieves user transactions from cache if available, otherwise fetches from
        database and caches the results for future requests.
        
        Args:
            request: The HTTP request object containing the authenticated user
            
        Returns:
            Response: Serialized transactions data
            
        Example:
            GET /api/payment/transactions/
            Response: [{"id": 1, "transaction_id": "TXN-ABC123", "amount": "100.00", ...}]
        """
        transactions = get_cached_user_transactions(request.user.id)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionDetailView(APIView):
    """
    View to get transaction details.
    
    Provides detailed information for a specific transaction with caching for improved performance.
    Requires authentication to access and only allows users to view their own transactions.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, transaction_id):
        """
        Get transaction details using caching.
        
        Retrieves transaction details from cache if available, otherwise fetches from
        database and caches the results for future requests.
        
        Args:
            request: The HTTP request object containing the authenticated user
            transaction_id (str): The unique identifier of the transaction
            
        Returns:
            Response: Serialized transaction data
            
        Example:
            GET /api/payment/transactions/TXN-ABC123/
            Response: {"id": 1, "transaction_id": "TXN-ABC123", "amount": "100.00", ...}
        """
        transaction = get_cached_transaction(transaction_id)
        if not transaction or transaction.user != request.user:
            return Response(
                {'error': 'Transaction not found or does not belong to you'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePaymentIntentView(APIView):
    """
    View to create a payment intent.
    
    Creates a payment intent for an order, preparing it for payment processing.
    Requires authentication to access.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Create a payment intent for an order.
        
        Validates the order and payment gateway, then creates a transaction record
        and returns payment intent data based on the selected gateway.
        
        Args:
            request: The HTTP request object containing order_id and gateway
            
        Returns:
            Response: Payment intent data or error message
            
        Example:
            POST /api/payment/create-intent/
            Request: {"order_id": 1, "gateway": "stripe"}
            Response: {"transaction_id": "TXN-ABC123", "amount": 10000, "client_secret": "..."}
        """
        serializer = PaymentIntentSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            gateway = serializer.validated_data['gateway']
            
            # Get the order
            try:
                order = Order.objects.select_related('user').get(id=order_id, user=request.user)
            except Order.DoesNotExist:
                return Response(
                    {'error': 'Order not found or does not belong to you'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if order is already paid
            if order.payment_status:
                return Response(
                    {'error': 'Order is already paid'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get payment configuration using cache
            from .cache_utils import get_cached_payment_config
            config = get_cached_payment_config(gateway)
            if not config or not config.is_active:
                return Response(
                    {'error': f'{gateway} payment gateway is not configured or not active'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create transaction
            with db_transaction.atomic():
                transaction = Transaction.objects.create(
                    order=order,
                    user=request.user,
                    gateway=gateway,
                    amount=order.total_amount,
                    currency=config.currency or 'USD'
                )
                
                # Invalidate user transactions cache since we added a new transaction
                invalidate_user_transactions_cache(request.user.id)
            
            # Return payment intent data based on gateway
            intent_data = self.get_payment_intent_data(transaction, config)
            
            return Response(intent_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_payment_intent_data(self, transaction, config):
        """
        Generate payment intent data based on gateway.
        
        Creates the appropriate payment intent data structure based on the selected
        payment gateway, including client secrets and publishable keys.
        
        Args:
            transaction (Transaction): The transaction object
            config (PaymentConfiguration): The payment configuration object
            
        Returns:
            dict: Payment intent data
        """
        if config.gateway == PaymentGateway.DUMMY:
            return {
                'transaction_id': transaction.transaction_id,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'gateway': config.gateway,
                'client_secret': f"dummy_secret_{transaction.transaction_id}",
                'publishable_key': config.public_key or "dummy_public_key"
            }
        elif config.gateway == PaymentGateway.STRIPE:
            # Stripe-specific implementation would go here
            return {
                'transaction_id': transaction.transaction_id,
                'amount': int(transaction.amount * 100),  # Convert to cents
                'currency': transaction.currency.lower(),
                'gateway': config.gateway,
                'client_secret': f"stripe_secret_{transaction.transaction_id}",
                'publishable_key': config.public_key
            }
        else:
            # Generic implementation for other gateways
            return {
                'transaction_id': transaction.transaction_id,
                'amount': str(transaction.amount),
                'currency': transaction.currency,
                'gateway': config.gateway,
                'client_secret': f"{config.gateway}_secret_{transaction.transaction_id}",
                'publishable_key': config.public_key
            }


class ProcessPaymentView(APIView):
    """
    View to process a payment.
    
    Processes a payment transaction and updates the order and transaction status accordingly.
    Requires authentication to access.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Process a payment transaction.
        
        Validates the transaction and processes the payment using the appropriate
        payment gateway. Updates transaction and order status upon completion.
        
        Args:
            request: The HTTP request object containing transaction_id, payment_method, and payment_data
            
        Returns:
            Response: Success or error message
            
        Example:
            POST /api/payment/process/
            Request: {"transaction_id": "TXN-ABC123", "payment_method": "card"}
            Response: {"message": "Payment processed successfully", "transaction_id": "TXN-ABC123"}
        """
        transaction_id = request.data.get('transaction_id')
        payment_method = request.data.get('payment_method')
        payment_data = request.data.get('payment_data', {})
        
        # Get the transaction using cache
        transaction = get_cached_transaction(transaction_id)
        if not transaction or transaction.user != request.user:
            return Response(
                {'error': 'Transaction not found or does not belong to you'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if transaction.status != TransactionStatus.PENDING:
            return Response(
                {'error': 'Transaction not eligible for processing'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Process payment based on gateway
        success = self.process_payment_gateway(transaction, payment_method, payment_data)
        
        if success:
            # Update transaction status
            transaction.status = TransactionStatus.SUCCESS
            transaction.metadata.update({'payment_method': payment_method})
            transaction.save()
            
            # Update order payment status
            transaction.order.payment_status = True
            transaction.order.status = 'confirmed'
            transaction.order.save()
            
            # Invalidate caches
            invalidate_transaction_cache(transaction_id)
            invalidate_user_transactions_cache(request.user.id)
            
            return Response({
                'message': 'Payment processed successfully',
                'transaction_id': transaction.transaction_id,
                'status': transaction.status
            }, status=status.HTTP_200_OK)
        else:
            # Update transaction status to failed
            transaction.status = TransactionStatus.FAILED
            transaction.error_message = 'Payment processing failed'
            transaction.save()
            
            # Invalidate caches
            invalidate_transaction_cache(transaction_id)
            invalidate_user_transactions_cache(request.user.id)
            
            return Response({
                'error': 'Payment processing failed'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def process_payment_gateway(self, transaction, payment_method, payment_data):
        """
        Process payment based on gateway.
        
        Handles payment processing for different gateways. In a production environment,
        this would integrate with actual payment gateway APIs.
        
        Args:
            transaction (Transaction): The transaction object to process
            payment_method (str): The payment method used
            payment_data (dict): Additional payment data
            
        Returns:
            bool: True if payment processing succeeded, False otherwise
        """
        if transaction.gateway == PaymentGateway.DUMMY:
            # For dummy gateway, simulate success/failure
            # In a real implementation, you would integrate with the actual gateway API
            return True  # Always succeed for dummy
        elif transaction.gateway == PaymentGateway.STRIPE:
            # Stripe implementation would go here
            return True
        else:
            # Generic implementation
            return True


class RefundTransactionView(APIView):
    """
    View to refund a transaction.
    
    Processes a refund for a successful transaction and updates related records.
    Requires authentication to access.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Refund a transaction.
        
        Validates the transaction and creates a refund record. Updates transaction
        and order status upon completion.
        
        Args:
            request: The HTTP request object containing transaction_id, reason, and amount
            
        Returns:
            Response: Refund data or error message
            
        Example:
            POST /api/payment/refund/
            Request: {"transaction_id": "TXN-ABC123", "reason": "Customer request"}
            Response: {"id": 1, "refund_id": "REF-XYZ789", "amount": "100.00", ...}
        """
        transaction_id = request.data.get('transaction_id')
        reason = request.data.get('reason', '')
        amount = request.data.get('amount')
        
        # Get the transaction using cache
        transaction = get_cached_transaction(transaction_id)
        if not transaction or transaction.user != request.user:
            return Response(
                {'error': 'Successful transaction not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if transaction.status != TransactionStatus.SUCCESS:
            return Response(
                {'error': 'Transaction is not successful'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate amount
        if amount:
            amount = Decimal(str(amount))
            if amount > transaction.amount:
                return Response(
                    {'error': 'Refund amount cannot exceed transaction amount'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            amount = transaction.amount
        
        # Create refund
        with db_transaction.atomic():
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
            
            # Update order status if all transactions are refunded
            if not transaction.order.transactions.exclude(status=TransactionStatus.REFUNDED).exists():
                transaction.order.status = 'refunded'
                transaction.order.save()
            
            # Invalidate caches
            from .cache_utils import invalidate_refund_cache
            invalidate_refund_cache(refund.refund_id)
            invalidate_transaction_cache(transaction_id)
            invalidate_user_transactions_cache(request.user.id)
        
        serializer = RefundSerializer(refund)
        return Response(serializer.data, status=status.HTTP_201_CREATED)