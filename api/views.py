from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import ReferralsDataSerializer

User = get_user_model()

class UserReferralsView(RetrieveAPIView):
    """Returns the referral details of the logged-in user"""
    serializer_class = ReferralsDataSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user