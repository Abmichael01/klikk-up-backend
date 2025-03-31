from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("User must have an email")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        user = self.create_user(username, email, password=password, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255, unique=True)
    point_balance = models.PositiveIntegerField(default=0) 
    xp = models.PositiveIntegerField(default=0)  # Store XP only
    referred_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def reward_referrer(self, points=100):
        """Reward the referrer and user with points."""
        if self.referred_by:
            self.referred_by.point_balance += points
            self.referred_by.save()
        self.point_balance += points
        self.save()

    def total_referral_points(self, points_per_referral=100):
        """Calculate total points from referrals."""
        return self.referrals.count() * points_per_referral

    def calculate_level(self):
        """Calculate level dynamically based on XP."""
        return int((self.xp ** 0.5) // 10 + 1)

    def xp_for_level(self, level):
        """Calculate XP required to reach a given level."""
        return ((level - 1) * 10) ** 2

    def xp_to_next_level(self):
        """Calculate the XP required to reach the next level."""
        next_level = self.calculate_level() + 1  # Fix: Use `calculate_level()` instead of `self.level`
        return self.xp_for_level(next_level) - self.xp

    def add_xp(self, amount):
        """Add XP and save, without storing level."""
        self.xp += amount
        self.save()
