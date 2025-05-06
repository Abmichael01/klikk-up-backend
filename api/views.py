from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model

from api.checkin_service import perform_daily_checkin
from .serializers import RecentActivitiesSerializer, ReferralsDataSerializer
from .serializers import TaskSerializer, StorySerializer
from admin_panel.models import Task, Activity, Story
from django.contrib.auth import logout


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
        points_earned = 0
        
        for task in tasks:
            activity = activities.filter(task=task).first()
            serializer = TaskSerializer(task, context={"request": request})  # Pass context
            if activity:
                completed_tasks.append(serializer.data)
                points_earned += activity.task.reward
            else:
                available_tasks.append(serializer.data)
                
        data = {
            "completed_tasks": completed_tasks,
            "available_tasks": available_tasks,
            "points_earned": points_earned,
        }
        
        return Response(data, status=status.HTTP_200_OK)

class ConfirmTaskView(APIView):
    """Confirm a task completion."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(request.data)
        task_id = request.data.get("id")
        confirmation_code = request.data.get("confirmation_code")
        
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

        activity = Activity.objects.filter(user=request.user, task=task).first()
        if activity:
            return Response({"error": "Task already confirmed"}, status=status.HTTP_400_BAD_REQUEST)
        
        if task.confirmation_code == confirmation_code:
            activity = Activity.objects.create(
                user=request.user,
                activity_type="task",
                task=task,
                reward=task.reward
            )
            activity.save()
            
            return Response({"message": "Task confirmed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid confirmation code"}, status=status.HTTP_400_BAD_REQUEST)



class StoriesView(APIView):
    """Returns story-related data for users to view."""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        stories = Story.objects.all()
        activities = Activity.objects.filter(user=request.user)
        stories_read = []
        new_stories = []
        points_earned = 0
        
        for story in stories:
            activity = activities.filter(story=story).first()
            serializer = StorySerializer(story, context={"request": request})  # Pass context
            if activity:
                stories_read.append(serializer.data)
                points_earned += activity.story.reward
            else:
                new_stories.append(serializer.data)
                
        data = {
            "stories_read": stories_read,
            "new_stories": new_stories,
            "points_earned": points_earned,
        }
        
        return Response(data, status=status.HTTP_200_OK)

class StoryView(RetrieveAPIView):
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated]
    queryset = Story.objects.all()
    lookup_field = 'id'
    
class ConfirmStoryView(APIView):
    """Confirm a task completion."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(request.data["id"])
        task_id = request.data.get("id")
        
        try:
            story = Story.objects.get(id=task_id)
        except Story.DoesNotExist:
            return Response({"error": "Story not found"}, status=status.HTTP_404_NOT_FOUND)

        activity = Activity.objects.filter(user=request.user, story=story).first()
        if activity:
            return Response({"error": "You have read this story"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        activity = Activity.objects.create(
            user=request.user,
            activity_type="story",
            story= story,
            reward = story.reward
        )
        activity.save()
        
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