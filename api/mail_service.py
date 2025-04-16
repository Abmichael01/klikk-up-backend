from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

def send_coupon_email(username, email, coupon_code):
    subject = 'Your Coupon Code is Ready!'
    from_email = settings.EMAIL_HOST_USER
    to_email = email

    context = {
        'username': username,
        'coupon_code': coupon_code,
        'signup_url': 'https://klikk-up.vercel.app/auth/register?coupon_code='+coupon_code,
        'year': timezone.now().year
    }

    html_content = render_to_string('coupon-code.html', context)

    text_content = f"""
    Hi {username}!

    Thanks for your payment — here’s your coupon code:

    {coupon_code}

    Use it to signup here: https://yourwebsite.com/signup

    Thanks,
    Your Brand
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
