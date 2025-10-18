from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import RegistroForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Documento
from .forms import DocumentoForm

@login_required
def admin_dashboard(request):
    return render(request, '/admin_dashboard.html')
@login_required
def colaboradores(request):
    return render(request, 'colaboradores_dashboard.html')
@login_required
def base (request):
    return render(request, 'base.html')

@login_required
def carga_documentos (request):
    return render(request, 'carga_documentos.html')

@login_required
def proyectos (request):
    return render(request, 'proyectos.html')

def formulario (request):    
    return render(request, 'login.html',{
        'form': UserChangeForm,
    })

@login_required
def carga_documentos(request): # Renombrar para no chocar con el URL pattern si es necesario, aunque aquí no pasa
    if request.method == 'POST':
        # Instanciar con POST data y FILES (imprescindible para subir archivos)
        form = DocumentoForm(request.POST, request.FILES) 
        if form.is_valid():
            # 1. NO guardar inmediatamente (commit=False)
            documento = form.save(commit=False) 
            
            # 2. Asignar el AUTOR: Usa el usuario logueado (request.user)
            documento.autor = request.user 
            
            # 3. Guardar el objeto (y el archivo) en la DB
            documento.save() 
            
            # Mensaje de éxito
            messages.success(request, 'El documento ha sido subido correctamente.')
            
            # Redirigir a la misma página para ver el mensaje y limpiar el form
            return redirect('carga_documentos') 
        else:
            # Mensaje de error
            messages.error(request, 'Error al subir el documento. Revisa los datos del formulario.')
    else:
        # Petición GET, inicializar un formulario vacío
        form = DocumentoForm()

    # Obtener el nombre del usuario logueado para mostrarlo en el HTML
    autor_nombre = request.user.get_full_name() or request.user.username
    
    context = {
        'form': form,
        'autor_nombre': autor_nombre,
    }
    return render(request, 'carga_documentos.html', context)


@login_required
def proyectos(request):
    # Obtener todos los documentos subidos para mostrarlos
    documentos_subidos = Documento.objects.all().order_by('-fecha_subida')
    
    context = {
        'documentos_subidos': documentos_subidos
    }
    return render(request, 'proyectos.html', context)









def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            if usuario.tipo_usuario == 'admin':
                return redirect('/admin_dashboard/')
            elif usuario.tipo_usuario == 'colaborador':
            # CAMBIO CLAVE: Usar el nuevo nombre de URL
                return redirect('/colaboradores/') 
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')
