from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import ReferralsDataSerializer
from .serializers import TaskSerializer
from admin_panel.models import Task, Activity

User = get_user_model()

class UserReferralsView(RetrieveAPIView):
    """Returns the referral details of the logged-in user"""
    serializer_class = ReferralsDataSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class TasksView(APIView):
    """Returns task-related data for users to view."""
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        completed_tasks
        available_tasks
        points_earned
        """
        tasks = Task.objects.all()
        activities = Activity.objects.filter(user=request.user)
        completed_tasks = []
        available_tasks = []
        
        for task in tasks:
            activity = activities.filter(task=task).first()
            serializer = TaskSerializer(task)
            points_earned = 0
            if activity:
                completed_tasks.append(serializer.data)
                points_earned += activity.points_earned
            else:
                available_tasks.append(serializer.data)
                
        data = {
            "completed_tasks": completed_tasks,
            "available_tasks": available_tasks,
            "points_earned": 0,
        }
        
        return Response(data, status=status.HTTP_200_OK)

