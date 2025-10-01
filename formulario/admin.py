from django.contrib import admin
# formulario/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import TipoUsuario # Importamos tu modelo de usuario personalizado

# 1. Creamos una clase administrativa personalizada
#    Heredamos de UserAdmin para mantener toda la funcionalidad de Django (cambio de contraseña, etc.)
class TipoUsuarioAdmin(UserAdmin):
    # Definimos qué campos mostrar en la vista de lista del admin
    list_display = ('username', 'email', 'tipo_usuario', 'is_staff') 
    
    # Definimos qué campos mostrar en la vista de edición de un usuario
    # Incluimos los campos estándar de UserAdmin, y añadimos el campo 'tipo_usuario'
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('tipo_usuario',)}),
    )
    
    # Usamos los formularios de Django estándar si no tienes formularios admin personalizados
    # form = RegistroForm # Si tuvieras un formulario específico para el admin

# 2. Registramos tu modelo personalizado en el panel de administración
admin.site.register(TipoUsuario, TipoUsuarioAdmin)

# Nota: Asegúrate de que tu modelo TipoUsuario tiene los campos 'tipo_usuario', 
# 'is_staff' y los campos básicos de autenticación.