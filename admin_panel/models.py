import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from cloudinary_storage.storage import MediaCloudinaryStorage


User = get_user_model()

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    used = models.BooleanField(default=False)
    sold = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.code  
    
class Task(models.Model):
    title = models.CharField(max_length=225)
    link = models.CharField(max_length=225)
    reward = models.IntegerField()
    confirmation_code = models.CharField(max_length=20, blank=True, null=True)
    estimated_time = models.FloatField(default=1)  # in minutes
    no_wait_confirm = models.BooleanField(default=False, help_text="If True, task can be confirmed without waiting for timer")
    no_code_required = models.BooleanField(default=False, help_text="If True, task doesn't require confirmation code")
    banner = models.ImageField(
        upload_to='task_banners/',
        storage=MediaCloudinaryStorage(),
        blank=True,
        null=True
    )
    expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class Story(models.Model):
    title = models.CharField(max_length=225)
    body = models.TextField()
    reward = models.IntegerField()
    estimated_time = models.FloatField(default=1)  # in minutes
    banner = models.ImageField(
        upload_to='story_banners/',
        storage=MediaCloudinaryStorage(),
        blank=True,
        null=True
    )
    expired = models.BooleanField(default=False)
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

        self.user.add_xp(FIXED_XP) # type: ignore

        self.user.point_balance += self.reward # type: ignore
       
        self.user.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.task.reward if self.task else self.story.reward} points" # type: ignore
    

class DailyCheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    date = models.DateField(auto_now_add=True)
    streak_count = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'date')  # Prevent multiple check-ins per day

    def __str__(self):
        return f"{self.user.username} - {self.date} - Streak: {self.streak_count}"
    
class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, related_name='courses')
    course_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# The code defines two models, `Giveaway` and `GiveawayParticipation`, for managing giveaways and user
# participation in Django.
class Giveaway(models.Model):
    title = models.CharField(max_length=255)
    prize = models.CharField(max_length=255)
    date = models.DateTimeField()
    is_active = models.BooleanField(default=False, help_text="Toggle to activate/deactivate this giveaway")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.is_active:
            Giveaway.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class GiveawayParticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    giveaway = models.ForeignKey(Giveaway, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(auto_now_add=True)
    winner = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'giveaway')

    def __str__(self):
        return f"{self.user.username} - {self.giveaway.title}"

class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
