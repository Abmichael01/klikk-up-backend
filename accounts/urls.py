from django.urls import path
from .views import *


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path('login/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(),),
]