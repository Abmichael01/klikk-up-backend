# wallets/admin.py

from django.contrib import admin

from wallets.services import approve_withdrawal, reject_withdrawal
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

from .models import WithdrawalRequest

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'reference', 'get_bank_name', 'get_account_name', 'get_account_number', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'reference')
    readonly_fields = ('created_at', 'processed_at')
    ordering = ('-created_at',)

    actions = ['mark_as_approved', 'mark_as_rejected']

    def get_queryset(self, request):
        """Optionally filter to show only pending withdrawals by default."""
        qs = super().get_queryset(request)
        if request.GET.get('status__exact') is None:
            return qs.filter(status=WithdrawalRequest.Status.PENDING)
        return qs
    
    @admin.display(description="Bank Name")
    def get_bank_name(self, obj):
        return getattr(obj.user.wallet, 'bank_name', '-')

    @admin.display(description="Account Name")
    def get_account_name(self, obj):
        return getattr(obj.user.wallet, 'account_name', '-')

    @admin.display(description="Account Number")
    def get_account_number(self, obj):
        return getattr(obj.user.wallet, 'account_number', '-')
    
    def save_model(self, request, obj, form, change):
        if change:
            old_obj = WithdrawalRequest.objects.get(pk=obj.pk)
            if (
                old_obj.status == WithdrawalRequest.Status.PENDING and
                obj.status == WithdrawalRequest.Status.APPROVED
            ):
                approve_withdrawal(obj, admin_note=obj.admin_note or "Approved via admin panel")
                return
        super().save_model(request, obj, form, change)
        
    def mark_as_approved(self, request, queryset):
        success_count = 0
        skipped_count = 0

        for withdrawal in queryset:
            if withdrawal.status == WithdrawalRequest.Status.PENDING:
                try:
                    approve_withdrawal(withdrawal, admin_note="Approved via bulk action")
                    success_count += 1
                except Exception as e:
                    skipped_count += 1
                    print(f"Failed to approve {withdrawal.reference}: {e}")
            else:
                skipped_count += 1

        self.message_user(
            request,
            f"{success_count} withdrawal(s) approved. {skipped_count} skipped (already processed or error)."
        )
    mark_as_approved.short_description = "Mark selected as Approved"
    # import your existing function

    def mark_as_rejected(self, request, queryset):
        success_count = 0
        skipped_count = 0

        for withdrawal in queryset:
            if withdrawal.status == WithdrawalRequest.Status.PENDING:
                try:
                    reject_withdrawal(withdrawal, reason="Rejected via bulk action")
                    success_count += 1
                except Exception as e:
                    skipped_count += 1
                    print(f"Failed to reject {withdrawal.reference}: {e}")
            else:
                skipped_count += 1

        self.message_user(
            request,
            f"{success_count} withdrawal(s) rejected. {skipped_count} skipped (already processed or error)."
        )
    mark_as_rejected.short_description = "Mark selected as Rejected"

