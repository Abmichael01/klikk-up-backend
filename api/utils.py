import random
import string
from admin_panel.models import Coupon  # adjust path as needed

def generate_coupon_code(length=6):
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))
        if not Coupon.objects.filter(code=code).exists():
            return code
