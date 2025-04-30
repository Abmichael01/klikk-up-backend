# wallets/services.py

from decimal import Decimal
from django.db import transaction as db_transaction
from .models import Wallet, Transaction

def get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet

@db_transaction.atomic
def credit_wallet(user, amount: Decimal, description="Wallet credit"):
    wallet = get_or_create_wallet(user)
    wallet.balance += amount
    wallet.save()
    Transaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=Transaction.TransactionType.CREDIT,
        description=description,
    )
    return wallet

@db_transaction.atomic
def debit_wallet(user, amount: Decimal, description="Wallet debit"):
    wallet = get_or_create_wallet(user)
    if wallet.balance < amount:
        raise ValueError("Insufficient wallet balance.")
    wallet.balance -= amount
    wallet.save()
    Transaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=Transaction.TransactionType.DEBIT,
        description=description,
    )
    return wallet
