from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('addresses', views.AddressViewSet, basename='address')

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]

