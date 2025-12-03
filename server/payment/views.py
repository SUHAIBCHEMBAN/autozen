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
from order.models import Order


class PaymentConfigurationListView(APIView):
    """View to list payment configurations"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get all payment configurations"""
        configs = PaymentConfiguration.objects.all()
        serializer = PaymentConfigurationSerializer(configs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionListView(APIView):
    """View to list user transactions"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user transactions"""
        transactions = Transaction.objects.filter(user=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionDetailView(APIView):
    """View to get transaction details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, transaction_id):
        """Get transaction details"""
        transaction = get_object_or_404(Transaction, transaction_id=transaction_id, user=request.user)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreatePaymentIntentView(APIView):
    """View to create a payment intent"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Create a payment intent for an order"""
        serializer = PaymentIntentSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            gateway = serializer.validated_data['gateway']
            
            # Get the order
            try:
                order = Order.objects.get(id=order_id, user=request.user)
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
            
            # Get payment configuration
            try:
                config = PaymentConfiguration.objects.get(gateway=gateway, is_active=True)
            except PaymentConfiguration.DoesNotExist:
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
            
            # Return payment intent data based on gateway
            intent_data = self.get_payment_intent_data(transaction, config)
            
            return Response(intent_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_payment_intent_data(self, transaction, config):
        """Generate payment intent data based on gateway"""
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
    """View to process a payment"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Process a payment"""
        transaction_id = request.data.get('transaction_id')
        payment_method = request.data.get('payment_method')
        payment_data = request.data.get('payment_data', {})
        
        # Get the transaction
        try:
            transaction = Transaction.objects.get(
                transaction_id=transaction_id, 
                user=request.user,
                status=TransactionStatus.PENDING
            )
        except Transaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found or not eligible for processing'}, 
                status=status.HTTP_404_NOT_FOUND
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
            
            return Response({
                'error': 'Payment processing failed'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def process_payment_gateway(self, transaction, payment_method, payment_data):
        """Process payment based on gateway"""
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
    """View to refund a transaction"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Refund a transaction"""
        transaction_id = request.data.get('transaction_id')
        reason = request.data.get('reason', '')
        amount = request.data.get('amount')
        
        # Get the transaction
        try:
            transaction = Transaction.objects.get(
                transaction_id=transaction_id, 
                user=request.user,
                status=TransactionStatus.SUCCESS
            )
        except Transaction.DoesNotExist:
            return Response(
                {'error': 'Successful transaction not found'}, 
                status=status.HTTP_404_NOT_FOUND
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
        
        serializer = RefundSerializer(refund)
        return Response(serializer.data, status=status.HTTP_201_CREATED)