from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import TipoUsuario, Documento

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


class RegistroForm(UserCreationForm):
    # ... (Tu código de RegistroForm existente) ...
    rut = forms.CharField(max_length=12)
    tipo_usuario = forms.ChoiceField(
        choices=[('admin', 'Administrador'), ('colaborador', 'Colaborador')]
    )

    class Meta:
        model = TipoUsuario
        fields = ['username', 'email', 'rut', 'tipo_usuario', 'password'] # Ajusté fields para evitar duplicados
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo Electrónico',
            'rut': 'RUT (Identificación)',
            'tipo_usuario': 'Tipo de Usuario',
            'password': 'Contraseña',
        }
# --- Nuevo Formulario para Documentos ---
class DocumentoForm(forms.ModelForm):
    # Sobrescribimos los campos para usar los IDs/nombres del HTML
    titulo = forms.CharField(label='Titulo de Documento', widget=forms.TextInput(attrs={'id': 'document_title', 'placeholder': 'e.g., API Documentation V2'}))
    
    # OJO: Los selects necesitan que los valores coincidan con los del HTML, si no usas un modelo para Projecto.
    proyecto_asociado = forms.ChoiceField(
        label='Asociación a Proyecto',
        choices=[
            ('', 'Seleccione un proyecto'),
            ('1', 'Projecto Alpha'),
            ('2', 'Projecto Beta'),
        ],
        widget=forms.Select(attrs={'id': 'project_select'})
    )
    
    tipo_documento = forms.ChoiceField(
        label='Tipo Documento',
        choices=[
            ('', 'Select a document type'),
            ('doc', 'Documentation'),
            ('guide', 'User Guide'),
        ],
        widget=forms.Select(attrs={'id': 'document_type'})
    )
    
    class Meta:
        model = Documento
        fields = ['titulo', 'proyecto_asociado', 'tipo_documento', 'archivo']

        widgets = {
            # 💡 CLAVE: Este ID debe coincidir con el que busca el JavaScript
            'archivo': forms.FileInput(attrs={'id': 'document_file', 'style': 'display: none;'}),
        }