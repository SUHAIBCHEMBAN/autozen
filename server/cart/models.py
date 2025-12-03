from django.db import models
from django.conf import settings
from products.models import Product


class Cart(models.Model):
    """
    Represents a user's shopping cart
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user}'s Cart"
    
    @property
    def items_count(self):
        """Return the number of items in the cart"""
        return self.items.count()
    
    @property
    def total_quantity(self):
        """Return the total quantity of all items in the cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Return the subtotal of all items in the cart"""
        return sum(item.total_price for item in self.items.all())
    
    def add_item(self, product, quantity=1):
        """Add an item to the cart or update quantity if it already exists"""
        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Update cart timestamp
        self.save()
        return cart_item
    
    def remove_item(self, product):
        """Remove an item from the cart"""
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.delete()
            self.save()
            return True
        except CartItem.DoesNotExist:
            return False
    
    def update_item_quantity(self, product, quantity):
        """Update the quantity of an item in the cart"""
        if quantity <= 0:
            return self.remove_item(product)
        
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.quantity = quantity
            cart_item.save()
            self.save()
            return cart_item
        except CartItem.DoesNotExist:
            return None
    
    def clear(self):
        """Clear all items from the cart"""
        self.items.all().delete()
        self.save()


class CartItem(models.Model):
    """
    Represents an item in a user's shopping cart
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of adding to cart")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['cart', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user}'s Cart"
    
    @property
    def total_price(self):
        """Return the total price for this item (quantity * price)"""
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        """Override save to ensure price is set"""
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)