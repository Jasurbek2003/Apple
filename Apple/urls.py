from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    # API endpoints (without language prefix)
    path('api/v1/', include('api.urls')),

    # Django admin (with language prefix)
]

# URLs with language prefix
urlpatterns += i18n_patterns(
    path(_('admin/'), admin.site.urls),
    prefix_default_language=False,
)

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)