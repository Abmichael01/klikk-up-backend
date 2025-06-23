from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model

from api.checkin_service import perform_daily_checkin
from .serializers import RecentActivitiesSerializer, ReferralsDataSerializer
from .serializers import *
from admin_panel.models import *
from django.contrib.auth import logout
from datetime import timedelta
from django.utils import timezone

from rest_framework.pagination import PageNumberPagination
from admin_panel.models import Course, CourseCategory
from admin_panel.serializers import CourseSerializer, CourseCategorySerializer
from django.db.models import Q

from admin_panel.models import Announcement
from .serializers import AnnouncementSerializer
from rest_framework.exceptions import NotFound


User = get_user_model() 

class UserReferralsView(RetrieveAPIView):
    serializer_class = ReferralsDataSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class TasksView(APIView):
    """Returns task-related data for users to view."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tasks = Task.objects.all()
        activities = Activity.objects.filter(user=request.user)

        completed_tasks = []
        available_tasks = []
        missed_tasks = []
        points_earned = 0

        one_day_ago = timezone.now() - timedelta(days=1)

        for task in tasks:
            has_completed = activities.filter(task=task).exists()
            serializer = TaskSerializer(task, context={"request": request})

            if has_completed:
                completed_tasks.append(serializer.data)
                points_earned += task.reward
            elif task.created_at < one_day_ago:
                missed_tasks.append(serializer.data)
            else:
                available_tasks.append(serializer.data)

        data = {
            "completed_tasks": completed_tasks,
            "available_tasks": available_tasks,
            "missed_tasks": missed_tasks,
            "points_earned": points_earned,
        }

        return Response(data, status=status.HTTP_200_OK)


class ConfirmTaskView(APIView):
    """Confirm a task completion."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        task_id = request.data.get("id")
        confirmation_code = request.data.get("confirmation_code")

        if not task_id or not confirmation_code:
            return Response(
                {"error": "Task ID and confirmation code are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {"error": "Task not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if Activity.objects.filter(user=request.user, task=task).exists():
            return Response(
                {"error": "Task already confirmed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ⛔️ Check if the task is more than a day old
        if timezone.now() - task.created_at > timedelta(days=1):
            return Response(
                {"error": "This task has expired and can no longer be confirmed"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ✅ Proceed to confirm only if confirmation code matches
        if task.confirmation_code != confirmation_code:
            return Response(
                {"error": "Invalid confirmation code"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Activity.objects.create(
            user=request.user,
            activity_type="task",
            task=task,
            reward=task.reward
        )

        return Response(
            {"message": "Task confirmed successfully"},
            status=status.HTTP_200_OK
        )





class StoriesView(APIView):
    """Returns story-related data for users to view."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        stories = Story.objects.all()
        activities = Activity.objects.filter(user=request.user)

        stories_read = []
        new_stories = []
        missed_stories = []
        points_earned = 0

        one_day_ago = timezone.now() - timedelta(days=1)

        for story in stories:
            has_read = activities.filter(story=story).exists()
            serializer = StorySerializer(story, context={"request": request})  # Include context if needed

            if has_read:
                stories_read.append(serializer.data)
                points_earned += story.reward
            elif not has_read and story.created_at < one_day_ago:
                missed_stories.append(serializer.data)
            else:
                new_stories.append(serializer.data)

        data = {
            "stories_read": stories_read,
            "new_stories": new_stories,
            "missed_stories": missed_stories,
            "points_earned": points_earned,
        }

        return Response(data, status=status.HTTP_200_OK)


class StoryView(RetrieveAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]
    queryset = Story.objects.all()
    lookup_field = 'id'
    
class ConfirmStoryView(APIView):
    """Confirm a story completion."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        story_id = request.data.get("id")
        if not story_id:
            return Response({"error": "Story ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            story = Story.objects.get(id=story_id)
        except Story.DoesNotExist:
            return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)

        if Activity.objects.filter(user=request.user, story=story).exists():
            return Response({"error": "You have already read this story"}, status=status.HTTP_400_BAD_REQUEST)

        # ⛔️ Check if story is older than 1 day
        if timezone.now() - story.created_at > timedelta(days=1):
            return Response(
                {"error": "This story has expired and can no longer be confirmed"},
                status=status.HTTP_400_BAD_REQUEST
            )

        Activity.objects.create(
            user=request.user,
            activity_type="story",
            story=story,
            reward=story.reward
        )

        return Response({"message": "The story has been confirmed"}, status=status.HTTP_200_OK)


class DailyCheckInView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = perform_daily_checkin(request.user)
        return Response(result)

class RoadmapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users_count = User.objects.count()
        # Updated roadmap data
        roadmap_data = {
            "roadmap": [
                {"title": "Launch of KLIKK UP", "completed": True},
                {"title": "Load testing", "completed": True},
                {"title": "Marketing", "completed": False},
                {"title": "Social quest", "completed": False},
                {"title": "Stories task", "completed": False},
                {"title": "Daily rewards", "completed": False},
                {"title": "1000 activation", "completed": False},
                {"title": "Referral bonus withdrawal", "completed": False},
                {"title": "100k monthly referral bonus begins", "completed": False},
                {"title": "5000 activation", "completed": False},
                {"title": "Giveaway", "completed": False},
                {"title": "10,000 activation", "completed": False},
                {"title": "YouTube task begins", "completed": False},
                {"title": "50,000 activation", "completed": False},
                {"title": "Giveaway", "completed": False},
                {"title": "100,000 activation", "completed": False},
                {"title": "200,000 activation", "completed": False},
                {"title": "500,000 activation", "completed": False},
                {"title": "End of 100k monthly referral bonus", "completed": False},
                {"title": "500M Naira giveaway", "completed": False},
                {"title": "1,000,000 activation", "completed": False},
                {"title": "Game development", "completed": False},
                {"title": "Integrating backend services", "completed": False},
                {"title": "Launching and promotion", "completed": False},
                {"title": "Project announcement", "completed": False},
                {"title": "End of KLIKK UP quest", "completed": False},
                {"title": "Conversion of points to coins", "completed": False},
                {"title": "Snapshot", "completed": False},
                {"title": "Community activity", "completed": False},
                {"title": "Post-launch scaling", "completed": False},
            ],
            "users_count": users_count,
        }
        return Response(roadmap_data, status=status.HTTP_200_OK)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100


class CoursesView(APIView):
    def get(self, request):
        # Get query params
        category_id = request.query_params.get("category")
        search_query = request.query_params.get("query", "").strip()
        page = request.query_params.get("page", 1)

        # Fetch all categories for dropdown/filter
        categories = CourseCategory.objects.all()
        category_serializer = CourseCategorySerializer(categories, many=True)

        # Start with all courses
        queryset = Course.objects.select_related('category').order_by('-created_at')

        # Filter by category if provided
        if category_id:
            try:
                category_id = int(category_id)
                queryset = queryset.filter(category_id=category_id)
            except (ValueError, TypeError):
                pass  # Invalid category ID — ignore filter

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Paginate results
        paginator = StandardResultsSetPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        # Serialize data
        course_serializer = CourseSerializer(paginated_queryset, many=True)

        # Build final response
        data = {
            "courses": course_serializer.data,
            "categories": category_serializer.data,
            "has_next": paginator.page.has_next(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "total_results": paginator.page.paginator.count,
        }
        
        return Response(data, status=status.HTTP_200_OK)
    
class AnnouncementListView(APIView):
    def get(self, request):
        # Only get active announcements
        announcements = Announcement.objects.filter(is_active=True)
        serializer = AnnouncementSerializer(announcements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ActiveGiveawayDetailView(RetrieveAPIView):
    serializer_class = GiveawaySerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        giveaway = Giveaway.objects.filter(is_active=True).first()

        if not giveaway:
            # Return 200 OK with empty data
            return Response({"none": True }, status=200)

        serializer = self.get_serializer(giveaway)
        return Response(serializer.data, status=200)
    
class ParticipateInGiveawayView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        giveaway = Giveaway.objects.filter(is_active=True).first()

        if not giveaway:
            return Response({"detail": "No active giveaway available."}, status=status.HTTP_404_NOT_FOUND)

        # Check if already participated
        if GiveawayParticipation.objects.filter(user=user, giveaway=giveaway).exists():
            return Response({"detail": "You have already participated in this giveaway."}, status=status.HTTP_400_BAD_REQUEST)

        participation = GiveawayParticipation.objects.create(user=user, giveaway=giveaway)

        serializer = GiveawayParticipationSerializer(participation)
        return Response({"detail": "Successfully entered the giveaway!", "data": serializer.data}, status=status.HTTP_201_CREATED)