from rest_framework import serializers
from .models import User, Address


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    
    Handles serialization and deserialization of user data for API endpoints.
    """
    
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'username', 'profile', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile updates.
    
    Handles partial updates to user profile information.
    """
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'profile']


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the Address model.
    
    Handles serialization and deserialization of address data for API endpoints.
    """
    
    class Meta:
        model = Address
        fields = [
            'id', 'title', 'first_name', 'last_name', 'company',
            'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'phone_number', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, attrs):
        """
        Validate address data.
        
        Ensures that if an address is marked as default, it belongs to the requesting user.
        """
        # This validation will be handled in the view
        return attrs


class AddressCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new addresses.
    
    Handles creation of new address records with user association.
    """
    
    class Meta:
        model = Address
        fields = [
            'title', 'first_name', 'last_name', 'company',
            'address_line1', 'address_line2', 'city', 'state',
            'postal_code', 'country', 'phone_number', 'is_default'
        ]

    def create(self, validated_data):
        """
        Create a new address instance.
        
        Args:
            validated_data (dict): Validated address data
            
        Returns:
            Address: The created address instance
        """
        # The user will be set in the view
        return Address.objects.create(**validated_data)