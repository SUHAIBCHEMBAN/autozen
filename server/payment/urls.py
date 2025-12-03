from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    # Payment configurations
    path('configurations/', views.PaymentConfigurationListView.as_view(), name='payment-configurations'),
    
    # Transactions
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<str:transaction_id>/', views.TransactionDetailView.as_view(), name='transaction-detail'),
    
    # Payment processing
    path('create-intent/', views.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('process/', views.ProcessPaymentView.as_view(), name='process-payment'),
    
    # Refunds
    path('refund/', views.RefundTransactionView.as_view(), name='refund-transaction'),
]