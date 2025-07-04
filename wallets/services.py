from decimal import Decimal
from uuid import uuid4
from django.db import transaction as db_transaction
from .models import Wallet, Transaction
from .emails import send_transaction_receipt_email, send_withdrawal_request_email
from .models import WithdrawalRequest
from django.utils import timezone

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

    return wallet

def request_withdrawal(user, amount: Decimal):
    wallet = get_or_create_wallet(user)
    if wallet.balance < amount:
        raise ValueError("Insufficient balance for withdrawal.")

    reference = f"WDR-{uuid4().hex[:12].upper()}"

    # Debit now with status=PENDING
    debit_wallet(user, amount, reference=reference, status=Transaction.TransactionStatus.PENDING)

    withdrawal = WithdrawalRequest.objects.create(
        user=user,
        amount=amount,
        reference=reference,
    )
    
    send_withdrawal_request_email(user, amount, reference)

    return withdrawal


def approve_withdrawal(withdrawal: WithdrawalRequest, admin_note="Processed manually"):
    if withdrawal.status != WithdrawalRequest.Status.PENDING:
        raise ValueError("Only pending withdrawals can be approved.")

    withdrawal.status = WithdrawalRequest.Status.APPROVED
    withdrawal.processed_at = timezone.now()
    withdrawal.admin_note = admin_note
    withdrawal.save()

    # Update transaction to SUCCESS
    Transaction.objects.filter(reference=withdrawal.reference).update(status=Transaction.TransactionStatus.SUCCESS)
    
    send_transaction_receipt_email(
        user=withdrawal.user,
        amount=withdrawal.amount,
        reference=withdrawal.reference,
        description="Withdrawal approved",
        transaction_type="withdrawal",
        balance=withdrawal.user.wallet.balance if hasattr(withdrawal.user, 'wallet') else Decimal('0.00')
    )


def reject_withdrawal(withdrawal: WithdrawalRequest, reason="Not eligible"):
    if withdrawal.status != WithdrawalRequest.Status.PENDING:
        raise ValueError("Only pending withdrawals can be rejected.")

    # Refund user
    credit_wallet(withdrawal.user, withdrawal.amount, description="Withdrawal refund")

    withdrawal.status = WithdrawalRequest.Status.REJECTED
    withdrawal.processed_at = timezone.now()
    withdrawal.admin_note = reason
    withdrawal.save()

    Transaction.objects.filter(reference=withdrawal.reference).update(status=Transaction.TransactionStatus.FAILED)

