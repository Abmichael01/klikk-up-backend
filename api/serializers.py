from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Count
from admin_panel.models import *
from django.utils import timezone
from datetime import timedelta
from admin_panel.models import Announcement

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
    percentage_rank = serializers.SerializerMethodField()


    class Meta:
        model = User
        fields = [ 
                  "total_referrals", 
                  "referrals", 
                  "points_earned", 
                  "rank", 
                  "ref_code", 
                  "leaderboard",
                  "percentage_rank",
                ]

    def get_points_earned(self, obj):
        """Calculate points earned from referrals using total_referral_points method."""
        return obj.total_referral_points()
    
    def get_ref_code(self, obj):
        """Generate a referral code for the user."""
        return obj.username

    
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
    
    def get_percentage_rank(self, obj):
        """Calculate the user's percentage rank."""
        total_users = User.objects.count()
        if total_users == 0:
            return 0  # Avoid division by zero
        user_rank = self.get_rank(obj)
        percentage_rank = ((total_users - user_rank + 1) / total_users) * 100
        return round(percentage_rank, 2)

class TaskSerializer(serializers.ModelSerializer):
    completed = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ["id", "title", "link", "reward", "estimated_time", "completed", "banner"]

    def get_completed(self, obj):
        user = self.context['request'].user
        now = timezone.now()

        # Mark as completed if task is more than a day old
        if now - obj.created_at > timedelta(days=1):
            return True

        # Otherwise check if activity exists
        activity = Activity.objects.filter(user=user, task=obj).first()
        return activity is not None

class StorySerializer(serializers.ModelSerializer):
    story_read = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = [
            "id",
            "title",
            "body",
            "reward",
            "estimated_time",
            "story_read",
            "banner",
        ]

    def get_story_read(self, obj):
        user = self.context['request'].user
        now = timezone.now()

        # Mark as read if story is more than a day old
        if now - obj.created_at > timedelta(days=1):
            return True

        # Otherwise check if activity exists
        activity = Activity.objects.filter(user=user, story=obj).first()
        return activity is not None
    
class RecentActivitiesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = ['activity_type', 'reward', 'created_at']

class RoadmapSerializer(serializers.ModelSerializer):
    """Serializer for the roadmap."""
    total_users = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['total_users']
        
    def get_total_users(self, obj):
        return User.objects.count()




class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'created_at']
        read_only_fields = ['created_at']

class GiveawaySerializer(serializers.ModelSerializer):
    participated = serializers.SerializerMethodField()

    class Meta:
        model = Giveaway
        fields = ['id', 'title', 'prize', 'date', 'is_active', 'created_at', 'participated']

    def get_participated(self, obj):
        user = self.context['request'].user
        return GiveawayParticipation.objects.filter(user=user, giveaway=obj).exists()
    

class GiveawayParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GiveawayParticipation
        fields = ['id', 'giveaway', 'entry_date', 'winner']
        read_only_fields = ['id', 'entry_date', 'winner']
        