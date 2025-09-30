from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import TipoUsuario

class RegistroForm(UserCreationForm):
    rut = forms.CharField(max_length=12)
    tipo_usuario = forms.ChoiceField(choices=[('admin', 'Administrador'), ('colaborador', 'Colaborador')])

    class Meta:
        model = TipoUsuario
    
        fields = ['username', 'email', 'rut', 'tipo_usuario', 'password1', 'password2']