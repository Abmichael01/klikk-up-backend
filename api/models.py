from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    description = models.CharField(max_length=255)  # e.g., "Completed Tweet Generation"
    xp_reward = models.PositiveIntegerField(default=10)  # XP for the activity
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.description}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.user.add_xp(self.xp_reward)
