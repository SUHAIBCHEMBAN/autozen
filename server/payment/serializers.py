from rest_framework import serializers
from .models import PaymentConfiguration, Transaction, Refund, PaymentGateway, TransactionStatus


class PaymentConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for payment configuration.
    
    Serializes payment configuration data for API responses and validates
    incoming data for payment configuration creation/update.
    """
    class Meta:
        model = PaymentConfiguration
        fields = [
            'id', 'gateway', 'is_active', 'merchant_id', 
            'public_key', 'currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for transactions.
    
    Serializes transaction data for API responses, including related user and order information.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'order', 'order_number', 'user', 'user_email',
            'gateway', 'gateway_transaction_id', 'amount', 'currency',
            'status', 'metadata', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'transaction_id', 'user', 'user_email', 'order_number',
            'gateway_transaction_id', 'metadata', 'error_message',
            'created_at', 'updated_at'
        ]


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating transactions.
    
    Validates incoming data for transaction creation, ensuring the order belongs
    to the requesting user and hasn't already been paid.
    """
    class Meta:
        model = Transaction
        fields = [
            'id', 'order', 'gateway', 'amount', 'currency'
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        """
        Validate transaction creation data.
        
        Ensures the order belongs to the requesting user and hasn't already been paid.
        
        Args:
            attrs (dict): The attributes to validate
            
        Returns:
            dict: The validated attributes
            
        Raises:
            serializers.ValidationError: If validation fails
        """
        order = attrs.get('order')
        user = self.context['request'].user
        
        # Check if order belongs to user
        if order.user != user:
            raise serializers.ValidationError("You can only create transactions for your own orders.")
        
        # Check if order already has a successful transaction
        if order.transactions.filter(status=TransactionStatus.SUCCESS).exists():
            raise serializers.ValidationError("This order has already been paid.")
        
        return attrs


class RefundSerializer(serializers.ModelSerializer):
    """
    Serializer for refunds.
    
    Serializes refund data for API responses, including related transaction information.
    """
    transaction_id = serializers.CharField(source='transaction.transaction_id', read_only=True)
    
    class Meta:
        model = Refund
        fields = [
            'id', 'refund_id', 'transaction', 'transaction_id',
            'amount', 'currency', 'status', 'reason',
            'gateway_refund_id', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'refund_id', 'transaction_id',
            'gateway_refund_id', 'metadata',
            'created_at', 'updated_at'
        ]


class PaymentIntentSerializer(serializers.Serializer):
    """
    Serializer for payment intent creation.
    
    Validates incoming data for payment intent creation, ensuring the order ID
    and payment gateway are provided and valid.
    """
    order_id = serializers.IntegerField()
    gateway = serializers.ChoiceField(choices=PaymentGateway.choices)