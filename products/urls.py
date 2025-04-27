from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('variants', views.ProductVariantViewSet)
router.register('colors', views.ProductVariantColorViewSet)
router.register('images', views.ProductImageViewSet)

urlpatterns = [
    path('', include(router.urls)),

]