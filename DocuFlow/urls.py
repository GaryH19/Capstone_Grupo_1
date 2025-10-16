
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='root_redirect'),
    path('', include('formulario.urls')),
]

