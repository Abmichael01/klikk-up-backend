from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

def send_coupon_email(username, email, coupon_code):
    subject = 'Complete your registration'
    from_email = "klikkuphelp@gmail.com"
    to_email = email

    context = {
        'username': username,
        'coupon_code': coupon_code,
        'signup_url': 'https://klikk-up.vercel.app/auth/register?coupon_code='+coupon_code,
        'year': timezone.now().year
    }

    html_content = render_to_string('coupon-code.html', context)

    text_content = f"""
    Hi {username},

    We’ve successfully received your payment — thank you!

    To complete your registration on KlikkUp, please use the unique code below:

    {coupon_code}

    You can enter this code during signup by visiting the link below:
    https://klikkupp.com/auth/register?coupon_code={coupon_code}

    If you have any questions or didn’t make this request, feel free to reach out to us at support@klikkup.com.

    Warm regards,  
    The KlikkUp Team

    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
