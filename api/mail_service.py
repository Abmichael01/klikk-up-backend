from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

def send_coupon_email(username, email, coupon_code):
    subject = 'Finish setting up your KlikkUp account'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = email

    context = {
        'username': username,
        'coupon_code': coupon_code,
        'signup_url': f'https://klikkupp.com/auth/register?coupon_code={coupon_code}',
        'unsubscribe_url': 'https://klikk-up.vercel.app/unsubscribe',
        'year': timezone.now().year
    }

    html_content = render_to_string('coupon-code.html', context)

    text_content = f"""
    Hi {username},

    Thanks for joining KlikkUp!

    To complete your registration, use the verification code below:

    {coupon_code}

    Click this link to sign up:
    {context['signup_url']}

    If you didn’t request this, just ignore this message or contact us at support@klikkup.com.

    – KlikkUp Team
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
        return True
    except Exception as e:
        print("Email sending failed:", str(e))
        return False
