from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer, UserSerializer as DjoserUserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from admin_panel.models import Coupon

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
            "is_admin", "is_staff", "is_superuser", "point_balance"
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
            user.referred_by = referrer
            user.save()
            user.reward_referrer()

        # Mark coupon as used
        coupon.user = user
        coupon.used = True
        coupon.save()

        return user



class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "is_admin", "is_staff", "is_superuser"]
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
    current_level = serializers.SerializerMethodField()
    current_level_xp = serializers.SerializerMethodField()
    xp_in_level = serializers.SerializerMethodField()
    next_level = serializers.SerializerMethodField()
    next_level_xp = serializers.SerializerMethodField()
    xp_remaining = serializers.SerializerMethodField()
    percent_xp_in_level = serializers.SerializerMethodField()
    total_referrals = serializers.SerializerMethodField()

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = [
            "id", 
            "username",
            "email",
            "roles", 
            "is_admin", 
            "is_staff", 
            "is_superuser",
            "point_balance",
            "referred_by",
            "xp",
            "point_balance",
            "current_level",
            "current_level_xp",
            "next_level",
            "next_level_xp",
            "xp_remaining",
            "xp_in_level",
            "percent_xp_in_level",
            "total_referrals",
        ]
        
    def get_current_level(self, obj):
        """Calculate level dynamically."""
        return obj.calculate_level()
    
    def get_current_level_xp(self, obj):
        """Total XP required to reach the next level."""
        return obj.xp_for_level(obj.calculate_level()) 
        
    def get_xp_in_level(self, obj):
        """XP needed to reach the next level."""
        return obj.xp - obj.xp_for_level(obj.calculate_level()) 

    def get_next_level(self, obj):
        """The next level the user is aiming for."""
        return obj.calculate_level() + 1  

    def get_next_level_xp(self, obj):
        """Total XP required to reach the next level."""
        return obj.xp_for_level(obj.calculate_level() + 1)  
     
    def get_xp_remaining(self, obj):
        """XP remaining to reach the next level."""
        return obj.xp_to_next_level()
    
    def get_percent_xp_in_level(self, obj):
        """Percentage of XP in the current level."""
        return round(((obj.xp - obj.xp_for_level(obj.calculate_level()) ) / (obj.xp_for_level(obj.calculate_level() + 1) - obj.xp_for_level(obj.calculate_level()))) * 100, 2) 

    def get_total_referrals(self, obj):
        """Return total referrals."""
        return User.objects.filter(referred_by=obj).count()
    
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
