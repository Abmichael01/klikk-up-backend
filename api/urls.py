from django.urls import path
from .views import UserReferralsView

urlpatterns = [
    path("users/me/referrals/", UserReferralsView.as_view(), name="user-referrals"),
]

