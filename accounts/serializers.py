from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from admin_panel.models import Coupon

User = get_user_model()

class UserCreateSerializer(UserCreateSerializer):
    coupon = serializers.CharField(write_only=True, required=True)

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ["id", "email", "username", "password", "coupon"]

    def validate_coupon(self, value):
        """Validate coupon code before creating the user"""
        try:
            coupon = Coupon.objects.get(code=value, used=False, sold=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used coupon code")

        return coupon  # Store the coupon object for later use

    def create(self, validated_data):
        """Override create to link coupon after user creation"""
        coupon = validated_data.pop("coupon")  # This is already validated
        user = super().create(validated_data)  # Create user

        # Assign coupon to the user
        coupon.user = user
        coupon.used = True
        coupon.save()

        return user


class UserSerializer(UserSerializer):
    roles = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ["id", "username", "email", "roles"]  # Return only needed data

    def get_roles(self, obj):
        roles = []
        if obj.is_admin:
            roles = [1, 2, 3]  # Admin has all roles
        elif obj.is_staff:
            roles = [2, 3]  # Staff has staff and normal user roles
        else:
            roles = [3]  # Normal user role only
        return roles