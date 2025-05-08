import requests
from django.conf import settings
import uuid
from .services import debit_wallet
from .models import Transaction as TransactionModel


SECRET_KEY = settings.PAYSTACK_SECRET_KEY

class Paystack():
    pass
    
class Transaction():
    def __init__(self):
        self.base_url = "https://api.paystack.co/"
        self.headers = {
            "Authorization": f"Bearer {SECRET_KEY}",
            "Content-Type": "application/json",
        }
        
    def initialize(self, amount, email, *args, **kwargs):
        url = self.base_url + "transaction/initialize"
        data = {
            "amount": int(amount) * 100,  # Paystack expects kobo
            "email": email,
        }
        response = requests.post(url=url, headers=self.headers, json=data)

        response_data = response.json()

        if response.status_code == 200 and response_data['status']:
            return response_data['status'], response_data['data']

        return response_data['status'], response_data.get('message', 'Transaction initialization failed')

    
    
    def verify(self, ref, *args, **kwargs):
        path = f'transaction/verify/{ref}'
        url = self.base_url + path
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            response_data = response.json()
            return response_data['status'], response_data['data']

        response_data = response.json()

        return response_data['status'], response_data['message']
    

class Transfer:
    def __init__(self):
        self.base_url = "https://api.paystack.co/"
        self.headers = {
            "Authorization": f"Bearer {SECRET_KEY}",
            "Content-Type": "application/json",
        }

    def generate_reference(self) -> str:
        """Generate a UUID4-based transfer reference"""
        return f"TRF-{uuid.uuid4().hex.upper()}"

    def create_recipient(self, name: str, account_number: str, bank_code: str, currency: str = "NGN"):
        url = self.base_url + "transferrecipient"
        data = {
            "type": "nuban",
            "name": name,
            "account_number": account_number,
            "bank_code": bank_code,
            "currency": currency
        }

        response = requests.post(url, headers=self.headers, json=data)
        response_data = response.json()

        if response_data['status']:
            return response_data['data']['recipient_code']
        else:
            raise Exception(f"Recipient creation failed: {response_data.get('message', 'Unknown error')}")

    def initiate_transfer(self, user, amount: int, recipient_code: str, reason: str = "Wallet withdrawal"):
        """
        Initiate a transfer in kobo (so ₦1000 = 100000)
        """
        url = self.base_url + "transfer"
        
        reference = self.generate_reference()
        
        data = {
            "source": "balance",
            "amount": int(amount) * 100,  # Paystack uses kobo
            "recipient": recipient_code,
            "reference": reference,
            "reason": reason
        }

        response = requests.post(url, headers=self.headers, json=data)
        response_data = response.json()

        if response_data['status']:
            print(response_data)
            
            debit_wallet(
                user=user,
                amount=amount,
                reference=response_data["data"].get("reference"),
                description="Wallet withdrawal",
                status=TransactionModel.TransactionStatus.PENDING
            )
            
            return {
                "status": True,
                "reference": response_data["data"].get("reference"),
                "transfer_code": response_data["data"].get("transfer_code"),
                "message": response_data["message"]
            }
        else:
            raise Exception(f"Transfer initiation failed: {response_data.get('message', 'Unknown error')}")
