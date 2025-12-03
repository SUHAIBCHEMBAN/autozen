# Order App Documentation

This Django app provides a complete order management system for an automotive spare parts and accessories e-commerce platform.

## Overview

The order app implements a comprehensive system for handling customer orders, including:

- Order creation and management
- Checkout processing
- Order tracking and status updates
- User-specific access control
- Order history
- Notification system
- Admin interface

## Key Features

### Order Management
- Complete order lifecycle from creation to delivery
- Status tracking with automatic timestamp updates
- Comprehensive order details including customer information, billing/shipping addresses, and pricing
- Order item tracking with historical product data
- Status change logging

### Checkout Processing
- Secure checkout process
- Validation of product availability
- Automatic stock quantity updates
- Tax and shipping cost calculations
- Multiple payment method support

### Order Tracking
- Real-time order status updates
- Shipment and delivery tracking
- Status change notifications
- Customer communication system

### Security & Access Control
- User-specific order access (customers can only view their own orders)
- Staff access controls for order management
- Data integrity through historical product data storage

### Admin Interface
- Comprehensive admin panel for order management
- Inline editing of order items and status logs
- Advanced filtering and search capabilities
- Status change tracking

## Models

### Order
Represents a customer order with all associated information.

Key fields:
- `order_number`: Unique order identifier
- `user`: Customer who placed the order
- Customer information (name, email, phone)
- Billing and shipping addresses
- `status`: Current order status
- `payment_method`: Selected payment method
- `payment_status`: Payment completion status
- Pricing fields (subtotal, tax, shipping, discount, total)

### OrderItem
Represents a single item in an order.

Key fields:
- `order`: Parent order
- `product`: Ordered product
- Historical product data (name, SKU, price)
- `quantity`: Number of items ordered
- `total_price`: Quantity × unit price

### OrderStatusLog
Tracks all status changes for an order.

Key fields:
- `order`: Parent order
- `old_status`: Previous status
- `new_status`: Updated status
- `timestamp`: When the change occurred
- `notes`: Additional information

### OrderNotification
Tracks notifications sent to customers about their orders.

Key fields:
- `order`: Parent order
- `notification_type`: Type of notification
- `sent_at`: When it was sent
- `sent_to`: Recipient email
- `subject` and `message`: Notification content

## API Endpoints

See [API_DOCS.md](API_DOCS.md) for detailed API documentation.

## Status Flow

The order system implements the following status flow:

1. `pending` - Order placed but not yet confirmed
2. `confirmed` - Order confirmed, awaiting processing
3. `processing` - Order is being processed
4. `shipped` - Order has been shipped
5. `out_for_delivery` - Order is out for delivery
6. `delivered` - Order has been delivered
7. `cancelled` - Order was cancelled
8. `returned` - Order was returned
9. `refunded` - Order was refunded

## Payment Methods

Supported payment methods:
- Credit Card
- Debit Card
- PayPal
- Bank Transfer
- Cash on Delivery
- UPI

## Security Features

- User-specific access control (customers can only view their own orders)
- Staff-only access to order management features
- Historical product data storage prevents data inconsistency
- Automatic stock quantity updates prevent overselling

## Admin Interface

All models are registered in the Django admin with:
- Custom list displays with relevant information
- Filtering by key attributes
- Search functionality
- Inline editing for related models
- Organized fieldsets for easy editing

## Management Commands

### populate_orders
Creates sample orders for testing:
```bash
python manage.py populate_orders
```

## Helper Utilities

The `utils.py` file provides functions for:
- Sending order confirmation emails
- Sending shipping and delivery notifications
- Calculating order totals
- Validating stock availability
- Updating product stock quantities

## Best Practices Implemented

1. **Data Integrity**
   - Historical product data storage
   - Proper foreign key relationships
   - Unique constraints where appropriate

2. **Security**
   - User-specific access control
   - Staff-only administrative functions
   - Data validation

3. **Performance**
   - Proper indexing on frequently queried fields
   - Efficient querying patterns
   - Select/prefetch related optimizations

4. **Scalability**
   - Modular design with clear separation of concerns
   - Efficient serialization strategies
   - Pagination support

5. **Developer Experience**
   - Comprehensive documentation
   - Consistent naming conventions
   - Clear error handling
   - Helpful admin interface

## Installation

1. Ensure the app is in `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       'order',
       ...
   ]
   ```

2. Add to `urls.py`:
   ```python
   urlpatterns = [
       ...
       path('api/orders/', include('order.urls')),
       ...
   ]
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations order
   python manage.py migrate order
   ```

## Usage Examples

### Creating an Order
```python
from order.models import Order, OrderItem
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()
user = User.objects.get(email="customer@example.com")
product = Product.objects.get(sku="SW-001")

# Create order
order = Order.objects.create(
    user=user,
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    phone_number="+1234567890",
    billing_address_line1="123 Main St",
    billing_city="New York",
    billing_state="NY",
    billing_postal_code="10001",
    billing_country="USA",
    shipping_address_line1="123 Main St",
    shipping_city="New York",
    shipping_state="NY",
    shipping_postal_code="10001",
    shipping_country="USA",
    payment_method="credit_card",
    subtotal=Decimal('100.00'),
    tax_amount=Decimal('8.00'),
    shipping_cost=Decimal('10.00'),
    total_amount=Decimal('118.00')
)

# Add items to order
OrderItem.objects.create(
    order=order,
    product=product,
    quantity=2,
    product_price=product.price,
    total_price=product.price * 2
)
```

### Updating Order Status
```python
from order.models import Order, OrderStatus

order = Order.objects.get(order_number="ORD-A1B2C3D4")
order.update_status(OrderStatus.SHIPPED)
```

### Checking Order Eligibility for Cancellation
```python
from order.models import Order

order = Order.objects.get(order_number="ORD-A1B2C3D4")
if order.can_be_cancelled():
    order.update_status(OrderStatus.CANCELLED)
```

## Extending the App

The modular design makes it easy to extend:
- Add new order statuses
- Implement additional payment methods
- Customize notification system
- Add new fields to existing models
- Create additional serializers for specific use cases

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests if applicable
5. Submit a pull request

## License

[Your license information here]