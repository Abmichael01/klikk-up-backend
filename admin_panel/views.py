from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import secrets
import string
from rest_framework.permissions import IsAdminUser

def generate_coupon_code(length=6):
    characters = string.ascii_uppercase + string.digits  # A-Z and 0-9
    return ''.join(secrets.choice(characters) for _ in range(length))

class CouponView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    def create(self, request, *args, **kwargs):
        amount = request.data.get('amount', 1)

        try:
            amount = int(amount)
        except ValueError:
            return Response({"error": "Invalid amount value"}, status=status.HTTP_400_BAD_REQUEST)

        if amount < 1:
            return Response({"error": "Amount must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)

        created_coupons = []
        for _ in range(amount):
            code = generate_coupon_code()

            # Check if the coupon code already exists
            while Coupon.objects.filter(code=code).exists():
                code = generate_coupon_code()  # Regenerate if it already exists

            # Create the coupon
            coupon = Coupon.objects.create(code=code)
            created_coupons.append(coupon)

        serializer = self.get_serializer(created_coupons, many=True)
        return Response({"data": serializer.data, "message": "Coupons created successfully"}, status=status.HTTP_201_CREATED)
    
class TaskListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    
class TaskUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    
class StoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = StorySerializer
    queryset = Story.objects.all()

class StoryUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = StorySerializer
    queryset = Story.objects.all()
    
    