from rest_framework import generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
import secrets
import string
from rest_framework.permissions import IsAdminUser, AllowAny
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Count, Sum

def generate_coupon_code(length=6):
    characters = string.ascii_uppercase + string.digits  # A-Z and 0-9
    return ''.join(secrets.choice(characters) for _ in range(length))

class CouponView(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    def create(self, request, *args, **kwargs):
        # Generate a unique coupon code
        code = generate_coupon_code()
        while Coupon.objects.filter(code=code).exists():
            code = generate_coupon_code()

        # Create and save the coupon
        coupon = Coupon.objects.create(code=code, sold=True)

        # Serialize and return
        serializer = self.get_serializer(coupon)
        return Response(
            {"data": serializer.data, "message": "Coupon created successfully"},
            status=status.HTTP_201_CREATED
        )
    
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
    
class CourseView(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('category').order_by('-created_at')
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser]
    
class CourseCategoryView(viewsets.ModelViewSet):
    queryset = CourseCategory.objects.all().order_by('-created_at')
    serializer_class = CourseCategorySerializer
    permission_classes = [IsAdminUser]
    
class AnnouncementView(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementAdminSerializer
    permission_classes = [IsAdminUser]
    
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]  # Or use IsAuthenticated() if you want only logged-in users to view
        return [IsAdminUser()]
    
class GiveawayView(viewsets.ModelViewSet):
    """
    Admin viewset for managing giveaways.
    Provides CRUD operations: list, create, retrieve, update, delete
    """
    queryset = Giveaway.objects.all().order_by('-created_at')
    serializer_class = GiveawayAdminSerializer
    permission_classes = [IsAdminUser]

class DashboardAnalyticsView(APIView):
    def get(self, request):
        today = now().date()
        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]

        # === TASKS ===
        total_tasks = Task.objects.count()
        completed_tasks = Activity.objects.filter(task__isnull=False).count()
        task_daily_completed = {
            day.isoformat(): Activity.objects.filter(task__isnull=False, created_at__date=day).count()
            for day in last_7_days
        }
        new_tasks_today = Activity.objects.filter(task__isnull=False, created_at__date=today).count()

        # === STORIES ===
        total_stories = Story.objects.count()
        completed_stories = Activity.objects.filter(story__isnull=False).count()
        story_daily_completed = {
            day.isoformat(): Activity.objects.filter(story__isnull=False, created_at__date=day).count()
            for day in last_7_days
        }
        new_stories_today = Activity.objects.filter(story__isnull=False, created_at__date=today).count()

        # === USERS ===
        total_users = User.objects.count()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        new_users_daily = {
            day.isoformat(): User.objects.filter(date_joined__date=day).count()
            for day in last_7_days
        }

        # === COUPONS ===
        total_coupons = Coupon.objects.count()
        sold_coupons = Coupon.objects.filter(sold=True).count()
        used_coupons = Coupon.objects.filter(used=True).count()
        coupon_sold_daily = {
            day.isoformat(): Coupon.objects.filter(sold=True, created_at__date=day).count()
            for day in last_7_days
        }
        new_coupons_sold_today = Coupon.objects.filter(sold=True, created_at__date=today).count()

        # === ACTIVITY DISTRIBUTION (PIE CHART) ===
        activity_distribution_raw = Activity.objects.values('activity_type').annotate(count=Count('id'))
        activity_distribution = {item['activity_type']: item['count'] for item in activity_distribution_raw}

        # === TOP USERS (BAR CHART) ===
        top_users = User.objects.order_by('-point_balance')[:5].values('username', 'point_balance')

        # === REWARDS ===
        total_rewards = Activity.objects.aggregate(total=Sum('reward'))['total'] or 0
        avg_rewards = round(total_rewards / total_users, 2) if total_users else 0

        return Response({
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "daily_completed": task_daily_completed,
                "new_today": new_tasks_today,
            },
            "stories": {
                "total": total_stories,
                "completed": completed_stories,
                "daily_completed": story_daily_completed,
                "new_today": new_stories_today,
            },
            "users": {
                "total": total_users,
                "new_today": new_users_today,
                "new_users_daily": new_users_daily
            },
            "coupons": {
                "total": total_coupons,
                "sold": sold_coupons,
                "used": used_coupons,
                "daily_sold": coupon_sold_daily,
                "new_today": new_coupons_sold_today,
            },
            "activity_distribution": activity_distribution,
            "top_users": list(top_users),
            "rewards_summary": {
                "total_rewards_given": total_rewards,
                "average_per_user": avg_rewards,
            }
        }) 