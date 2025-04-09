# wallets/urls.py

from django.urls import path
from .views import WalletDetailView, BankDetailsView

urlpatterns = [
    path('wallet/', WalletDetailView.as_view(), name='wallet-detail'),
    path('wallet/bank-details/', BankDetailsView.as_view(), name='bank-details'),
]
