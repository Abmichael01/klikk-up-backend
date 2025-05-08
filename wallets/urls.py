# wallets/urls.py

from django.urls import path
from .views import WalletDetailView, BankDetailsView, BuyCoupon, PaystackWebhook, WithdrawView

urlpatterns = [
    path('wallet/', WalletDetailView.as_view(), name='wallet-detail'),
    path('wallet/bank-details/', BankDetailsView.as_view(), name='bank-details'),
    path("buy-coupon/", BuyCoupon.as_view(), name="initiate-buy-coupon"),
    path("buy-coupon/<str:ref>/", BuyCoupon.as_view(), name="verify-buy-coupon"),
    path('webhook/paystack/', PaystackWebhook.as_view(), name='paystack-webhook'),
    path('wallet/withdraw/', WithdrawView.as_view())
]
