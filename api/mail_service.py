import requests
from django.utils import timezone
from django.conf import settings

ZEPTO_MAIL_API_URL = "https://api.zeptomail.com/v1.1/email/template"
ZEPTO_MAIL_AUTH_HEADER = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Zoho-enczapikey {settings.ZEPTO_MAIL_API_KEY}",  # keep in .env
}

def send_coupon_email(username: str, email: str, coupon_code: str) -> bool:
    """Send coupon email using ZeptoMail template"""
    try:
        payload = {
            "template_key": "2d6f.483361808279cbfa.k1.ad7dbe11-2b5c-11f0-8ad3-86f7e6aa0425.196ab7bf470",
            "bounce_address": "bounce@klikkupp.com",  # must be set as verified CNAME
            "from": {
                "address": "noreply@klikkupp.com",
                "name": "KlikkUp"
            },
            "to": [
                {
                    "email_address": {
                        "address": email,
                        "name": username
                    },
                    "merge_info": {
                        "USERNAME": username,
                        "COUPON_CODE": coupon_code,
                        "SIGNUP_URL": f"https://klikk-up.vercel.app/auth/register?coupon_code={coupon_code}",
                        "UNSUBSCRIBE_URL": "https://klikk-up.vercel.app/unsubscribe",
                        "YEAR": str(timezone.now().year)
                    }
                }
            ]
        }

        response = requests.post(
            ZEPTO_MAIL_API_URL,
            headers=ZEPTO_MAIL_AUTH_HEADER,
            json=payload
        )

        response.raise_for_status()  # Raise error for HTTP errors

        return True
    except Exception as e:
        # Optional: log error
        print("Email sending failed:", str(e))
        return False
