from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from products.models import Product, Brand, VehicleModel, PartCategory
from products.admin import ProductAdmin, BrandAdmin, VehicleModelAdmin, PartCategoryAdmin
from order.models import Order, OrderItem, OrderStatusLog, OrderNotification
from order.admin import OrderAdmin, OrderItemAdmin, OrderStatusLogAdmin, OrderNotificationAdmin
from users.models import User as CustomUser
from users.admin import CustomUserAdmin
from cart.models import Cart, CartItem
from cart.admin import CartAdmin, CartItemAdmin
from wishlist.models import Wishlist, WishlistItem
from wishlist.admin import WishlistAdmin, WishlistItemAdmin
from pages.models import Page, FAQ
from pages.admin import PageAdmin, FAQAdmin
from landing.models import (
    HeroBanner, CategorySection, AdvertisementBanner, 
    Testimonial, LandingPageConfiguration, FeaturedVehicle
)
from landing.admin import (
    HeroBannerAdmin, CategorySectionAdmin, AdvertisementBannerAdmin, 
    TestimonialAdmin, LandingPageConfigurationAdmin, FeaturedVehicleAdmin
)
from payment.models import PaymentConfiguration, Transaction, Refund
from payment.admin import PaymentConfigurationAdmin, TransactionAdmin, RefundAdmin


class CustomAdminSite(AdminSite):
    site_header = 'AutoZen Administration'
    site_title = 'AutoZen Admin'
    index_template = 'admin/index.html'

    def index(self, request, extra_context=None):
        from django.db.models import Count, Sum, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        # Calculate date ranges for comparison
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Users statistics
        total_users = CustomUser.objects.count()
        new_users_today = CustomUser.objects.filter(date_joined__date=today).count()
        new_users_week = CustomUser.objects.filter(date_joined__gte=week_ago).count()
        new_users_month = CustomUser.objects.filter(date_joined__gte=month_ago).count()
        
        # Products statistics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        featured_products = Product.objects.filter(is_featured=True).count()
        out_of_stock_products = Product.objects.filter(stock_quantity=0).count()
        low_stock_products = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lt=10).count()
        
        # Brands statistics
        total_brands = Brand.objects.count()
        
        # Orders statistics
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        confirmed_orders = Order.objects.filter(status='confirmed').count()
        shipped_orders = Order.objects.filter(status='shipped').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        returned_orders = Order.objects.filter(status='returned').count()
        
        # Sales statistics
        total_sales = Order.objects.filter(status='delivered').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Average order value
        avg_order_value = Order.objects.filter(status='delivered').aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0
        
        # Conversion rate (orders/customers)
        conversion_rate = 0
        if total_users > 0:
            conversion_rate = (total_orders / total_users) * 100
        
        # Monthly sales trend (last 6 months)
        monthly_sales = []
        monthly_labels = []
        
        for i in range(5, -1, -1):
            start_date = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
            
            monthly_revenue = Order.objects.filter(
                status='delivered',
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            monthly_sales.append(float(monthly_revenue))
            monthly_labels.append(start_date.strftime('%b %Y'))
        
        # Recent orders
        recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
        
        # Revenue chart data (last 30 days)
        revenue_data = []
        orders_data = []
        dates = []
        
        for i in range(29, -1, -1):
            date = today - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
            
            daily_revenue = Order.objects.filter(
                status='delivered',
                created_at__date=date
            ).aggregate(
                total=Sum('total_amount')
            )['total'] or 0
            
            daily_orders = Order.objects.filter(
                created_at__date=date
            ).count()
            
            revenue_data.append(float(daily_revenue))
            orders_data.append(daily_orders)
        
        # Top selling products with revenue calculation
        top_products = Product.objects.annotate(
            total_sold=Sum('order_items__quantity')
        ).filter(
            total_sold__gt=0
        ).order_by('-total_sold')[:10]
        
        # Add revenue calculation to each product
        for product in top_products:
            product.revenue = (product.total_sold or 0) * product.price
        
        # Recent carts and wishlists
        recent_carts = Cart.objects.select_related('user').prefetch_related(
            'items__product'
        ).order_by('-updated_at')[:5]
        
        recent_wishlists = Wishlist.objects.select_related('user').prefetch_related(
            'items__product'
        ).order_by('-updated_at')[:5]
        
        # Calculate percentages for progress bars
        pending_orders_pct = (pending_orders / total_orders * 100) if total_orders > 0 else 0
        confirmed_orders_pct = (confirmed_orders / total_orders * 100) if total_orders > 0 else 0
        shipped_orders_pct = (shipped_orders / total_orders * 100) if total_orders > 0 else 0
        delivered_orders_pct = (delivered_orders / total_orders * 100) if total_orders > 0 else 0
        cancelled_orders_pct = (cancelled_orders / total_orders * 100) if total_orders > 0 else 0
        
        active_products_pct = (active_products / total_products * 100) if total_products > 0 else 0
        out_of_stock_products_pct = (out_of_stock_products / total_products * 100) if total_products > 0 else 0
        low_stock_products_pct = (low_stock_products / total_products * 100) if total_products > 0 else 0
        featured_products_pct = (featured_products / total_products * 100) if total_products > 0 else 0
        
        # Customer statistics
        total_carts = Cart.objects.count()
        total_wishlists = Wishlist.objects.count()
        
        # Revenue breakdown by status
        revenue_by_status = {
            'delivered': Order.objects.filter(status='delivered').aggregate(total=Sum('total_amount'))['total'] or 0,
            'shipped': Order.objects.filter(status='shipped').aggregate(total=Sum('total_amount'))['total'] or 0,
            'confirmed': Order.objects.filter(status='confirmed').aggregate(total=Sum('total_amount'))['total'] or 0,
            'pending': Order.objects.filter(status='pending').aggregate(total=Sum('total_amount'))['total'] or 0,
        }
        
        # Inventory alerts
        inventory_alerts = Product.objects.filter(stock_quantity__lt=10).order_by('stock_quantity')[:10]
        
        # Customer snapshot
        customers_snapshot = {
            'total': total_users,
            'new_this_week': new_users_week,
            'with_orders': CustomUser.objects.filter(orders__isnull=False).distinct().count(),
            'with_wishlist': CustomUser.objects.filter(wishlist__isnull=False).distinct().count(),
        }
        
        context = {
            **self.each_context(request),
            # Users stats
            'total_users': total_users,
            'new_users_today': new_users_today,
            'new_users_week': new_users_week,
            'new_users_month': new_users_month,
            
            # Products stats
            'total_products': total_products,
            'active_products': active_products,
            'featured_products': featured_products,
            'out_of_stock_products': out_of_stock_products,
            'low_stock_products': low_stock_products,
            'total_brands': total_brands,
            
            # Orders stats
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'shipped_orders': shipped_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'returned_orders': returned_orders,
            
            # Percentages for progress bars
            'pending_orders_pct': pending_orders_pct,
            'confirmed_orders_pct': confirmed_orders_pct,
            'shipped_orders_pct': shipped_orders_pct,
            'delivered_orders_pct': delivered_orders_pct,
            'cancelled_orders_pct': cancelled_orders_pct,
            
            'active_products_pct': active_products_pct,
            'out_of_stock_products_pct': out_of_stock_products_pct,
            'low_stock_products_pct': low_stock_products_pct,
            'featured_products_pct': featured_products_pct,
            
            # Sales stats
            'total_sales': total_sales,
            'avg_order_value': avg_order_value,
            'conversion_rate': conversion_rate,
            'recent_orders': recent_orders,
            
            # Chart data
            'revenue_data': revenue_data,
            'orders_data': orders_data,
            'dates': dates,
            'monthly_sales': monthly_sales,
            'monthly_labels': monthly_labels,
            
            # Top products
            'top_products': top_products,
            
            # Recent activity
            'recent_carts': recent_carts,
            'recent_wishlists': recent_wishlists,
            
            # Customer stats
            'total_carts': total_carts,
            'total_wishlists': total_wishlists,
            
            # New additions for enhanced dashboard
            'revenue_by_status': revenue_by_status,
            'inventory_alerts': inventory_alerts,
            'customers_snapshot': customers_snapshot,
        }
        
        context.update(extra_context or {})
        return super().index(request, extra_context=context)


# Create an instance of our custom admin site
custom_admin_site = CustomAdminSite(name='custom_admin')

# Register your models here with the custom admin site
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
custom_admin_site.register(CustomUser, CustomUserAdmin)
custom_admin_site.register(Product, ProductAdmin)
custom_admin_site.register(Brand, BrandAdmin)
custom_admin_site.register(VehicleModel, VehicleModelAdmin)
custom_admin_site.register(PartCategory, PartCategoryAdmin)
custom_admin_site.register(Order, OrderAdmin)
custom_admin_site.register(OrderItem, OrderItemAdmin)
custom_admin_site.register(OrderStatusLog, OrderStatusLogAdmin)
custom_admin_site.register(OrderNotification, OrderNotificationAdmin)
custom_admin_site.register(Cart, CartAdmin)
custom_admin_site.register(CartItem, CartItemAdmin)
custom_admin_site.register(Wishlist, WishlistAdmin)
custom_admin_site.register(WishlistItem, WishlistItemAdmin)
custom_admin_site.register(Page, PageAdmin)
custom_admin_site.register(FAQ, FAQAdmin)
custom_admin_site.register(HeroBanner, HeroBannerAdmin)
custom_admin_site.register(FeaturedVehicle, FeaturedVehicleAdmin)
custom_admin_site.register(CategorySection, CategorySectionAdmin)
custom_admin_site.register(AdvertisementBanner, AdvertisementBannerAdmin)
custom_admin_site.register(Testimonial, TestimonialAdmin)
custom_admin_site.register(LandingPageConfiguration, LandingPageConfigurationAdmin)
custom_admin_site.register(PaymentConfiguration, PaymentConfigurationAdmin)
custom_admin_site.register(Transaction, TransactionAdmin)
custom_admin_site.register(Refund, RefundAdmin)