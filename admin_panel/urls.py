from django.urls import path
from .views import *

urlpatterns = [
    path('coupons/', CouponView.as_view(), name='coupon-list-create'),
    path('task/', TaskListCreateView.as_view()),
    path('task/<int:pk>/', TaskUpdateDeleteView.as_view()),
    path('story/', StoryListCreateView.as_view()),
    path('story/<int:pk>/', StoryUpdateDeleteView.as_view()),
    
]
