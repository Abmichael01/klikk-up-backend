from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from .serializers import UserCreateSerializer, UserSerializer, UserUpdateSerializer
from rest_framework import generics
from django.conf import settings
from django.shortcuts import get_object_or_404

User = get_user_model()



class IsAdminUser(BasePermission):
    """
    Custom permission to only allow admin users to edit user details.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAdminUser]
    lookup_field = "id"  # Update users based on their ID

class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    lookup_field = "id"  # Delete users based on their ID

class RegisterView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer

class CookieTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        tokens = response.data

        user = self.user_lookup(request)

        if not user:
            return Response({"error": "User not found"}, status=400)

        response = Response({
            "user": UserSerializer(user).data,
            "message": "Your account has been created successfully. Login to continue."
        }, status=200)
        
        csrf_token = get_token(request)

        # Set Access Token in HTTP-only cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=tokens['access'],
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE'),
            samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE')
        )

        # Set Refresh Token in HTTP-only cookie
        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
            value=tokens['refresh'],
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE'),
            samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE',)
        )
        

        return response

    def user_lookup(self, request):
        username = request.data.get("username")
        return User.objects.filter(username=username).first()

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
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=response.data['access'],
            httponly=True,
            secure=settings.SIMPLE_JWT.get('AUTH_COOKIE_SECURE'),
            samesite=settings.SIMPLE_JWT.get('AUTH_COOKIE_SAMESITE')
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