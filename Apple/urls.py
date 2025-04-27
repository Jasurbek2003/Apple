from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

from products.views import tinymce_image_upload
from .swagger import swagger_urlpatterns

urlpatterns = [
    # API endpoints (without language prefix)
    path('api/v1/', include('api.urls')),
    path('tinymce/', include('tinymce.urls')),
    *swagger_urlpatterns,

    # Django admin (with language prefix)
]

# URLs with language prefix
urlpatterns += i18n_patterns(
    path(_('admin/'), admin.site.urls),
    path('admin/tinymce/upload/', tinymce_image_upload, name='tinymce_upload_api'),
    prefix_default_language=False,
)

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)