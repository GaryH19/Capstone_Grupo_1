# formulario/views.py
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import RegistroForm, ProyectoForm # ¡Importa el nuevo ProyectoForm!
from django.contrib.auth.decorators import login_required
from .models import Proyecto, Fase, TipoUsuario # ¡Importa Fase y TipoUsuario!
from django.contrib import messages # Para mostrar mensajes de éxito

# --- VISTA DE LOGIN (Se queda igual) ---
def login_view(request):
    # ... (tu código de login_view no cambia) ...
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            print("[DEBUG] Redirigiendo a 'dashboard'...")
            return redirect('dashboard')
        else:
            print("[DEBUG] Autenticación fallida.")
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    return render(request, 'login.html')

# --- VISTA DE REGISTRO (Se queda igual) ---
def registro(request):
    # ... (tu código de registro no cambia) ...
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

# --- VISTA DEL DASHBOARD (Se queda igual) ---
@login_required
def dashboard(request):
    # ... (tu código de dashboard no cambia) ...
    proyectos = [] 
    if request.user.tipo_usuario == 'admin':
        proyectos = request.user.proyectos_creados.all()
    elif request.user.tipo_usuario == 'colaborador':
        proyectos = request.user.proyectos_asignados.all()
    context = {'proyectos_del_usuario': proyectos}
    return render(request, 'dashboard.html', context)

# -----------------------------------------------------------------
# --- ¡NUEVAS VISTAS PARA LA PÁGINA DE "PROYECTOS"! ---
# -----------------------------------------------------------------

@login_required
def proyectos_lista_crear(request):
    """
    Vista para Admins (crear/listar todo) y
    Colaboradores (listar asignados).
    """
    
    # Lógica POST (Solo para Admins)
    if request.method == 'POST' and request.user.tipo_usuario == 'admin':
        # 1. Pasamos 'admin_user' al formulario
        form = ProyectoForm(request.POST, admin_user=request.user) 
        
        if form.is_valid():
            # 2. Extraemos los colaboradores ANTES de guardar
            colaboradores = form.cleaned_data['colaboradores']
            
            # 3. Guardamos el proyecto (commit=False)
            proyecto = form.save(commit=False) 
            proyecto.propietario = request.user
            proyecto.save() # Guardamos el objeto principal

            # 4. ASIGNAMOS los colaboradores (después de guardar)
            proyecto.colaboradores.set(colaboradores) 
            
            messages.success(request, f"¡Proyecto '{proyecto.nombre}' creado!")
            return redirect('proyectos_lista_crear')
    else:
        form = ProyectoForm(admin_user=request.user) if request.user.tipo_usuario == 'admin' else None

    if request.user.tipo_usuario == 'admin':
        proyectos_lista = Proyecto.objects.all().order_by('-fecha_creacion')
    else:
        proyectos_lista = request.user.proyectos_asignados.all().order_by('-fecha_creacion')
    
    context = {
        'form': form,
        'proyectos_lista': proyectos_lista
    }
    return render(request, 'proyectos.html', context)


@login_required
def proyecto_editar(request, pk):
    """
    Esta vista permite a un admin editar un proyecto existente
    (ej: cambiar el nombre o añadir/quitar colaboradores).
    """
    # Seguridad: Solo admins
    if request.user.tipo_usuario != 'admin':
        messages.error(request, 'No tienes permiso.')
        return redirect('dashboard')

    # Buscamos el proyecto por su ID (pk) o mostramos un error 404
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    # Creamos un formulario, pero esta vez lo "llenamos" con 
    # los datos del proyecto que estamos editando (instance=proyecto)
    form = ProyectoForm(request.POST or None, instance=proyecto)

    # Ocultamos el campo 'cantidad_de_fases' porque NO queremos
    # añadir más fases al editar. La edición de fases será en otra vista.
    form.fields['cantidad_de_fases'].widget = forms.HiddenInput()
    form.fields['cantidad_de_fases'].required = False

    if request.method == 'POST' and form.is_valid():
        form.save() # Guardamos los cambios (nombre, descripción, colaboradores)
        messages.success(request, f"¡Proyecto '{proyecto.nombre}' actualizado!")
        return redirect('proyectos_lista_crear') # Volvemos a la lista

    context = {
        'form': form,
        'proyecto': proyecto
    }
    return render(request, 'proyecto_editar.html', context)

@login_required
def proyecto_eliminar(request, pk):
    """
    Procesa la eliminación de un proyecto.
    Solo acepta POST para seguridad.
    """
    
    # 1. Seguridad: Solo admins
    if request.user.tipo_usuario != 'admin':
        messages.error(request, 'No tienes permiso para realizar esta acción.')
        return redirect('dashboard')
    
    # 2. Busca el proyecto
    proyecto = get_object_or_404(Proyecto, pk=pk)
    
    # 3. Solo procesa si es POST
    if request.method == 'POST':
        # 4. Seguridad Extra: Solo el propietario puede borrar
        if proyecto.propietario == request.user or request.user.is_superuser:
            nombre_proyecto = proyecto.nombre
            proyecto.delete()
            messages.success(request, f"El proyecto '{nombre_proyecto}' ha sido eliminado.")
        else:
            messages.error(request, 'No puedes eliminar un proyecto que no te pertenece.')
        
        return redirect('proyectos_lista_crear')
    
    # Si alguien intenta ir por GET, simplemente lo regresamos
    return redirect('proyectos_lista_crear')