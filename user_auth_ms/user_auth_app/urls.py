from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LoginViewSet
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


router = DefaultRouter()
user_router = router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('',include(router.urls)),
    path('login',LoginViewSet.as_view(), name='login'),
    path('refresh-token',TokenRefreshView.as_view(), name='refresh-token')
]
