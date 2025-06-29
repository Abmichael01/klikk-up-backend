import random
import string
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from admin_panel.models import Coupon

User = get_user_model()

class Command(BaseCommand):
    help = 'Create 200 fake users with coupons and referral structure'

    DOMAINS = ['gmail.com', 'yahoo.com', 'outlook.com']
    USERNAME_POOL = [
        "ayobami23", "chidera007", "emeka94", "kemi101", "tomiwa88", "ibrahim42", "damilola75", "sade2000",
        "segun96", "ifeanyi32", "yusuf11", "uche56", "maryam04", "zainab777", "fatima09", "adesuwa45",
        "ngozi91", "ebuka61", "chuka13", "blessing22", "oluchi17", "rachel08", "victor99", "tunde63",
        "kunle28", "bola86", "kayode19", "abigail50", "johnson27", "kenneth44", "samuel37", "ibukun36",
        "miracle30", "lawrence02", "tobi17", "femi20", "bimbo34", "opeyemi78", "richard92", "olamide98",
        "dammy29", "michael88", "micheal04", "stephen09", "jeremiah84", "peter91", "daniel33", "paul99",
        "collins90", "ebun95", "tolulope67", "harry24", "tania76", "david13", "grace57", "james18",
        "emmanuel73", "temidayo12", "lucy44", "benita26", "chris41", "desmond88", "simon35", "israel62",
        "andrew80", "martha10", "rebecca87", "joyce55", "kingsley91", "simon54", "anthony38", "gideon21",
        "kelvin82", "justina49", "hannah79", "dennis66", "nicholas08", "praise70", "angel83", "mirabel16",
        "esther65", "patricia53", "oliver25", "doris18", "sharon33", "ruth46", "tope59", "peter75",
        "juliet39", "bliss92", "precious31", "gloria60", "cynthia15", "desire51", "caroline81", "gabriel06",
        "clinton58", "ella85", "peace99", "flora43", "deborah14", "janet64"
    ]

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=200, help='Number of users to create')

    def generate_strong_password(self):
        while True:
            password = ''.join(random.choices(
                string.ascii_uppercase +
                string.ascii_lowercase +
                string.digits +
                "!@#$%^&*()-_=+", k=16
            ))
            # Make sure it contains at least one from each group
            if (
                any(c.isupper() for c in password)
                and any(c.islower() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "!@#$%^&*()-_=+" for c in password)
            ):
                return password

    def generate_unique_username(self, base):
        base = base.lower()
        username = base
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base}{counter}"
            counter += 1
        return username

    def generate_email(self, username):
        return f"{username}@{random.choice(self.DOMAINS)}"

    def create_coupon(self, user):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return Coupon.objects.create(
            code=code,
            used=True,
            sold=True,
            user=user
        )
        
    def random_username(self):
        name_part = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 8)))
        number_part = str(random.randint(10, 99))
        return name_part + number_part

    @transaction.atomic
    def handle(self, *args, **options):
        count = options['count']
        usernames = self.USERNAME_POOL.copy()
        created_users = []
        user_lookup = {}

        self.stdout.write(self.style.SUCCESS(f"🚀 Creating {count} users..."))

        # Step 1: Create users
        for _ in range(count):
            if usernames:
                base_username = usernames.pop()
            else:
                base_username = self.random_username()

            username = self.generate_unique_username(base_username)
            email = self.generate_email(username)
            password = self.generate_strong_password()

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
            )
            user.date_joined = timezone.now()
            user.save()

            self.create_coupon(user)
            created_users.append(user)
            user_lookup[username] = user

            self.stdout.write(f"✓ {username} created with email {email}")
        # Step 2: Assign referrals
        self.stdout.write(self.style.SUCCESS("🔁 Assigning referrals..."))

        referrers = random.sample(created_users, k=20)  # Pick 20 top referrers
        available_users = set(created_users) - set(referrers)
        referred_ids = set()

        for referrer in referrers:
            max_refs = random.randint(10, 30)
            possible_refs = list(available_users - {referrer})  # can't refer self
            random.shuffle(possible_refs)
            chosen_refs = possible_refs[:max_refs]

            for referred_user in chosen_refs:
                referred_user.referred_by = referrer
                referred_user.save()
                referred_ids.add(referred_user.id)
                available_users.discard(referred_user)  # Don't reuse
            self.stdout.write(f"→ {referrer.username} referred {len(chosen_refs)} users")

        self.stdout.write(self.style.SUCCESS(f"\n✅ {len(created_users)} users created"))
        self.stdout.write(self.style.SUCCESS(f"🏆 20 users assigned as top referrers with 10–30 referrals each."))
