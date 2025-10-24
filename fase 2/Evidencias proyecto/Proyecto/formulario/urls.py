from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('registro/', views.registro, name='registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('proyectos/', views.proyectos_lista_crear, name='proyectos_lista_crear'),
    path('proyectos/editar/<int:pk>/', views.proyecto_editar, name='proyecto_editar'),
    path('proyectos/eliminar/<int:pk>/', views.proyecto_eliminar, name='proyecto_eliminar'),
]