from rest_framework import serializers

from . models import *
from django.contrib.auth import get_user_model
from accounts.serializers import UserSerializer

User = get_user_model()

class CouponSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Coupon
        fields = ["id", "code", "used", "sold", "user"]
        
class TaskSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Task
        fields = ["id", "title", "link", "reward", "confirmation_code"]
        
    def create(self, validated_data):
        return super().create(validated_data)

class StorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Story
        fields = ["id", "title", "body", "reward"]