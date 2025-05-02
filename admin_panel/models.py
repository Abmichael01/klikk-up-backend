import datetime
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
    estimated_time = models.IntegerField(default=1)  # in minutes
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class Story(models.Model):
    title = models.CharField(max_length=225)
    body = models.TextField()
    reward = models.IntegerField()
    estimated_time = models.IntegerField(default=1)  # in minutes
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class Activity(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('task', 'Task'),
        ('story', 'Story'),
        ('checkin', 'Check-in'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=10, choices=ACTIVITY_TYPE_CHOICES)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, null=True, blank=True)
    reward = models.IntegerField(default=0)  # Points earned from the activity
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Override save method to update user fields."""
        # Fixed XP for every activity
        FIXED_XP = 10

        # Add XP to the user
        self.user.add_xp(FIXED_XP)

        # Add points based on the activity type
        if self.activity_type == 'task' and self.task:
            self.user.point_balance += self.points
        elif self.activity_type == 'story' and self.story:
            self.user.point_balance += self.points

        # Save the updated user fields
        self.user.save()

        # Call the original save method
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.task.reward if self.task else self.story.reward} points"
    

class DailyCheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    date = models.DateField(auto_now_add=True)
    streak_count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'date')  # Prevent multiple check-ins per day

    def __str__(self):
        return f"{self.user.username} - {self.date} - Streak: {self.streak_count}"