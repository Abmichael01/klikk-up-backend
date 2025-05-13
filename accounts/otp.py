import random
from django.core.cache import cache

OTP_TTL_SECONDS = 300  # 5 minutes

def generate_otp(length: int = 6) -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(length)])

def store_otp(key: str, otp: str) -> None:
    cache.set(key, otp, timeout=OTP_TTL_SECONDS)

def verify_otp(key: str, otp: str) -> bool:
    stored_otp = cache.get(key)
    if stored_otp and stored_otp == otp:
        cache.delete(key)
        return True
    return False
