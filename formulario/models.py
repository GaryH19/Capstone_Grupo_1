from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import datetime # ¡Importante!

# --- 1. TU MODELO DE USUARIO (Se queda igual) ---
class TipoUsuario(AbstractUser):
    rut = models.CharField(max_length=12, unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=[('admin', 'Administrador'), ('colaborador', 'Colaborador')])

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"

# --- 2. MODELO PROYECTO (¡Versión actualizada!) ---
class Proyecto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True) # Descripción añadida
    
    # Propietario (Admin)
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="proyectos_creados" # Nombre cambiado para claridad
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    # --- ¡NUEVO CAMPO! (Para los Colaboradores) ---
    colaboradores = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="proyectos_asignados", # Nombre cambiado para claridad
        blank=True
    )

    def __str__(self):
        return self.nombre

    # --- Propiedades de Progreso (Actualizadas) ---
    @property
    def total_documentos_requeridos(self):
        return ItemDocumento.objects.filter(fase__proyecto=self).count()

    @property
    def total_documentos_subidos(self):
        # Ahora cuenta solo los APROBADOS
        return ItemDocumento.objects.filter(
            fase__proyecto=self, 
            estado='aprobado' # ¡CAMBIO IMPORTANTE!
        ).count()

    @property
    def progreso_porcentaje(self):
        total = self.total_documentos_requeridos
        subidos = self.total_documentos_subidos
        if total == 0:
            return 0
        return round((subidos / total) * 100)


# --- 3. MODELO FASE (Se queda igual) ---
class Fase(models.Model):
    nombre = models.CharField(max_length=100)
    proyecto = models.ForeignKey(
        Proyecto, 
        on_delete=models.CASCADE,
        related_name="fases"
    )
    def __str__(self):
        return f"{self.proyecto.nombre} - {self.nombre}"


# --- 4. MODELO ITEMDOCUMENTO (¡Versión actualizada!) ---
class ItemDocumento(models.Model):
    
    # Estados de aprobación
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de Revisión'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    nombre_requerido = models.CharField(max_length=255)
    fase = models.ForeignKey(Fase, on_delete=models.CASCADE, related_name="items")
    
    # Campos del archivo subido
    archivo = models.FileField(upload_to='documentos_colaboradores/%Y/%m/%d/', blank=True, null=True)
    autor_subida = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="documentos_subidos", blank=True, null=True)
    fecha_subida = models.DateTimeField(null=True, blank=True)

    # --- ¡NUEVO CAMPO! (Estado de aprobación) ---
    estado = models.CharField(
        max_length=10, 
        choices=ESTADO_CHOICES, 
        default='pendiente'
    )
    
    # --- ¡NUEVO CAMPO! (Comentario del admin) ---
    comentario_admin = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"Item: {self.nombre_requerido} ({self.estado})"

    @property
    def esta_completo(self):
        # Ahora "completo" significa que fue APROBADO
        return self.estado == 'aprobado'

    def save(self, *args, **kwargs):
        # Actualiza la fecha de subida solo cuando se añade un archivo
        if self.archivo and not self.fecha_subida:
            self.fecha_subida = datetime.now()
        super().save(*args, **kwargs)


# --- 5. ¡NUEVO MODELO! (Documentos Guía) ---
class DocumentoGuia(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to='documentos_guia/%Y/')
    
    # Enlace al proyecto al que pertenece esta guía
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="documentos_guia"
    )
    # Quién lo subió (siempre será un admin)
    subido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Guía: {self.nombre} (Proyecto: {self.proyecto.nombre})"