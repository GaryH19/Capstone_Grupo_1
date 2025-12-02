from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from .models import (REGION, COMUNA, EMPRESA, TIPO_DOCUMENTO, PROYECTO, 
                     FASE_PROYECTO, FASE_TIPO_DOCUMENTO, DOCUMENTO, 
                     FASE_DOCUMENTO)
# Register your models here.
admin.site.register(REGION)
admin.site.register(COMUNA)
admin.site.register(EMPRESA)
admin.site.register(TIPO_DOCUMENTO)
admin.site.register(PROYECTO)
admin.site.register(FASE_PROYECTO)
admin.site.register(FASE_TIPO_DOCUMENTO)
admin.site.register(DOCUMENTO)
admin.site.register(FASE_DOCUMENTO)


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'ver_grupos', 'is_staff')
    
    list_filter = ('groups', 'is_staff', 'is_active')
    
    actions = [
        'asignar_grupo_alumno', 
        'quitar_grupo_alumno',
        'asignar_grupo_profesor', 
        'quitar_grupo_profesor'
    ]

    def ver_grupos(self, obj):
        grupos = ", ".join([g.name for g in obj.groups.all()])
        return grupos if grupos else "-"
    ver_grupos.short_description = 'Grupos / Roles'

    # ==========================================
    # ACCIONES PARA ALUMNOS
    # ==========================================
    @admin.action(description='Asignar rol "Alumno" a seleccionados')
    def asignar_grupo_alumno(self, request, queryset):
        grupo, _ = Group.objects.get_or_create(name='Alumno')
        for usuario in queryset:
            usuario.groups.add(grupo)
        self.message_user(request, f"Usuarios agregados al grupo 'Alumno' exitosamente.", level='success')

    @admin.action(description='Quitar rol "Alumno" a seleccionados')
    def quitar_grupo_alumno(self, request, queryset):
        grupo, _ = Group.objects.get_or_create(name='Alumno')
        for usuario in queryset:
            usuario.groups.remove(grupo)
        self.message_user(request, f"Usuarios eliminados del grupo 'Alumno'.", level='warning')

    # ==========================================
    # ACCIONES PARA PROFESORES
    # ==========================================
    @admin.action(description='Asignar rol "Profesor" a seleccionados')
    def asignar_grupo_profesor(self, request, queryset):
        grupo, _ = Group.objects.get_or_create(name='Profesor')
        for usuario in queryset:
            usuario.groups.add(grupo)
        self.message_user(request, f"Usuarios agregados al grupo 'Profesor' exitosamente.", level='success')

    @admin.action(description='Quitar rol "Profesor" a seleccionados')
    def quitar_grupo_profesor(self, request, queryset):
        grupo, _ = Group.objects.get_or_create(name='Profesor')
        for usuario in queryset:
            usuario.groups.remove(grupo)
        self.message_user(request, f"Usuarios eliminados del grupo 'Profesor'.", level='warning')

admin.site.register(User, CustomUserAdmin)