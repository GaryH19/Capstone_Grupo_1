from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import TipoUsuario

class RegistroForm(UserCreationForm):
    # Estos campos personalizados NO necesitan el atributo 'label' aquí
    # si usamos el diccionario 'labels' en la clase Meta.
    rut = forms.CharField(max_length=12)
    tipo_usuario = forms.ChoiceField(
        choices=[('admin', 'Administrador'), ('colaborador', 'Colaborador')]
    )

    class Meta:
        model = TipoUsuario
        
        # Usamos password1 y password2 como están en tu lista de campos
        fields = ['username', 'email', 'rut', 'tipo_usuario', 'password1', 'password2']
        
        # Sobreescribir las etiquetas de los campos para traducirlas
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
            'rut': 'RUT (Identificación)',  # Traducción para tu campo personalizado
            'tipo_usuario': 'Tipo de Usuario', # Traducción para tu campo personalizado
            'password1': 'Contraseña',
            'password2': 'Confirmación de Contraseña',
        }
        
        # También puedes usar 'help_texts' si quieres traducir el texto de ayuda
        # help_texts = {
        #     'username': 'Requerido. 150 caracteres o menos.',
        # }
