from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group, User
from .forms import LoginForm, SignUpForm
from django.db import IntegrityError

from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from .forms import ForgotPasswordForm
from django.core.mail import send_mail
from django.contrib import messages



def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if getattr(user, 'es_clave_temporal', False):
                    messages.warning(request, '⚠️ Estás usando una contraseña temporal. Por seguridad, ve a tu perfil y cámbiala ahora.')
                return redirect("/")
            else:
                msg = 'Usuario o contraseña son invalidas, intente nuevamente.'
        else:
            msg = 'Error al validar el formulario'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False
    
    # 1. PREPARAMOS EL DICCIONARIO PARA GUARDAR LO QUE ESCRIBIÓ EL USUARIO
    # (Si no es POST, estará vacío)
    post_data = {}

    if request.method == "POST":
        form = SignUpForm(request.POST)
        
        # 2. CAPTURAMOS LOS DATOS MANUALES INMEDIATAMENTE
        # Esto asegura que si falla, tengamos los datos para devolverlos
        post_data = {
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'rut': request.POST.get('rut', ''),
            'phone': request.POST.get('phone', '')
        }

        if form.is_valid():
            # Validación manual de duplicados
            rut_ingresado = post_data['rut']
            phone_ingresado = post_data['phone']

            # CASO ERROR: RUT Duplicado
            if User.objects.filter(rut=rut_ingresado).exists():
                msg = 'Error: Este RUT ya está registrado.'
                # IMPORTANTE: Aquí devolvemos "data": post_data para que el HTML lo pinte
                return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": False, "data": post_data})
            
            # CASO ERROR: Teléfono Duplicado
            if User.objects.filter(telefono=phone_ingresado).exists():
                msg = 'Error: Este número de teléfono ya está registrado.'
                return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": False, "data": post_data})

            try:
                # Guardado exitoso
                user = form.save(commit=False)
                
                user.first_name = post_data['first_name']
                user.last_name  = post_data['last_name']
                user.rut        = rut_ingresado
                user.telefono   = phone_ingresado

                user.save()

                try:
                    grupo_alumno = Group.objects.get(name='Alumno')
                    user.groups.add(grupo_alumno)
                except Group.DoesNotExist:
                    pass

                msg = 'Usuario creado con éxito. Por favor <a href="/login">inicia sesión</a>.'
                success = True
                
                # Al ser exitoso, vaciamos post_data para limpiar el formulario
                post_data = {} 

            except IntegrityError:
                msg = 'Error: Los datos ya existen en el sistema.'
                return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": False, "data": post_data})

        else:
            msg = 'El formulario no es válido (Revisa usuario o contraseñas)'
            # Si falla el form de Django, también devolvemos los datos manuales
            return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": False, "data": post_data})
    
    else:
        form = SignUpForm()

    # 3. RENDER FINAL
    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success, "data": post_data})

        ############################
        ### OLVIDO DE CONTRASEÑA ###
        ############################
def forgot_password_view(request):
    form = ForgotPasswordForm(request.POST or None)
    msg = None
    success = False

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            
            try:
                # 1. Buscamos al usuario en la base de datos
                user = User.objects.get(username=username)
                
                # 2. Verificamos que tenga un correo registrado
                if not user.email:
                    msg = "Este usuario existe, pero no tiene un correo vinculado para enviar la clave."
                else:
                    # 3. Generamos una clave temporal de 6 números
                    nueva_clave = get_random_string(length=6, allowed_chars='0123456789')
                    
                    # 4. Actualizamos el usuario
                    user.set_password(nueva_clave)
                    user.es_clave_temporal = True  # Activamos la alerta amarilla
                    user.save()

                    # 5. Preparamos el correo
                    asunto = 'Recuperación de Contraseña - DocuFlow'
                    mensaje = f"""
                    Hola {user.first_name},

                    Has solicitado recuperar tu acceso a DocuFlow.
                    
                    Tu nueva contraseña temporal es: {nueva_clave}

                    1. Ingresa al sistema con esta clave.
                    2. El sistema te pedirá cambiarla por seguridad.
                    
                    Saludos,
                    El equipo de DocuFlow.
                    """
                    
                    # 6. ENVIAMOS EL CORREO REAL
                    send_mail(
                        asunto,
                        mensaje,
                        settings.DEFAULT_FROM_EMAIL, # Remitente (tu correo)
                        [user.email],                # Destinatario (el correo del usuario)
                        fail_silently=False,
                    )

                    # Ocultamos parte del correo por seguridad visual
                    email_oculto = user.email.replace(user.email.split('@')[0][3:], '****')
                    msg = f"Hemos enviado una clave temporal al correo {email_oculto}"
                    success = True
                    form = ForgotPasswordForm() # Limpiamos formulario

            except User.DoesNotExist:
                msg = "El nombre de usuario ingresado no existe."
            except Exception as e:
                # Esto atrapa errores de conexión con Gmail (ej: mala contraseña)
                print(f"Error SMTP: {e}")
                msg = "Hubo un error técnico al enviar el correo. Contacte al administrador."

    return render(request, "accounts/forgot_password.html", {"form": form, "msg": msg, "success": success})