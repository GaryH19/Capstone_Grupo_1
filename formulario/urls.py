from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
     path('colaboradores/', views.colaboradores, name='colaboradores'), 
    path('base/', views.base, name="base"),
]
