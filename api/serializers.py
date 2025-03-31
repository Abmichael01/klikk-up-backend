from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count

User = get_user_model()

class ReferralUserSerializer(serializers.ModelSerializer):
    """Serializer for individual referrals."""
    total_referrals = serializers.IntegerField(source="referrals.count", read_only=True)
    class Meta:
        model = User
        fields = ["id", "username", "email", "point_balance", "xp", "total_referrals"]

class ReferralsDataSerializer(serializers.ModelSerializer):
    """Serializer to handle referral data for the authenticated user."""
    total_referrals = serializers.IntegerField(source="referrals.count", read_only=True)
    referrals = ReferralUserSerializer(many=True, read_only=True)
    points_earned = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    ref_code = serializers.SerializerMethodField()
    leaderboard = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = ["total_referrals", "referrals", "points_earned", "rank", "ref_code", "leaderboard"]

    def get_points_earned(self, obj):
        """Calculate points earned from referrals using total_referral_points method."""
        return obj.total_referral_points()
    
    def get_ref_code(self, obj):
        """Generate a referral code for the user."""
        return obj.username

    def get_rank(self, obj):
        """Calculate the user's referral rank."""
        user_referral_count = obj.referrals.count()
        rank = User.objects.annotate(
            referral_count=Count("referrals")
        ).filter(referral_count__gt=user_referral_count).count() + 1
        return rank
    
    def get_leaderboard(self, obj):
        """Return the top 100 users based on referral count."""
        top_users = User.objects.annotate(
            referral_count=Count("referrals")
        ).order_by("-referral_count")[:100]
        
        return ReferralUserSerializer(top_users, many=True).data

    def get_rank(self, obj):
        """Return the leaderboard rank of the logged-in user."""
        user_referral_count = obj.referrals.count()
        rank = User.objects.annotate(
            referral_count=Count("referrals")
        ).filter(referral_count__gt=user_referral_count).count() + 1
        return rank
