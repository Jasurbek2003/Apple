# api/urls.py - Update with the correct way to document JWT token views

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from . import views

# Define response schemas for token views
token_obtain_response = openapi.Response(
    description="JWT token pair response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT refresh token'),
        }
    )
)

token_refresh_response = openapi.Response(
    description="JWT token refresh response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'access': openapi.Schema(type=openapi.TYPE_STRING, description='New JWT access token'),
        }
    )
)

token_verify_response = openapi.Response(
    description="Token verification response",
    schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={},
        description='Empty response indicates the token is valid'
    )
)

# We need to create class decorators instead of decorating the class directly
# This is the correct approach for built-in Django REST Framework views

@swagger_auto_schema(
    responses={200: token_obtain_response},
    operation_description="Obtain JWT token pair by providing username and password",
    operation_summary="Login",
    tags=['Authentication'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
        }
    )
)
class DecoratedTokenObtainPairView(TokenObtainPairView):
    pass

@swagger_auto_schema(
    responses={200: token_refresh_response},
    operation_description="Refresh JWT access token using refresh token",
    operation_summary="Refresh Token",
    tags=['Authentication'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['refresh'],
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )
)
class DecoratedTokenRefreshView(TokenRefreshView):
    pass

@swagger_auto_schema(
    responses={200: token_verify_response},
    operation_description="Verify JWT token validity",
    operation_summary="Verify Token",
    tags=['Authentication'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING),
        }
    )
)
class DecoratedTokenVerifyView(TokenVerifyView):
    pass

# Create a router for API viewsets
router = DefaultRouter()

urlpatterns = [
    # API root
    # path('', views.APIRootView.as_view(), name='api-root'),

    # Authentication endpoints - use the decorated classes
    path('token/', DecoratedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', DecoratedTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', DecoratedTokenVerifyView.as_view(), name='token_verify'),

    # Rest of your urlpatterns...
    path('languages/', views.LanguagesView.as_view(), name='languages'),
    path('languages/current/', views.CurrentLanguageView.as_view(), name='current-language'),
    path('languages/set/', views.SetLanguageView.as_view(), name='set-language'),

    # Featured and new products
    # path('featured-products/', views.featured_products, name='featured-products'),
    # path('new-products/', views.new_products, name='new-products'),

    # Include app-specific endpoints
    path('products/', include('products.urls')),
    path('users/', include('users.urls')),
    # path('', include('orders.urls')),

    # path('search/', views.search, name='search'),
    # path('search/autocomplete/', views.search_autocomplete, name='search-autocomplete'),
]