from django.urls import path
from .views import *


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path('login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view()),
    path("users/<int:id>/update/", UserUpdateView.as_view(), name="user-update"),
    path("users/<int:id>/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("users/account-overview/", AccountOverviewView.as_view(), name="account-overview"),
    path("users/send-otp/", SendOTPView.as_view(), name="account-overview"),
]