from faulthandler import disable
from pydoc import text
from random import choices
from tkinter import Widget
from django import forms
from django.contrib.auth.models import *
from apps.home.models import *

class formDOCUMENTO(forms.ModelForm):
    class Meta:
        model = DOCUMENTO
        fields = ('DOC_NOMBRE','DOC_CONTENIDO')

        labels = '__all__' 
        
        widgets = {
            'DOC_NOMBRE': forms.TextInput(attrs={'class': 'form-control','id':'nombre_id'}),
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
    class Meta:
        model = PROYECTO
        fields = ('PRO_CNOMBRE','EMP_NID')

        labels = '__all__' 
        
        widgets = {
            'PRO_CNOMBRE': forms.TextInput(attrs={'class': 'form-control','id':'nombre_id'}),
            'EMP_NID': forms.Select(attrs={'class': 'form-control js-example-placeholder-multiple', 'placeholder': 'Seleccione empresa', 'id': 'empresa_id', "data-placeholder":"Seleccione Empresa" }),
        }
    
    
