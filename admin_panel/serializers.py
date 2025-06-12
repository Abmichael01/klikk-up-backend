from rest_framework import serializers

from . models import *
from django.contrib.auth import get_user_model
from accounts.serializers import UserSerializer

User = get_user_model()

import base64
from django.core.files.base import ContentFile

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)

class CouponSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Coupon
        fields = ["id", "code", "used", "sold", "user"]
        
class TaskSerializer(serializers.ModelSerializer):
    banner = Base64ImageField(required=False)
    class Meta:
        model = Task
        fields = ["id", "title", "link", "reward", "confirmation_code", "banner", "estimated_time"]
        
    def create(self, validated_data):
        return super().create(validated_data)

class StorySerializer(serializers.ModelSerializer):
    banner = Base64ImageField(required=False)
    class Meta:
        model = Story
        fields = ["id", "title", "body", "reward", "banner", "estimated_time"]
        
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