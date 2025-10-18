from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class TipoUsuario(AbstractUser):
    rut = models.CharField(max_length=12, unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=[('admin', 'Administrador'), ('colaborador', 'Colaborador')])

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"


# --- Nuevo Modelo Documento ---
class Documento(models.Model):
    
    # Campo para el archivo real. 'upload_to' define el subdirectorio dentro de MEDIA_ROOT.
    archivo = models.FileField(upload_to='documentos/%Y/%m/%d/')
    titulo = models.CharField(max_length=255)
    
    # Clave foránea al modelo de Usuario personalizado.
    # El usuario logueado será el autor.
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Campo para el proyecto (usamos CharField como en tu HTML)
    proyecto_asociado = models.CharField(max_length=100) # Se llena con el 'project_id' del form
    
    tipo_documento = models.CharField(max_length=50)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # Usamos .first_name y .last_name si están disponibles, sino .username
        nombre_completo = f"{self.autor.first_name} {self.autor.last_name}".strip() or self.autor.username
        return f"{self.titulo} por {nombre_completo}"