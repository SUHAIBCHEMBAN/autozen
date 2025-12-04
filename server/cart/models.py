from django.db import models
from django.conf import settings
from django.core.cache import cache
from products.models import Product


class Cart(models.Model):
    """
    Represents a user's shopping cart.
    
    Each user has one cart that persists across sessions. The cart tracks
    items added by the user and provides utility methods for cart operations.
    Cart data is cached for performance optimization.
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
    def items_with_products(self):
        """
        Return cart items with prefetched product data.
        
        This property optimizes database queries by prefetching related
        product information including brand, vehicle model, and part category.
        
        Returns:
            QuerySet: Cart items with prefetched product relationships
        """
        return self.items.select_related(
            'product__brand',
            'product__vehicle_model', 
            'product__part_category'
        )
    
    @property
    def items_count(self):
        """
        Return the number of items in the cart.
        
        This property uses caching to avoid repeated database queries.
        The count is cached for 15 minutes and invalidated when cart
        contents change.
        
        Returns:
            int: Number of distinct items in the cart
        """
        # Try to get from cache first
        cache_key = f"cart_items_count_{self.id}"
        count = cache.get(cache_key)
        
        if count is None:
            count = self.items.count()
            # Cache for 15 minutes
            cache.set(cache_key, count, 60 * 15)
        
        return count
    
    @property
    def total_quantity(self):
        """
        Return the total quantity of all items in the cart.
        
        This property uses database aggregation to efficiently calculate
        the sum of quantities without loading all items into memory.
        The result is cached for 15 minutes.
        
        Returns:
            int: Total quantity of all items in the cart
        """
        # Try to get from cache first
        cache_key = f"cart_total_quantity_{self.id}"
        total = cache.get(cache_key)
        
        if total is None:
            # Use aggregate to avoid loading all items into memory
            from django.db.models import Sum
            result = self.items.aggregate(total=Sum('quantity'))
            total = result['total'] or 0
            # Cache for 15 minutes
            cache.set(cache_key, total, 60 * 15)
        
        return total
    
    @property
    def subtotal(self):
        """
        Return the subtotal of all items in the cart.
        
        This property uses database aggregation to efficiently calculate
        the sum of (quantity * price) for all items without loading
        them into memory. The result is cached for 15 minutes.
        
        Returns:
            Decimal: Subtotal amount for all items in the cart
        """
        # Try to get from cache first
        cache_key = f"cart_subtotal_{self.id}"
        subtotal = cache.get(cache_key)
        
        if subtotal is None:
            # Use aggregate to avoid loading all items into memory
            from django.db.models import Sum, F
            result = self.items.aggregate(
                subtotal=Sum(F('quantity') * F('price'))
            )
            subtotal = result['subtotal'] or 0
            # Cache for 15 minutes
            cache.set(cache_key, subtotal, 60 * 15)
        
        return subtotal
    
    def add_item(self, product, quantity=1):
        """
        Add an item to the cart or update quantity if it already exists.
        
        If the product is already in the cart, the quantity is increased.
        Otherwise, a new cart item is created. The cart timestamp is
        updated and cache is invalidated.
        
        Args:
            product (Product): The product to add to the cart
            quantity (int): The quantity to add (default: 1)
            
        Returns:
            CartItem: The created or updated cart item
        """
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
        
        # Invalidate cart cache
        self._invalidate_cache()
        
        return cart_item
    
    def remove_item(self, product):
        """
        Remove an item from the cart.
        
        Deletes the cart item associated with the given product.
        The cart timestamp is updated and cache is invalidated.
        
        Args:
            product (Product): The product to remove from the cart
            
        Returns:
            bool: True if item was removed, False if item was not in cart
        """
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.delete()
            self.save()
            
            # Invalidate cart cache
            self._invalidate_cache()
            
            return True
        except CartItem.DoesNotExist:
            return False
    
    def update_item_quantity(self, product, quantity):
        """
        Update the quantity of an item in the cart.
        
        Updates the quantity of the cart item associated with the given product.
        If quantity is 0 or negative, the item is removed from the cart.
        The cart timestamp is updated and cache is invalidated.
        
        Args:
            product (Product): The product whose quantity to update
            quantity (int): The new quantity
            
        Returns:
            CartItem: The updated cart item, or None if item not in cart
        """
        if quantity <= 0:
            return self.remove_item(product)
        
        try:
            cart_item = CartItem.objects.get(cart=self, product=product)
            cart_item.quantity = quantity
            cart_item.save()
            self.save()
            
            # Invalidate cart cache
            self._invalidate_cache()
            
            return cart_item
        except CartItem.DoesNotExist:
            return None
    
    def clear(self):
        """
        Clear all items from the cart.
        
        Removes all items from the cart. The cart timestamp is updated
        and cache is invalidated.
        """
        self.items.all().delete()
        self.save()
        
        # Invalidate cart cache
        self._invalidate_cache()
    
    def _invalidate_cache(self):
        """
        Invalidate all cache entries for this cart.
        
        Deletes cached values for items_count, total_quantity, and subtotal
        to ensure data consistency when cart contents change.
        """
        cache_keys = [
            f"cart_items_count_{self.id}",
            f"cart_total_quantity_{self.id}",
            f"cart_subtotal_{self.id}",
        ]
        cache.delete_many(cache_keys)


class CartItem(models.Model):
    """
    Represents an item in a user's shopping cart.
    
    Each cart item represents a product added to a user's cart with a specific
    quantity. The price is captured at the time of adding to preserve pricing
    even if product prices change later.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price at time of adding to cart", null=True, blank=True)
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
        """
        Return the total price for this item (quantity * price).
        
        Calculates the total price by multiplying quantity with the
        captured price. Returns 0 if price is not set.
        
        Returns:
            Decimal: Total price for this cart item (quantity * price)
        """
        if self.price is None:
            return 0
        return self.quantity * self.price
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure price is set.
        
        If price is not explicitly set, it's captured from the product
        at the time of saving to preserve pricing history.
        """
        if self.price is None and self.product:
            self.price = self.product.price
        super().save(*args, **kwargs)