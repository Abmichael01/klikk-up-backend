from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import ReferralsDataSerializer
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
                task=task
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
        print(request.data)
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
            story= story
        )
        activity.save()
        
        return Response({"message": "The story has been confirmed"}, status=status.HTTP_200_OK)
