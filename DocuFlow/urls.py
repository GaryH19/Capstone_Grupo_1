# DocuFlow/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# ¡Importa la vista de Logout de Django!
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='root_redirect'),
    path('', include('formulario.urls')),

    # --- ¡AÑADE ESTA LÍNEA! ---
    # name='logout' es el nombre que usaremos en el HTML
    path('logout/', LogoutView.as_view(), name='logout'), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)