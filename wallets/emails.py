# wallets/emails.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings

def send_transaction_receipt_email(user, amount, reference, description, transaction_type, balance):
    subject = f"KlikkUp Wallet - {transaction_type.title()} Receipt"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    context = {
        "username": user.username,
        "amount": f"{amount:.2f}",
        "reference": reference,
        "description": description,
        "balance": balance,
        "transaction_type": transaction_type.upper(),
        "date": timezone.now(),
        "year": timezone.now().year,
    }

    html_content = render_to_string("transaction.html", context)
    text_content = f"""
    Hello {context['username']},

    This is a receipt for your recent wallet {transaction_type}.

    Description: {description}
    Amount: {context['amount']}
    Reference: {reference}
    Balance: {balance}
    Date: {context['date'].strftime("%Y-%m-%d %H:%M:%S")}

    Thank you for using KlikkUp!
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")

    try:
        msg.send()
        return True
    except Exception as e:
        print("Transaction email failed:", e)
        return False
