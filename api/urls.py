from django.urls import path
from .views import UserReferralsView, TasksView, ConfirmTaskView

urlpatterns = [
    path("users/referrals/", UserReferralsView.as_view(), name="user-referrals"),
    path("users/tasks/", TasksView.as_view(), name="tasks-data"),
    path("users/confirm-task/", ConfirmTaskView.as_view(), name="confirm-task"),
]

