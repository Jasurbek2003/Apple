from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

# Create a router for API viewsets
router = DefaultRouter()

urlpatterns = [
    # API root
    path('', views.APIRootView.as_view(), name='api-root'),

    # Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # Language endpoints
    path('languages/', views.LanguagesView.as_view(), name='languages'),
    path('languages/current/', views.CurrentLanguageView.as_view(), name='current-language'),
    path('languages/set/', views.SetLanguageView.as_view(), name='set-language'),

    # Featured and new products
    path('featured-products/', views.featured_products, name='featured-products'),
    path('new-products/', views.new_products, name='new-products'),

    # Include app-specific endpoints
    path('products/', include('products.urls')),
    path('users/', include('users.urls')),
    path('', include('orders.urls')),

    path('search/', views.search, name='search'),
    path('search/autocomplete/', views.search_autocomplete, name='search-autocomplete'),
]