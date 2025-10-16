from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('colaboradores/', views.colaboradores, name='colaboradores'), 
    path('base/', views.base, name="base"),
    path('carga_documentos/', views.carga_documentos, name='carga_documentos'),
    path('proyectos/', views.proyectos, name='proyectos'),
]
