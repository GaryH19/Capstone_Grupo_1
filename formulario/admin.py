from django.contrib import admin
# formulario/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import TipoUsuario 


class TipoUsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'tipo_usuario', 'is_staff') 
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('tipo_usuario',)}),
    )


admin.site.register(TipoUsuario, TipoUsuarioAdmin)
