from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer, UserSerializer as DjoserUserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from admin_panel.models import Coupon, Activity, DailyCheckIn
from django.utils import timezone
from django.db.models import Sum, Case, When, F
from _utils import format_time_since
from datetime import timedelta


User = get_user_model()

class UserCreateSerializer(DjoserUserCreateSerializer):
    coupon = serializers.CharField(write_only=True, required=True)
    ref_code = serializers.CharField(write_only=True, required=False)
    is_admin = serializers.BooleanField(write_only=True, required=False)
    is_staff = serializers.BooleanField(write_only=True, required=False)
    is_superuser = serializers.BooleanField(write_only=True, required=False)

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = [
            "id", "email", "username", "password", "coupon", "ref_code",
            "is_admin", "is_staff", "is_superuser", "point_balance", "is_partner"
        ]

    def validate_coupon(self, value):
        try:
            coupon = Coupon.objects.get(code=value, used=False, sold=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used coupon code")
        return coupon

    def validate_ref_code(self, value):
        try:
            return User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or non-existent referral code")

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.is_admin:
            # Prevent setting user type fields if not an admin
            attrs.pop("is_admin", None)
            attrs.pop("is_staff", None)
            attrs.pop("is_superuser", None)
        return attrs

    def create(self, validated_data):
        coupon = validated_data.pop("coupon")
        referrer = validated_data.pop("ref_code", None)

        user = super().create(validated_data)

        # Assign referral if exists
        if referrer:
            user.referred_by = referrer # type: ignore # type: ignore
            user.save()
            user.reward_referrer() # type: ignore

        # Mark coupon as used
        coupon.user = user
        coupon.used = True
        coupon.save()

        return user



class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "is_partner", "email", "is_admin", "is_staff", "is_superuser" ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.is_admin:
            # Prevent setting user type fields if not an admin
            attrs.pop("is_admin", None)
            attrs.pop("is_staff", None)
            attrs.pop("is_superuser", None)
        return attrs

class UserSerializer(DjoserUserSerializer):
    roles = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = [
            "id", 
            "username",
            "email",
            "is_partner",
            "roles", 
            "is_admin", 
            "is_staff", 
            "is_superuser",
        ]
        
    def get_roles(self, obj):
        """Return role IDs based on user type."""
        if obj.is_admin:
            return [1, 2, 3]  # Admin has all roles
        elif obj.is_staff:
            return [2, 3]  # Staff has staff and normal user roles
        return [3]  # Normal user role only

    def to_representation(self, instance):
        """Hide admin fields for non-admin users."""
        ret = super().to_representation(instance)
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.is_admin:
            ret.pop("is_admin", None)
            ret.pop("is_staff", None)
            ret.pop("is_superuser", None)
        return ret

class RecentActivitiesSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    class Meta:
        model = Activity
        fields = ['activity_type', 'reward', 'created_at']
    
    def get_created_at(self, obj):
        """Format the creation time into human-readable format."""
        return format_time_since(obj.created_at)


class AccountOverviewSerializer(serializers.ModelSerializer):
    """Serializer for providing account overview information."""

    current_level = serializers.SerializerMethodField()
    current_level_xp = serializers.SerializerMethodField()
    next_level = serializers.SerializerMethodField()
    next_level_xp = serializers.SerializerMethodField()
    xp_remaining = serializers.SerializerMethodField()
    xp_in_level = serializers.SerializerMethodField()
    percent_xp_in_level = serializers.SerializerMethodField()
    total_referrals = serializers.SerializerMethodField()
    points_earned_today = serializers.SerializerMethodField()
    total_activities_done = serializers.SerializerMethodField()
    recent_activities = serializers.SerializerMethodField()
    checked_in_today = serializers.SerializerMethodField()
    streak = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "username",
            "point_balance",
            "referred_by",
            "xp",
            "current_level",
            "current_level_xp",
            "next_level",
            "next_level_xp",
            "xp_remaining",
            "xp_in_level",
            "percent_xp_in_level",
            "total_referrals",
            "points_earned_today",
            "total_activities_done",
            "recent_activities",
            'checked_in_today',
            'streak',
        ]

    def get_current_level(self, obj):
        """Calculate the user's current level."""
        return obj.calculate_level()

    def get_current_level_xp(self, obj):
        """XP required to reach the current level."""
        return obj.xp_for_level(obj.calculate_level())

    def get_next_level(self, obj):
        """Determine the next level the user is progressing towards."""
        return obj.calculate_level() + 1

    def get_next_level_xp(self, obj):
        """XP required to reach the next level."""
        return obj.xp_for_level(obj.calculate_level() + 1)

    def get_xp_remaining(self, obj):
        """XP remaining to reach the next level."""
        return obj.xp_to_next_level()

    def get_xp_in_level(self, obj):
        """XP earned within the current level."""
        return obj.xp - obj.xp_for_level(obj.calculate_level())

    def get_percent_xp_in_level(self, obj):
        """Percentage of XP completed within the current level."""
        current_level = obj.calculate_level()
        xp_for_current = obj.xp_for_level(current_level)
        xp_for_next = obj.xp_for_level(current_level + 1)
        return round(((obj.xp - xp_for_current) / (xp_for_next - xp_for_current)) * 100, 2)

    def get_total_referrals(self, obj):
        """Total number of referrals made by the user."""
        return User.objects.filter(referred_by=obj).count()
    
    def get_points_earned_today(self, obj):
        today = timezone.now().date()
        points = Activity.objects.filter(user=obj, created_at__date=today).aggregate(
            total_points=Sum(
                Case(
                    When(activity_type='task', then=F('task__reward')),
                    When(activity_type='story', then=F('story__reward')),
                    default=0
                )
            )
        )['total_points'] or 0
        return points

    def get_total_activities_done(self, obj):
        return Activity.objects.filter(
            user=obj,
            activity_type__in=['task', 'story']
        ).count()
    
    def get_recent_activities(self, obj):
        """Return the latest 5 activities using RecentActivitiesSerializer."""
        recent_activities = Activity.objects.filter(user=obj).order_by('-created_at')[:5]
        return RecentActivitiesSerializer(recent_activities, many=True).data
    
    def get_checked_in_today(self, obj):
        today = timezone.now().date()
        return DailyCheckIn.objects.filter(user=obj, date=today).exists()
    
    def get_streak(self, obj):
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        last_checkin = DailyCheckIn.objects.filter(user=obj).order_by('-date').first()
        
        if not last_checkin:
            return 0

        if last_checkin.date == today or last_checkin.date == yesterday:
            return last_checkin.streak_count
        
        return 0  # streak is broken
