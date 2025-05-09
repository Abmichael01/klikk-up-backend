from django.conf import settings
from django.db import models
import uuid

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_code = models.CharField(max_length=255, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    
class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        CREDIT = "CREDIT", "Credit"
        DEBIT = "DEBIT", "Debit"

    class TransactionStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey('Wallet', on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    status = models.CharField(max_length=10, choices=TransactionStatus.choices, default=TransactionStatus.SUCCESS)
    description = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, unique=True, help_text="Unique transaction reference for traceability.", default="")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.transaction_type} of ₦{self.amount} - {self.wallet.user.username} [{self.status}]"