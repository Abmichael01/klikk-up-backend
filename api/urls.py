from django.urls import path
from .views import UserReferralsView, TasksView

urlpatterns = [
    path("users/me/referrals/", UserReferralsView.as_view(), name="user-referrals"),
    path("users/me/tasks/", TasksView.as_view(), name="tasks-data"),
]

