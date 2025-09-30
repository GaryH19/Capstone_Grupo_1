from django.db import models
from django.contrib.auth.models import AbstractUser

class TipoUsuario(AbstractUser):
    rut = models.CharField(max_length=12, unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=[('admin', 'Administrador'), ('colaborador', 'Colaborador')])

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"
