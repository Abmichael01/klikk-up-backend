from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .paystack import Transaction
from .models import Wallet
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
    permission_classes = []  # No auth — Paystack uses a secret signature

    def post(self, request, *args, **kwargs):
        # Verify signature
        paystack_secret = settings.PAYSTACK_SECRET_KEY.encode()
        signature = request.headers.get('x-paystack-signature')

        computed_signature = hmac.new(
            paystack_secret, 
            request.body, 
            hashlib.sha512
        ).hexdigest()

        if signature != computed_signature:
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        event = json.loads(request.body)
        event_type = event.get("event")
        data = event.get("data", {})

        if event_type == "charge.success":
            reference = data.get("reference")
            email = data.get("customer", {}).get("email")

            coupon_code = generate_coupon_code()
            
            coupon, created = Coupon.objects.get_or_create(code=coupon_code)
            # Send the email
            send_coupon_email(
                username= "Aspiring KlikkUp User",
                email=email,
                coupon_code=coupon_code
            )
            coupon.sold = True
            coupon.save()
            
            # TODO: Mark your transaction as successful in your database
            print(f"Payment successful: {reference}, Email: {email}")

        return Response({"status": "ok"}, status=status.HTTP_200_OK)