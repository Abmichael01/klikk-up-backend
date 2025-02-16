from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer, UserSerializer
from rest_framework import generics
from django.conf import settings

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
        


class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        tokens = response.data

        # Get the authenticated user
        user = self.user_lookup(request)
        
        response = Response({
            "user": UserSerializer(user).data,
            "message": "You account has been created successflully, Login to continue"
        }, status=200)

        # Set Access Token in HTTP-only cookie
        response.set_cookie(
            key = settings.SIMPLE_JWT['AUTH_COOKIE'],
            value = tokens['access'],
            httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'], 
            samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        )

        # Set Refresh Token in HTTP-only cookie
        response.set_cookie(
            key = settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            value = tokens['refresh'],
            httponly = settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure = settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'], 
            samesite = settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
        )

        return response

    def user_lookup(self, request):
        username = request.data.get("username") 
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({"error": "Refresh token not found."}, status=400)
        
        # Inject refresh token into request data
        request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)

        # If refresh is successful, set the new access token in cookies
        if 'access' in response.data:
            response.set_cookie(
                key='access_token',
                value=response.data['access'],
                httponly=True,
                secure=False,  # Set to True in production
                samesite='Lax',
            )

        return response



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token not found."}, status=400)
        
        # Logout by invalidating the refresh token
        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
        except Exception as e:
            return Response({"error": "Error invalidating tokens" + str(e)}, status=500)
        
        # Delete cookies
        response = Response({"success": "Logout successful"})
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response