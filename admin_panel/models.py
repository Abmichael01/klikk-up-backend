from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    used = models.BooleanField(default=False)
    sold = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.code
    
class Task(models.Model):
    title = models.CharField(max_length=225)
    link = models.CharField(max_length=225)
    reward = models.IntegerField()
    confirmation_code = models.CharField(max_length=20, blank=True, null=True)

class Story(models.Model):
    title = models.CharField(max_length=225)
    body = models.TextField()
    reward = models.IntegerField()
    