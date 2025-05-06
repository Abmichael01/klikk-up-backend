from django.urls import path, include
from .views import DailyCheckInView, UserReferralsView, TasksView, ConfirmTaskView, StoriesView, StoryView, ConfirmStoryView, RoadmapView

urlpatterns = [
    path("users/referrals/", UserReferralsView.as_view(), name="user-referrals"),
    path("users/tasks/", TasksView.as_view(), name="tasks-data"),
    path("users/confirm-task/", ConfirmTaskView.as_view(), name="confirm-task"),
    path("users/stories/", StoriesView.as_view(), name="stories-data"),
    path("users/story/<int:id>/", StoryView.as_view(), name="story"),
    path("users/confirm-story/", ConfirmStoryView.as_view(), name="confirm-story"),
    path("roadmap/", RoadmapView.as_view()),
    
    path("", include("wallets.urls")),
    
    path('daily-checkin/', DailyCheckInView.as_view(), name='daily-checkin'),
]

