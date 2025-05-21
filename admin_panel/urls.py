from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'courses', CourseView, basename='course')
router.register(r'course-categories', CourseCategoryView, basename='course-categories')

urlpatterns = [
    path('coupons/', CouponView.as_view(), name='coupon-list-create'),
    path('task/', TaskListCreateView.as_view()),
    path('task/<int:pk>/', TaskUpdateDeleteView.as_view()),
    path('story/', StoryListCreateView.as_view()),
    path('story/<int:pk>/', StoryUpdateDeleteView.as_view()),
    path("admin/analytics-data/", DashboardAnalyticsView.as_view(), name="dashboard-analytics"),
    
    path('', include(router.urls)),
]
