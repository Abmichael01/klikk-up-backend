# wallets/admin.py

from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'bank_name', 'account_name', 'account_number', 'created_at')
    search_fields = ('user__username', 'account_name', 'bank_name', 'account_number')
    readonly_fields = ('created_at',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'wallet', 'transaction_type', 'amount', 'description', 'timestamp')
    search_fields = ('wallet__user__username', 'description', 'transaction_type')
    list_filter = ('transaction_type', 'timestamp')
    readonly_fields = ('id', 'timestamp')
