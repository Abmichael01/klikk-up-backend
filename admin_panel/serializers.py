from rest_framework import serializers
from . models import *
from django.contrib.auth import get_user_model
from accounts.serializers import UserSerializer
from django.utils import timezone
import base64
from django.core.files.base import ContentFile

User = get_user_model()

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ["id", "code", "used", "sold", "user"]
        
class TaskSerializer(serializers.ModelSerializer):
    banner = Base64ImageField(required=False)
    class Meta:
        model = Task
        fields = ["id", "title", "link", "reward", "confirmation_code", "banner", "estimated_time", "expired"]
        
    def create(self, validated_data):
        return super().create(validated_data)
    
    def validate_banner(self, value):
        if value in [None, '', b'']:
            return None
        return value

class StorySerializer(serializers.ModelSerializer):
    banner = Base64ImageField(required=False)
    class Meta:
        model = Story
        fields = ["id", "title", "body", "reward", "banner", "estimated_time", "expired"]
        
class CourseCategorySerializer(serializers.ModelSerializer):
    courses_count = serializers.SerializerMethodField()
    class Meta:
        model = CourseCategory
        fields = ['id', 'name', 'slug', 'courses_count']
        
    def get_courses_count(self, obj): 
        return Course.objects.filter(category=obj).count()


class CourseSerializer(serializers.ModelSerializer):
    category = CourseCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=CourseCategory.objects.all(),
        write_only=True,
        source='category'
    )

    class Meta:
        model = Course
        fields = ['id', 'title', 'course_url', 'category', 'category_id', 'created_at']
        read_only_fields = ['created_at']
        
class AnnouncementAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'is_active', 'created_at']
        read_only_fields = ['created_at']

class GiveawayAdminSerializer(serializers.ModelSerializer):
    participants_count = serializers.SerializerMethodField()
    winners = serializers.SerializerMethodField()

    class Meta:
        model = Giveaway
        fields = [
            'id', 
            'title', 
            'prize',
            "is_active", 
            'date', 
            'created_at',
            'participants_count',
            'winners'
        ]
        read_only_fields = ['created_at']

    def get_participants_count(self, obj):
        return GiveawayParticipation.objects.filter(giveaway=obj).count()

    def get_winners(self, obj):
        winners = GiveawayParticipation.objects.filter(
            giveaway=obj,
            winner=True
        ).select_related('user')
        return [
            {'username': participation.user.username, 'id': participation.user.id} # type: ignore
            for participation in winners
        ]
        
    

    def validate_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Giveaway date cannot be in the past")
        return value