# wallets/emails.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

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
        "date": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
        "year": timezone.now().year,
    }

    try:
        # HTML version
        html_content = render_to_string("transaction.html", context)

        # Fallback plain text
        text_content = f"""
        Hello {context['username']},

        This is a receipt for your recent wallet {transaction_type}.

        Description: {description}
        Amount: ₦{context['amount']}
        Reference: {reference}
        Balance: ₦{balance}
        Date: {context['date']}

        Thank you for using KlikkUp!
        """

        msg = EmailMultiAlternatives(subject, text_content.strip(), from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print("Transaction email sent to:", to_email)
        return True
    except Exception as e:
        print("Transaction email failed:", e)
        return False

    


def send_withdrawal_request_email(user, amount, reference):
    subject = "New Withdrawal Request Submitted"
    from_email = settings.DEFAULT_FROM_EMAIL
    admin_emails = [email for _, email in settings.ADMINS]

    message = f"""
        New withdrawal request submitted:

        User: {user.username} (ID: {user.id}, Email: {user.email})
        Amount: ₦{amount:.2f}
        Reference: {reference}
        Date: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}
        Bank Name: {user.wallet.bank_name}
        Account Name: {user.wallet.account_name}
        Account Number: {user.wallet.account_number}

        Please review this request in the admin dashboard.
        """

    try:
        send_mail(subject, message, from_email, admin_emails)
        return True
    except Exception as e:
        print("Failed to send admin withdrawal email:", e)
        return False
