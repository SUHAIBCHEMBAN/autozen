# Payment App Documentation

This Django app provides a complete payment system for an automotive spare parts and accessories e-commerce platform.

## Overview

The payment app delivers a robust, secure, and extensible payment processing system with support for multiple payment gateways. It seamlessly integrates with the existing order system and provides comprehensive transaction management.

## Key Features

### Multi-Gateway Support
- **Dummy Gateway**: For testing and development
- **Stripe**: Ready for production integration
- **PayPal**: Ready for production integration
- **Razorpay**: Indian payment provider support
- **Flutterwave**: African payment provider support
- **Extensible**: Easy to add new payment providers

### Transaction Management
- Complete transaction lifecycle tracking
- Status management (Pending, Success, Failed, Cancelled, Refunded)
- Metadata storage for gateway-specific information
- Error tracking and logging

### Refund Processing
- Full refund management system
- Partial refund support
- Reason tracking
- Status management

### Security
- Secure handling of payment data
- Authentication required for all operations
- Proper error handling without exposing sensitive information
- Audit trails for all transactions

### Admin Interface
- Comprehensive Django admin integration
- Filtering and search capabilities
- Status monitoring
- Configuration management

## Models

### PaymentConfiguration
Represents configuration settings for payment gateways.

Key fields:
- `gateway`: Payment gateway type
- `is_active`: Enable/disable gateway
- `merchant_id`: Merchant identifier
- `public_key`: Public API key
- `secret_key`: Secret API key
- `webhook_secret`: Webhook verification secret
- `currency`: Default currency

### Transaction
Represents a payment transaction.

Key fields:
- `transaction_id`: Unique transaction identifier
- `order`: Related order
- `user`: Customer who made the payment
- `gateway`: Payment gateway used
- `gateway_transaction_id`: Gateway's transaction ID
- `amount`: Transaction amount
- `currency`: Transaction currency
- `status`: Current transaction status
- `metadata`: Additional gateway-specific data
- `error_message`: Error details if failed

### Refund
Represents a refund transaction.

Key fields:
- `refund_id`: Unique refund identifier
- `transaction`: Original transaction
- `amount`: Refund amount
- `currency`: Refund currency
- `status`: Current refund status
- `reason`: Reason for refund
- `gateway_refund_id`: Gateway's refund ID
- `metadata`: Additional gateway-specific data

## API Endpoints

See [API_DOCS.md](API_DOCS.md) for detailed API documentation.

## Admin Interface

All models are registered in the Django admin with:
- Custom list displays with relevant information
- Filtering by key attributes
- Search functionality
- Date hierarchies for time-based filtering

## Management Commands

### init_payments
Initialize the payment system with default configurations:
```bash
python manage.py init_payments
```

## Helper Utilities

The `utils.py` file provides functions for:
- Getting active payment gateways
- Creating dummy transactions for testing
- Processing dummy payments
- Creating refunds
- Initializing the payment system

## Performance

### Caching Implementation

The payment app implements comprehensive caching using Django's core cache framework with Redis as the backend:

1. **Payment Configurations**: Cached for 1 hour (less frequent changes)
2. **Transactions**: Cached for 15 minutes (more dynamic data)
3. **User Transaction Lists**: Cached for 15 minutes
4. **Refunds**: Cached for 15 minutes

See [CACHING_README.md](CACHING_README.md) for detailed caching implementation documentation.

## Best Practices Implemented

1. **Data Integrity**
   - Proper foreign key relationships
   - Data validation
   - Unique constraints where appropriate

2. **Security**
   - Authentication required for all operations
   - Secure storage of API keys
   - Proper error handling

3. **Performance**
   - Proper indexing on frequently queried fields
   - Efficient querying patterns
   - Atomic database operations
   - Redis-based caching for frequently accessed data

4. **Developer Experience**
   - Comprehensive documentation
   - Consistent naming conventions
   - Clear error handling
   - Helpful admin interface

## Installation

1. Ensure the app is in `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       'payment',
       ...
   ]
   ```

2. Add to `urls.py`:
   ```python
   urlpatterns = [
       ...
       path('api/payment/', include('payment.urls')),
       ...
   ]
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations payment
   python manage.py migrate payment
   ```

4. Initialize the payment system:
   ```bash
   python manage.py init_payments
   ```

## Usage Examples

### Creating a Payment Configuration
```python
from payment.models import PaymentConfiguration, PaymentGateway

config = PaymentConfiguration.objects.create(
    gateway=PaymentGateway.STRIPE,
    is_active=True,
    merchant_id='your_merchant_id',
    public_key='your_public_key',
    secret_key='your_secret_key',
    currency='USD'
)
```

### Processing a Dummy Payment
```python
from payment.utils import create_dummy_transaction, process_dummy_payment
from order.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email='customer@example.com')
order = Order.objects.get(order_number='ORD-ABC123')

# Create transaction
transaction = create_dummy_transaction(order, user)

# Process payment
process_dummy_payment(transaction)
```

### Creating a Refund
```python
from payment.utils import create_refund
from payment.models import Transaction

transaction = Transaction.objects.get(transaction_id='TXN-A1B2C3D4E5F6')
refund = create_refund(transaction, amount=50.00, reason='Customer request')
```

## API Integration

### Frontend Integration Example
```javascript
// Get payment configurations
fetch('/api/payment/configurations/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
.then(response => response.json())
.then(configs => {
  console.log('Available payment gateways:', configs);
});

// Create payment intent
fetch('/api/payment/create-intent/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    order_id: 1,
    gateway: 'dummy'
  })
})
.then(response => response.json())
.then(intent => {
  console.log('Payment intent:', intent);
});
```

## Content Management

### Admin Workflow
1. **Configure Gateways**: Set up payment gateway configurations
2. **Monitor Transactions**: Track all payment activities
3. **Process Refunds**: Handle customer refund requests
4. **Review Errors**: Investigate failed transactions

### Configuration Strategy
- **Development**: Use Dummy gateway for testing
- **Staging**: Configure test accounts for real gateways
- **Production**: Activate real payment gateways with production keys

## Integration with Other Systems

The payment system integrates with:

1. **Order System**: Links to Order model for payment processing
2. **User System**: Tracks payments by user
3. **Admin System**: Fully manageable through Django admin

## Extending the App

The modular design makes it easy to extend:
- Add new payment gateways
- Implement subscription payments
- Add recurring payments
- Integrate with accounting systems
- Add advanced fraud detection

## Gateway Integration Guide

### Stripe Integration
1. Sign up for a Stripe account
2. Get your API keys from the Stripe Dashboard
3. Update the PaymentConfiguration in Django admin:
   - Gateway: Stripe
   - Merchant ID: Your Stripe account ID
   - Public Key: Your Stripe publishable key
   - Secret Key: Your Stripe secret key
   - Set as Active

### PayPal Integration
1. Sign up for a PayPal Business account
2. Get your API credentials from the PayPal Developer Dashboard
3. Update the PaymentConfiguration in Django admin:
   - Gateway: PayPal
   - Merchant ID: Your PayPal merchant ID
   - Public Key: Your PayPal client ID
   - Secret Key: Your PayPal secret
   - Set as Active

## Testing

### Dummy Gateway Testing
The dummy gateway is perfect for testing payment flows:
- Always returns success
- No real money involved
- Perfect for unit tests
- Great for development environments

### Testing Checklist
- [ ] Payment intent creation
- [ ] Successful payment processing
- [ ] Failed payment handling
- [ ] Refund processing
- [ ] Partial refund processing
- [ ] Multiple payment methods
- [ ] Edge cases (insufficient funds, etc.)

## Troubleshooting

### Common Issues

1. **Payment Gateway Not Found**
   - Ensure the gateway is configured in PaymentConfiguration
   - Check that the gateway is marked as active

2. **Transaction Not Found**
   - Verify the transaction belongs to the authenticated user
   - Check that the transaction ID is correct

3. **Insufficient Permissions**
   - Ensure the user is authenticated
   - Check that the user owns the order/transaction

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests if applicable
5. Submit a pull request

## License

[Your license information here]