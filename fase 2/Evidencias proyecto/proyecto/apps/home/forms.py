from faulthandler import disable
from pydoc import text
from random import choices

from django import forms
from django.contrib.auth.models import *
from apps.home.models import *

# Esta clase personalizada obliga a cambiar el nombre visual
class AlumnoModelChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        # Imprimimos en consola para verificar que está entrando aquí (mira tu terminal)
        print(f"Procesando usuario: {obj.username} - Nombre: {obj.first_name} {obj.last_name}")
        
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username

class formDOCUMENTO(forms.ModelForm):
    class Meta:
        model = DOCUMENTO
        fields = ('DOC_NOMBRE','DOC_CONTENIDO','TD_NID')

        labels = '__all__' 
        
        widgets = {
            'DOC_NOMBRE': forms.TextInput(attrs={'class': 'form-control','id':'nombre_id'}),
            'TD_NID': forms.Select(attrs={'class': 'form-control js-example-placeholder-multiple', 'placeholder': 'Seleccione Tipo de documento', 'id': 'tipo_id'}),

        }
    
class formEMPRESA(forms.ModelForm):
    class Meta:
        model = EMPRESA
        fields = ('EM_CNOMBRE','EM_RUT', 'COM_NID')

        labels = '__all__' 
        
        widgets = {
            'EM_CNOMBRE': forms.TextInput(attrs={'class': 'form-control','id':'nombre_id'}),
            'EM_RUT': forms.TextInput(attrs={'class': 'form-control','id':'rut_id'}),
            'COM_NID': forms.Select(attrs={'class': 'form-control js-example-placeholder-multiple', 'placeholder': 'Seleccione comuna', 'id': 'comuna_id'}),
        }

class formPROYECTO(forms.ModelForm):
    
    # AQUI EL CAMBIO: Usamos la clase nueva 'AlumnoModelChoiceField'
    alumnos = AlumnoModelChoiceField(
        queryset=User.objects.none(), # Se llena en el __init__
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control js-example-placeholder-multiple', 
            'multiple': 'multiple',
            'data-placeholder': 'Seleccione alumnos para el proyecto'
        }), 
        required=False,
        label="Asignar Alumnos"
    )

    class Meta:
        model = PROYECTO
        fields = ('PRO_CNOMBRE','EMP_NID', 'alumnos')
        labels = '__all__' 
        widgets = {
            'PRO_CNOMBRE': forms.TextInput(attrs={'class': 'form-control','id':'nombre_id'}),
            'EMP_NID': forms.Select(attrs={'class': 'form-control js-example-placeholder-multiple', 'placeholder': 'Seleccione empresa', 'id': 'empresa_id', "data-placeholder":"Seleccione Empresa" }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # Buscamos el grupo y llenamos la lista
            alumno_group = Group.objects.get(name__iexact='alumno')
            self.fields['alumnos'].queryset = alumno_group.user_set.all().order_by('first_name', 'last_name')
        except Group.DoesNotExist:
            print("ADVERTENCIA: El grupo 'Alumno' no existe.")
            self.fields['alumnos'].queryset = User.objects.none()