from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import RegistroForm
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required


@login_required
def admin_dashboard(request):
    return render(request, '/admin_dashboard.html')
@login_required
def colaboradores(request):
    return render(request, 'colaboradores_dashboard.html')
@login_required
def base (request):
    return render(request, 'base.html')

def formulario (request):    
    return render(request, 'login.html',{
        'form': UserChangeForm,
    })

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
