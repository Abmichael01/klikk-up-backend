from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .paystack import Transaction, Transfer
from .models import Wallet, Transaction as TransactionModel
from .serializers import WalletSerializer, BankDetailsSerializer
from rest_framework.views import APIView
from django.conf import settings
import json
import hmac
import hashlib
from api.mail_service import send_coupon_email
import random
import string
from admin_panel.models import Coupon
from api.utils import generate_coupon_code
from .services import debit_wallet, get_or_create_wallet, request_withdrawal  # your existing util
import uuid
from decimal import Decimal
from django.db.models import Q
from accounts.otp import verify_otp 


class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        return wallet

class BankDetailsView(generics.UpdateAPIView):
    serializer_class = BankDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        wallet, created = Wallet.objects.get_or_create(user=self.request.user)
        return wallet

class BuyCoupon(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        amount = request.data.get("amount", 3000)
        
        print(email)

        if not email:
            return Response({"message": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction()
        txn_status, txn_response = transaction.initialize(amount=3000, email=email)

        if txn_status:
            return Response({
                "message": "Transaction initialized successfully.",
                "data": txn_response
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Failed to initialize transaction.",
                "error": txn_response
            }, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        ref = request.query_params.get("ref")
        if not ref:
            return Response({"message": "Reference is required."}, status=status.HTTP_400_BAD_REQUEST)

        transaction = Transaction()
        verify_status, verify_response = transaction.verify(ref=ref)

        if verify_status:
            return Response({
                "message": "Transaction verified successfully.",
                "data": verify_response
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Failed to verify transaction.",
                "error": verify_response
            }, status=status.HTTP_400_BAD_REQUEST)


class PaystackWebhook(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        signature = request.headers.get('x-paystack-signature')
        secret = settings.PAYSTACK_SECRET_KEY.encode()

        computed_signature = hmac.new(
            secret,
            request.body,
            hashlib.sha512
        ).hexdigest()

        if signature != computed_signature:
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        event = json.loads(request.body)
        event_type = event.get("event")
        data = event.get("data", {})

        if event_type == "charge.success":
            self.handle_charge_success(data)

        elif event_type == "transfer.success":
            self.handle_transfer_success(data)

        elif event_type == "transfer.failed":
            self.handle_transfer_failed(data)

        elif event_type == "transfer.reversed":
            self.handle_transfer_reversed(data)

        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    def handle_charge_success(self, data):
        reference = data.get("reference")
        email = data.get("customer", {}).get("email")

        if not email or not reference:
            return

        coupon_code = generate_coupon_code()
        coupon, _ = Coupon.objects.get_or_create(code=coupon_code)

        send_coupon_email(
            username="Aspiring KlikkUp User",
            email=email,
            coupon_code=coupon_code
        )

        coupon.sold = True
        coupon.save()

        print(f"[Charge Success] Reference: {reference}, Email: {email}")

    def handle_transfer_success(self, data):
        reference = data.get("reference")
        amount = data.get("amount")
        recipient = data.get("recipient", {}).get("name", "Unknown")
        print(f"[Transfer Success] Reference: {reference}, Amount: {amount}, Recipient: {recipient}")
        print(data)

        # Update the transaction status
        transaction = TransactionModel.objects.filter(reference=reference).first()
        print(transaction)
        
        while transaction == None:
            print("checking again.... \n")
            transaction = TransactionModel.objects.filter(reference=reference).first()
            
        if transaction:
            print(transaction)
            transaction.status=TransactionModel.TransactionStatus.SUCCESS
            transaction.save()
            print(transaction)
        else:
            print(f" \n [WARN] No transaction found with reference {reference} \n")

    def handle_transfer_failed(self, data):
        reference = data.get("reference")
        reason = data.get("reason")
        print(f"[Transfer Failed] Reference: {reference}, Reason: {reason}")

        transaction = TransactionModel.objects.filter(reference=reference).first()
        print(transaction)
        
        while transaction == None:
            print("checking again.... \n")
            transaction = TransactionModel.objects.filter(reference=reference).first()
            
        if transaction:
            print(transaction)
            transaction.status=TransactionModel.TransactionStatus.FAILED
            transaction.save()
            print(transaction)
        else:
            print(f" \n [WARN] No transaction found with reference {reference} \n") 

    def handle_transfer_reversed(self, data):
        reference = data.get("reference")
        reason = data.get("reason")
        print(f"[Transfer Reversed] Reference: {reference}, Reason: {reason}")

        updated = TransactionModel.objects.filter(reference=reference).update(status=TransactionModel.TransactionStatus.FAILED)
        if updated == 0:
            print(f"[WARN] No transaction found with reference {reference}")


        # Optional: Flag reversal in transaction table
        
        
class WithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        amount = request.data.get("amount")
        otp = request.data.get("otp")

        # Validate OTP
        if not otp:
            return Response({"message": "OTP is required to confirm withdrawal."},
                            status=status.HTTP_400_BAD_REQUEST)
        elif not verify_otp(f"otp:{user.email}", otp):
            return Response({"message": "Invalid or expired OTP."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate amount
        if not amount:
            return Response({"message": "Amount is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = Decimal(str(amount))
        except:
            return Response({"message": "Invalid amount format."}, status=status.HTTP_400_BAD_REQUEST)

        # Check bank details
        wallet = get_or_create_wallet(user)
        if not all([wallet.bank_code, wallet.account_number, wallet.account_name]):
            return Response({"message": "Bank details are incomplete. Please set up your bank information."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create withdrawal request (and debit immediately with status=PENDING)
            withdrawal = request_withdrawal(user, amount)

            return Response({
                "message": "Withdrawal request submitted successfully.",
                "reference": withdrawal.reference,
                "status": withdrawal.status,
            }, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            return Response({"message": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)