from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group, User
from .forms import LoginForm, SignUpForm
from django.db import IntegrityError

from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.utils.html import strip_tags
from .forms import ForgotPasswordForm
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
    post_data = {}

    if request.method == "POST":
        form = SignUpForm(request.POST)
        
        post_data = {
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'rut': request.POST.get('rut', ''),
            'phone': request.POST.get('phone', '')
        }

        if form.is_valid():
            rut_ingresado = post_data['rut']
            phone_ingresado = post_data['phone']

            if User.objects.filter(rut=rut_ingresado).exists():
                msg = 'Error: Este RUT ya está registrado.'
                return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": False, "data": post_data})
            
            if User.objects.filter(telefono=phone_ingresado).exists():
                msg = 'Error: Este número de teléfono ya está registrado.'
                return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": False, "data": post_data})

            try:
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
                
                post_data = {} 

            except IntegrityError:
                msg = 'Error: Los datos ya existen en el sistema.'
                return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": False, "data": post_data})

        else:
            msg = 'El formulario no es válido (Revisa usuario o contraseñas)'
            return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": False, "data": post_data})
    
    else:
        form = SignUpForm()

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
                user = User.objects.get(username=username)
                
                if not user.email:
                    msg = "Este usuario existe, pero no tiene un correo vinculado."
                else:
                    nueva_clave = get_random_string(length=6, allowed_chars='0123456789')
                    
                    user.set_password(nueva_clave)
                    user.es_clave_temporal = True
                    user.save()

                    asunto = 'Recuperación de Acceso - DocuFlow'

                    html_message = f"""
                    <!DOCTYPE html>
                    <html>
                    <body style="font-family: Arial, sans-serif; background-color: #f4f7fa; padding: 20px; margin: 0;">
                        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; padding: 30px; box-shadow: 0 4px 8px rgba(0,0,0,0.05); border-top: 4px solid #4680ff;">
                            
                            <h2 style="color: #333; text-align: center; margin-top: 0;">DocuFlow</h2>
                            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                            
                            <p style="color: #555; font-size: 16px;">
                                Hola <strong>{user.first_name} {user.last_name}</strong>,
                            </p>
                            
                            <p style="color: #666; line-height: 1.5;">
                                Has solicitado restablecer tu contraseña. Utiliza el siguiente código temporal para ingresar al sistema:
                            </p>

                            <div style="background-color: #f8f9fa; border: 2px dashed #4680ff; border-radius: 6px; text-align: center; padding: 15px; margin: 25px 0;">
                                <span style="display: block; color: #888; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Tu Clave Temporal</span>
                                <span style="display: block; color: #333; font-size: 32px; font-weight: bold; letter-spacing: 5px;">{nueva_clave}</span>
                            </div>

                            <p style="color: #666; font-size: 14px;">
                                <strong>Importante:</strong> Al ingresar, el sistema te pedirá cambiar esta contraseña por una segura.
                            </p>
                            
                            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 12px;">
                                <p>Si no solicitaste este cambio, por favor ignora este mensaje.</p>
                                <p>&copy; 2025 Equipo DocuFlow</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """

                    plain_message = strip_tags(html_message)
                    
                    send_mail(
                        subject=asunto,
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    email_oculto = user.email.replace(user.email.split('@')[0][3:], '****')
                    msg = f"Hemos enviado la clave al correo {email_oculto}"
                    success = True
                    form = ForgotPasswordForm()

            except User.DoesNotExist:
                msg = "El nombre de usuario ingresado no existe."
            except Exception as e:
                print(f"Error SMTP: {e}")
                msg = "Error técnico al enviar el correo. Intente más tarde."

    return render(request, "accounts/forgot_password.html", {"form": form, "msg": msg, "success": success})