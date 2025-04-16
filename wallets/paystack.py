import requests
from django.conf import settings


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