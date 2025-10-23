from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import TipoUsuario, Proyecto  # <-- Se importa el modelo

# --- Este es el formulario de Registro ---
class RegistroForm(UserCreationForm):
    class Meta:
        model = TipoUsuario
        fields = ('username', 'first_name', 'last_name', 'email', 'rut', 'tipo_usuario')

# --- ¡NUEVO FORMULARIO PARA CREAR PROYECTOS! ---
# formulario/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import TipoUsuario, Proyecto

# --- FORMULARIO DE PROYECTO (ACTUALIZADO) ---
class ProyectoForm(forms.ModelForm):
    
    colaboradores = forms.ModelMultipleChoiceField(
        queryset=TipoUsuario.objects.none(), 
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'size': '10'}),
        required=False,
        label="Colaboradores"
    )

    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion'] 
        
        # --- ¡AQUÍ ESTÁ LA CORRECCIÓN! ---
        # Añadimos 'nombre' y 'descripcion' a los widgets
        # para asignarles la clase de Bootstrap.
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        # 3. Recibimos el 'admin_user' que nos pasará la vista
        admin_user = kwargs.pop('admin_user', None) 
        
        super().__init__(*args, **kwargs)
        
        # 4. Filtramos el queryset para que solo muestre usuarios
        #    que NO sean el admin que está creando el proyecto
        if admin_user:
            self.fields['colaboradores'].queryset = TipoUsuario.objects.exclude(
                pk=admin_user.pk
            ).order_by('username')
        else:
             self.fields['colaboradores'].queryset = TipoUsuario.objects.all().order_by('username')
        
        # 5. Si estamos editando, marcamos los que ya están
        if self.instance and self.instance.pk:
            self.fields['colaboradores'].initial = self.instance.colaboradores.all()