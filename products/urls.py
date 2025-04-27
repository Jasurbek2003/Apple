from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('categories', views.CategoryViewSet)
router.register('products', views.ProductViewSet)
router.register('product-images', views.ProductImagesViewSet)
router.register('variants', views.ProductVariantViewSet)
router.register('colors', views.ProductVariantColorViewSet)
router.register('variant-images', views.ProductImageViewSet)
router.register('storage-options', views.ProductVariantStorageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/upload/image/', views.tinymce_image_upload, name='api_image_upload'),
]