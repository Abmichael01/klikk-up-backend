from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.middleware.csrf import get_token
from django.contrib.auth import get_user_model
from .serializers import AccountOverviewSerializer, UserCreateSerializer, UserSerializer, UserUpdateSerializer
from rest_framework import generics, status
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from .otp import generate_otp, store_otp
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from accounts.otp import verify_otp


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
    """Logs out the user by blacklisting their refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Get the refresh token from cookies
            refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
            print(refresh_token)
            if not refresh_token:
                return Response({"error": "Refresh token not found."}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Clear the cookies
            response = Response({"message": "Logged out successfully"}, status=status.HTTP_200_OK)
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
            response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

            return response
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class AccountOverviewView(generics.RetrieveAPIView):
    """
    Retrieve authenticated user's account overview.
    """
    serializer_class = AccountOverviewSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Return the authenticated user."""
        return self.request.user
    
class SendOTPView(APIView):
    def post(self, request):
        email = request.user.email
        otp = generate_otp()
        store_otp(f"otp:{email}", otp)

        subject = 'Your KlikkUp Verification Code'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email

        context = {
            'username': request.user.username,
            'otp': otp,
            'year': timezone.now().year,
        }

        html_content = render_to_string('otp.html', context)

        text_content = f"""
            Hi {request.user.username},

            Your KlikkUp verification code is:

            {otp}

            If you didn’t request this, you can safely ignore this message or contact us at support@klikkup.com.

            – KlikkUp Team
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")

        try:
            msg.send()
            return Response({"detail": "OTP sent successfully."})
        except Exception as e:
            print("Email sending failed:", str(e))
            return Response({"detail": "Failed to send OTP."}, status=500)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('oldPassword')
        new_password = request.data.get('newPassword')
        otp = request.data.get('otp')
        
        
        
        if not otp:
            return Response({"message": "OTP is required to change otp"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not user.check_password(old_password):
            return Response({"detail": "Old password is incorrect."}, status=400)
        
        if not verify_otp( f"otp:{user.email}", otp):
            return Response({"message": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Password changed successfully."})