from decimal import Decimal
from uuid import uuid4
from django.db import transaction as db_transaction
from .models import Wallet, Transaction
from .emails import send_transaction_receipt_email

def get_or_create_wallet(user):
    wallet, _ = Wallet.objects.get_or_create(user=user)
    return wallet

@db_transaction.atomic
def credit_wallet(user, amount: Decimal, description="Wallet credit"):
    wallet = get_or_create_wallet(user)
    wallet.balance += amount
    wallet.save()

    reference = f"CREDIT-{uuid4().hex.upper()[:12]}"

    Transaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=Transaction.TransactionType.CREDIT,
        description=description,
        reference=reference,
    )

    send_transaction_receipt_email(
        user=user,
        amount=amount,
        reference=reference,
        description=description,
        transaction_type="credit",
        balance=wallet.balance
    )

    return wallet

@db_transaction.atomic
def debit_wallet(user, amount: Decimal, reference: str, description="Wallet debit", status=Transaction.TransactionStatus.PENDING):
    
    if not reference:
        raise ValueError("Reference is required for debit transactions.")

    wallet = get_or_create_wallet(user)
    if wallet.balance < amount:
        raise ValueError("Insufficient wallet balance.")

    wallet.balance -= amount
    wallet.save()

    Transaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=Transaction.TransactionType.DEBIT,
        status=status,
        description=description,
        reference=reference,
    )

    send_transaction_receipt_email(
        user=user,
        amount=amount,
        reference=reference,
        description=description,
        transaction_type="debit",
        balance=wallet.balance
    )

    return wallet
