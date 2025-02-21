from djoser.serializers import UserCreateSerializer as DjoserUserCreateSerializer, UserSerializer as DjoserUserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from admin_panel.models import Coupon

User = get_user_model()

class UserCreateSerializer(DjoserUserCreateSerializer):
    coupon = serializers.CharField(write_only=True, required=True)
    is_admin = serializers.BooleanField(write_only=True, required=False)
    is_staff = serializers.BooleanField(write_only=True, required=False)
    is_superuser = serializers.BooleanField(write_only=True, required=False)

    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = ["id", "email", "username", "password", "coupon", "is_admin", "is_staff", "is_superuser"]

    def validate_coupon(self, value):
        try:
            coupon = Coupon.objects.get(code=value, used=False, sold=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid or already used coupon code")
        return coupon

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
        user = super().create(validated_data)
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

    class Meta(DjoserUserSerializer.Meta):
        model = User
        fields = ["id", "username", "email", "roles", "is_admin", "is_staff", "is_superuser"]

    def get_roles(self, obj):
        roles = []
        if obj.is_admin:
            roles = [1, 2, 3]  # Admin has all roles
        elif obj.is_staff:
            roles = [2, 3]  # Staff has staff and normal user roles
        else:
            roles = [3]  # Normal user role only
        return roles

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.is_admin:
            # Remove admin-specific fields for non-admin users
            ret.pop("is_admin", None)
            ret.pop("is_staff", None)
            ret.pop("is_superuser", None)
        return ret

