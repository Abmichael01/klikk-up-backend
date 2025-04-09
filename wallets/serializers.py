from rest_framework import serializers
from django.db import models

from .models import Wallet, Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'description', 'timestamp']

class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['bank_name', 'bank_code', 'account_name', 'account_number']

class WalletSerializer(serializers.ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)
    earned = serializers.SerializerMethodField()
    withdrawn = serializers.SerializerMethodField()
    pending_withdrawal = serializers.SerializerMethodField()
    bank_details = BankDetailsSerializer(source='*', read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'balance',
            'earned',
            'withdrawn',
            'pending_withdrawal',
            'transactions',
            "bank_details"
        ]
        
    def get_earned(self, obj):
        return sum(tx.amount for tx in obj.transactions.filter(transaction_type=Transaction.TransactionType.CREDIT))

    def get_withdrawn(self, obj):
        return sum(tx.amount for tx in obj.transactions.filter(transaction_type=Transaction.TransactionType.DEBIT))

    def get_pending_withdrawal(self, wallet):
        return wallet.transactions.filter(
            transaction_type=Transaction.TransactionType.DEBIT,
            status=Transaction.TransactionStatus.PENDING
        ).aggregate(total=models.Sum('amount'))['total'] or 0

