import json
from django import template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render, resolve_url)
from .models import *
from .forms import *
from django.contrib import messages
from functools import wraps

import mimetypes
from django.http import FileResponse, Http404

import os
from django.utils.text import slugify

from django.utils.encoding import escape_uri_path
from .models import DOCUMENTO

# --- FUNCIÓN DE SEGURIDAD ---
def group_required(*group_names):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/login/')
            if request.user.is_superuser or request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
            messages.error(request, 'No tienes permisos de Profesor para realizar esta acción.')
            return redirect('pro_listall')
        return _wrapped_view
    return decorator

@login_required(login_url="/login/")
def index(request):
    try:
        listado_proyectos = []
        proyectos = PROYECTO.objects.none() 
        
        # Obtenemos los roles
        is_profesor = request.user.groups.filter(name__iexact='profesor').exists() or request.user.is_superuser
        is_alumno = request.user.groups.filter(name__iexact='alumno').exists()

        # Filtramos proyectos según el rol
        if is_profesor:
            proyectos = PROYECTO.objects.filter(profesor=request.user)
        elif is_alumno:
            proyectos = PROYECTO.objects.filter(alumnos=request.user)
        
        proyectos = proyectos.filter(PRO_ESTADO=True).order_by('-PRO_FFECHACREACION')

        for pro in proyectos:
            fases_proyecto = FASE_PROYECTO.objects.filter(PRO_NID=pro)
            total_listo_x_fase = 0
            
            if fases_proyecto.exists():
                total_progreso_fases = 0
                for fase in fases_proyecto:
                    documentos_solicitado_fase = FASE_TIPO_DOCUMENTO.objects.filter(FA_NID=fase)
                    cant_doc_solicitados = documentos_solicitado_fase.count()
                    
                    if cant_doc_solicitados > 0:
                        documentos_aprobados = FASE_DOCUMENTO.objects.filter(
                            FA_NID=fase, 
                            DOC_NID__DOC_APROBADO=True
                        ).count()
                        # Sumamos el % de esta fase
                        total_progreso_fases += (documentos_aprobados / cant_doc_solicitados) * 100
                
                # Promedio de todas las fases
                total_listo_x_fase = total_progreso_fases / fases_proyecto.count()

            # Añadimos a la lista: [ID, Nombre, Empresa, Fecha, Progreso]
            listado_proyectos.append([
                pro.PRO_NID, 
                pro.PRO_CNOMBRE, 
                pro.EMP_NID.EM_CNOMBRE, 
                pro.PRO_FFECHACREACION, 
                int(total_listo_x_fase)
            ])

        # Creamos el contexto
        context = {
            'segment': 'index', # Para que el menú se marque como "home"
            'proyectos': listado_proyectos,
            'is_profesor': is_profesor,
            'total_proyectos': len(listado_proyectos) # Un extra para un contador
        }
        
        html_template = loader.get_template('gradient/index.html')
        return HttpResponse(html_template.render(context, request))

    except Exception as e:
        # Si algo falla, carga la página de index simple
        print(f"Error cargando dashboard index: {e}")
        context = {'segment': 'index'}
        html_template = loader.get_template('gradient/index.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        html_template = loader.get_template('gradient/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('gradient/page-404.html')
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template('gradient/page-500.html')
        return HttpResponse(html_template.render(context, request))

#################################
########### USUARIOS ############
#################################
@login_required(login_url="/login/")
@group_required('Profesor') 
def user_listall(request):
    try:
        if request.user.is_superuser:
            usuarios = User.objects.all().order_by('id')
        else:
            usuarios = User.objects.filter(groups__name='Alumno').order_by('id')

        context = {
            'usuarios': usuarios,
            'is_superuser': request.user.is_superuser
        }
        return render(request, 'capstone/usuario/us_listall.html', context)
    except Exception as e:
        print(f"Error detallado: {e}")
        messages.error(request,'Error al cargar listado de usuarios')
        return redirect('/')

@login_required(login_url="/login/")
@group_required('Profesor')
def create_user(request):
    try:
        perfiles = Group.objects.all() if request.user.is_superuser else None

        if request.method == "POST":
            username = request.POST.get('username')
            nombre = request.POST.get('nombre')
            apellidos = request.POST.get('apellidos')
            email = request.POST.get('correo')
            rut = request.POST.get('rut')
            telefono = request.POST.get('telefono')
            password = request.POST.get('contraseña')
            
            perfil_id = request.POST.get('perfil') if request.user.is_superuser else None

            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya existe.')
            else:
                user = User.objects.create(
                    username=username,
                    first_name=nombre,
                    last_name=apellidos,
                    email=email,
                    password=make_password(password),
                    rut=rut,
                    telefono=telefono,
                    is_active=True
                )
                
                if request.user.is_superuser:
                    if perfil_id:
                        grupo = Group.objects.get(id=perfil_id)
                        user.groups.add(grupo)
                else:
                    try:
                        grupo_alumno = Group.objects.get(name='Alumno')
                        user.groups.add(grupo_alumno)
                    except Group.DoesNotExist:
                        pass

                messages.success(request, 'Usuario creado correctamente.')
                return redirect('user_listall')

            context = {'perfiles': perfiles}
            return render(request, 'capstone/usuario/us_addone.html', context)
            
        else:
            context = {'perfiles': perfiles}
            return render(request, 'capstone/usuario/us_addone.html', context)
            
    except Exception as e:
        print(f"Error creando usuario: {e}")
        messages.error(request, f'Error al cargar formulario: {e}')
        return redirect('user_listall')
    
            
# --- Función para ELIMINAR USUARIO (Solo Superuser) ---
@login_required(login_url="/login/")
def delete_user(request, user_id):
    try:
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para eliminar usuarios.')
            return redirect('user_listall')

        user_to_delete = get_object_or_404(User, pk=user_id)
        
        if user_to_delete == request.user:
            messages.error(request, 'No puedes eliminar tu propio usuario.')
            return redirect('user_listall')

        user_to_delete.delete()
        messages.success(request, 'Usuario eliminado correctamente.')
        return redirect('user_listall')

    except Exception as e:
        print(f"Error eliminando usuario: {e}")
        messages.error(request, 'Error al eliminar el usuario.')
        return redirect('user_listall')
    
#############################
######### EMPRESA ###########
#############################
@login_required(login_url="/login/")
def emp_listall(request):
    try:
        emps = EMPRESA.objects.all()
        context = { 'emps': emps }
        return render(request,'capstone/empresa/emp_listall.html',context)
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar listado')
        return redirect('/')

@login_required(login_url="/login/")
def create_emp(request):
    try:
        if request.method == "POST":
            form = formEMPRESA(request.POST)
            if form.is_valid():
                form.save()
            messages.success(request,'Empresa agregada correctamente')
            return redirect('emp_listall')
        else:
            form = formEMPRESA()
            context = { 'form':form }
            return render(request,'capstone/empresa/emp_addone.html',context)
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        redirect('emp_listall')

@login_required(login_url="/login/")
def emp_update(request,EMP_NID):
    try:
        emp = EMPRESA.objects.get(EMP_NID = EMP_NID)
        if request.method == "POST":
            form = formEMPRESA(request.POST,  instance=emp)
            if form.is_valid():
                form.save()
                messages.success(request,'Empresa actualizada correctamente')
            else:
                messages.error(request, 'Error al actualizar empresa')
            return redirect('emp_listall')
        else:
            form = formEMPRESA(instance=emp)
            context = { 'form':form }
            return render(request,'capstone/empresa/emp_addone.html',context)
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        redirect('/')

@login_required(login_url="/login/")
def emp_deactivate(request,EMP_NID):
    try:
        emp =  EMPRESA.objects.get(EMP_NID = EMP_NID)
        emp.EMP_ESTADO = not emp.EMP_ESTADO
        emp.save()
        messages.success(request,'Estado de la empresa cambiado correctamente.')
        return redirect('emp_listall')
    except Exception as e:
        print(e)
        messages.error(request,'Error al cambiar estado de empresa')
        return redirect('emp_listall')
    
@login_required(login_url="/login/")
def emp_delete(request, EMP_NID):
    try:
        # 1. Seguridad: Solo Superuser
        if not request.user.is_superuser:
            messages.error(request, 'No tienes permisos para eliminar empresas.')
            return redirect('emp_listall')

        # 2. Buscar y borrar
        empresa = get_object_or_404(EMPRESA, EMP_NID=EMP_NID)
        empresa.delete()
        
        messages.success(request, 'Empresa eliminada correctamente.')
        return redirect('emp_listall')

    except Exception as e:
        print(f"Error eliminando empresa: {e}")
        messages.error(request, 'Error al eliminar la empresa (puede tener proyectos asociados).')
        return redirect('emp_listall')
    
#################################
###### TIPOS DE DOCUMENTOS ######
#################################
@login_required(login_url="/login/")
def tipodoc_listall(request):
    try:
        tipos = TIPO_DOCUMENTO.objects.all()
        context = { 'tipos': tipos }
        return render(request,'capstone/tipos_documentos/tipodoc_listall.html',context)
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar listado')
        return redirect('/')
    
@login_required(login_url="/login/")
def create_tipo_doc(request):
    try:
        if request.method == "POST":
            nombre = request.POST.get('nombre')
            TIPO_DOCUMENTO.objects.create(TD_NOMBRE = nombre)
            messages.success(request,'Tipo de documento agregado correctamente')
            return redirect('tipodoc_listall')
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        return redirect('tipodoc_listall')

@login_required(login_url="/login/")
def tipodoc_update(request,TD_NID):
    try:
        tipo = TIPO_DOCUMENTO.objects.get(TD_NID = TD_NID)
        if request.method == "POST":
            try:
                nombre = request.POST.get('nombre')
                tipo.TD_NOMBRE = nombre
                tipo.save()
                messages.success(request,'Tipo de documento actualizado correctamente.')
            except Exception as e:
                messages.error(request, 'Error al actualizar tipo de documento.')
            return redirect('tipodoc_listall')
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario.')
        return redirect('/')

@login_required(login_url="/login/")
def tipodoc_deactivate(request,TD_NID):
    try:
        tipo = TIPO_DOCUMENTO.objects.get(TD_NID = TD_NID)
        tipo.TD_ESTADO = not tipo.TD_ESTADO
        tipo.save()
        messages.success(request,'Estado cambiado correctamente.')
        return redirect('tipodoc_listall')
    except Exception as e:
        print(e)
        messages.error(request,'Error al cambiar estado')
        return redirect('tipodoc_listall')

@login_required(login_url="/login/")
def tipodoc_delete(request, TD_NID):
    try:
        # Buscamos el objeto
        tipo_doc = get_object_or_404(TIPO_DOCUMENTO, TD_NID=TD_NID)
        
        # Intentamos eliminar
        tipo_doc.delete()
        messages.success(request, 'Tipo de documento eliminado correctamente.')
        
    except Exception as e:
        # Esto captura errores si el tipo de documento está en uso (Foreign Keys)
        print(f"Error eliminando tipo doc: {e}")
        messages.error(request, 'No se puede eliminar: Este tipo de documento está en uso en algún proyecto.')
        
    return redirect('tipodoc_listall')

############################
######## PROYECTO ##########
############################
@login_required(login_url="/login/")
def pro_listall(request):
    try:
        listado_proyectos = []
        proyectos = PROYECTO.objects.none()
        
        if request.user.is_superuser:
            proyectos = PROYECTO.objects.all()
        elif request.user.groups.filter(name__iexact='profesor').exists(): 
            proyectos = PROYECTO.objects.filter(profesor=request.user)
        elif request.user.groups.filter(name__iexact='alumno').exists(): 
            proyectos = PROYECTO.objects.filter(alumnos=request.user)
        
        proyectos = proyectos.order_by('-PRO_FFECHACREACION')

        for pro in proyectos:
            fases_proyecto = FASE_PROYECTO.objects.filter(PRO_NID=pro)
            total_listo_x_fase = 0
            if fases_proyecto.exists():
                total_progreso_fases = 0
                for fase in fases_proyecto:
                    documentos_solicitado_fase = FASE_TIPO_DOCUMENTO.objects.filter(FA_NID=fase)
                    cant_doc_solicitados = documentos_solicitado_fase.count()
                    
                    if cant_doc_solicitados > 0:
                        documentos_aprobados = FASE_DOCUMENTO.objects.filter(
                            FA_NID=fase, 
                            DOC_NID__DOC_APROBADO=True
                        ).count()
                        total_progreso_fases += (documentos_aprobados / cant_doc_solicitados) * 100
                
                total_listo_x_fase = total_progreso_fases / fases_proyecto.count()

            listado_proyectos.append([pro.PRO_NID, pro.PRO_CNOMBRE, pro.EMP_NID.EM_CNOMBRE, pro.PRO_FFECHACREACION, int(total_listo_x_fase)])

        context = {
            'proyectos': listado_proyectos,
            'is_profesor': request.user.groups.filter(name__iexact='profesor').exists() or request.user.is_superuser
        }
        return render(request,'capstone/proyecto/pro_listall.html',context)
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar listado')
        return redirect('/')

@group_required('Profesor')
def create_pro(request):
    try:
        if request.method == "POST":
            form = formPROYECTO(request.POST)
            if form.is_valid():
                # 1. Guardar Proyecto
                proyecto = form.save(commit=False)
                proyecto.profesor = request.user 
                proyecto.save()
                form.save_m2m() # Alumnos

                # 2. Crear Fases (Lógica Original de Creación)
                cant_fases = int(request.POST.get('cant_fases', 0))
                
                for i in range(1, cant_fases + 1):
                    nombre = request.POST.get(f'nombre_fase_{i}')
                    desc = request.POST.get(f'descripcion_fase_{i}')
                    inicio = request.POST.get(f'fecha_inicio_fase_{i}')
                    termino = request.POST.get(f'fecha_termino_fase_{i}')
                    docs = request.POST.getlist(f'documentos_fase_{i}[]')

                    if nombre and inicio and termino:
                        fase = FASE_PROYECTO.objects.create(
                            FA_CNOMBRE=nombre,
                            FA_NNUMERO_FASE=i,
                            FA_CDESCRICPCION=desc,
                            PRO_FFECHAINCIO=inicio,
                            PRO_FFECHATERMINO=termino,
                            PRO_NID=proyecto
                        )
                        for doc_id in docs:
                            FASE_TIPO_DOCUMENTO.objects.create(
                                FA_NID=fase,
                                TD_NID_id=int(doc_id)
                            )
                
                messages.success(request, 'Proyecto creado correctamente')
                return redirect('pro_listall')
        
        # GET: Mostrar formulario vacío
        form = formPROYECTO()
        documentos = TIPO_DOCUMENTO.objects.all()
        context = { 'form': form, 'documentos': documentos }
        return render(request, 'capstone/proyecto/pro_addone.html', context)

    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        return redirect('/')

@group_required('Profesor')
def pro_update(request, PRO_NID):
    try:
        pro = get_object_or_404(PROYECTO, PRO_NID=PRO_NID)
        
        if pro.profesor != request.user and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso.')
            return redirect('pro_listall')

        if request.method == "POST":
            # 1. Guardar datos del Proyecto
            form = formPROYECTO(request.POST, instance=pro)
            if form.is_valid():
                form.save()
            
            # 2. Procesar Eliminaciones (Fases marcadas para borrar)
            ids_a_borrar = request.POST.get('ids_fases_a_borrar', '')
            if ids_a_borrar:
                lista_ids = ids_a_borrar.split(',')
                FASE_PROYECTO.objects.filter(FA_NID__in=lista_ids, PRO_NID=pro).delete()

            # 3. Procesar Fases (Aquí está la magia: Editar + Crear)
            # Obtenemos el número total de bloques que hay en el HTML
            try:
                total_indices = int(request.POST.get('total_indices_js', 0))
            except ValueError:
                total_indices = 0

            contador_orden = 1 

            # Recorremos desde el 1 hasta el último índice que generó el JS
            for i in range(1, total_indices + 1):
                prefix = f'fase_{i}'
                
                # Verificamos si el campo "nombre" de esa fase existe en el POST
                # (Si no existe, es porque el usuario eliminó ese bloque visualmente o saltó el índice)
                nombre_key = f'nombre_fase_{i}'
                
                if nombre_key in request.POST:
                    # Datos del formulario
                    fase_id = request.POST.get(f'fase_id_{i}') # ID oculto (Solo las viejas lo tienen)
                    nombre = request.POST.get(f'nombre_fase_{i}')
                    desc = request.POST.get(f'descripcion_fase_{i}')
                    inicio = request.POST.get(f'fecha_inicio_fase_{i}')
                    termino = request.POST.get(f'fecha_termino_fase_{i}')
                    docs_ids = request.POST.getlist(f'documentos_fase_{i}[]')

                    if nombre and inicio and termino:
                        fase_obj = None
                        
                        if fase_id:
                            # --- CASO A: TIENE ID -> EDITAR FASE EXISTENTE ---
                            try:
                                fase_obj = FASE_PROYECTO.objects.get(FA_NID=fase_id, PRO_NID=pro)
                                fase_obj.FA_CNOMBRE = nombre
                                fase_obj.FA_CDESCRICPCION = desc
                                fase_obj.PRO_FFECHAINCIO = inicio
                                fase_obj.PRO_FFECHATERMINO = termino
                                fase_obj.FA_NNUMERO_FASE = contador_orden 
                                fase_obj.save()
                            except FASE_PROYECTO.DoesNotExist:
                                continue
                        else:
                            # --- CASO B: NO TIENE ID -> CREAR FASE NUEVA ---
                            fase_obj = FASE_PROYECTO.objects.create(
                                FA_CNOMBRE=nombre,
                                FA_NNUMERO_FASE=contador_orden,
                                FA_CDESCRICPCION=desc,
                                PRO_FFECHAINCIO=inicio,
                                PRO_FFECHATERMINO=termino,
                                PRO_NID=pro
                            )
                        
                        # --- ACTUALIZAR DOCUMENTOS ---
                        if fase_obj:
                            FASE_TIPO_DOCUMENTO.objects.filter(FA_NID=fase_obj).delete()
                            for doc_id in docs_ids:
                                FASE_TIPO_DOCUMENTO.objects.create(
                                    FA_NID=fase_obj, 
                                    TD_NID_id=int(doc_id)
                                )
                        
                        contador_orden += 1

            messages.success(request, 'Proyecto actualizado correctamente.')
            return redirect('pro_listall')

        else:
            # GET: Cargar datos
            form = formPROYECTO(instance=pro)
            documentos = TIPO_DOCUMENTO.objects.all()
            
            fases_existentes = []
            fases_db = FASE_PROYECTO.objects.filter(PRO_NID=pro).order_by('FA_NNUMERO_FASE')
            
            for f in fases_db:
                docs_asignados = FASE_TIPO_DOCUMENTO.objects.filter(FA_NID=f).values_list('TD_NID', flat=True)
                fases_existentes.append({
                    'obj': f,
                    'docs_ids': list(docs_asignados)
                })

            # IMPORTANTE: Enviamos el 'ultimo_indice' para que el JS sepa dónde continuar
            context = {
                'form': form,
                'documentos': documentos,
                'fases_existentes': fases_existentes,
                'ultimo_indice': fases_db.count() 
            }
            return render(request, 'capstone/proyecto/pro_addone.html', context)

    except Exception as e:
        print(f"Error: {e}")
        messages.error(request, f"Error: {e}")
        return redirect('/')

@group_required('Profesor')
def pro_deactivate(request,PRO_NID):
    try:
        pro = get_object_or_404(PROYECTO, PRO_NID = PRO_NID)
        if pro.profesor != request.user and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para modificar este proyecto.')
            return redirect('pro_listall')
            
        pro.PRO_ESTADO = not pro.PRO_ESTADO
        pro.save()
        messages.success(request,'Estado del proyecto cambiado correctamente.')
        return redirect('pro_listall')
    except Exception as e:
        print(e)
        messages.error(request,'Error al cambiar estado de proyecto')
        return redirect('pro_listall')

@login_required(login_url="/login/")
def pro_listone(request, PRO_NID):
    try:
        proyecto = get_object_or_404(PROYECTO, PRO_NID = PRO_NID)
        es_alumno_asignado = proyecto.alumnos.filter(id=request.user.id).exists()
        es_profesor_guia = (proyecto.profesor == request.user)
        if not es_alumno_asignado and not es_profesor_guia and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para ver este proyecto.')
            return redirect('pro_listall')

        listado_fases_proyectos = []
        fases_proyecto = FASE_PROYECTO.objects.filter(PRO_NID = proyecto).order_by('FA_NNUMERO_FASE')
        
        for fase in fases_proyecto:
            documentos_solicitado_fase = FASE_TIPO_DOCUMENTO.objects.filter(FA_NID=fase)
            cant_doc = documentos_solicitado_fase.count()
            
            total_listo_x_fase = 0
            if cant_doc > 0:
                doc_aprobados = FASE_DOCUMENTO.objects.filter(
                    FA_NID=fase, 
                    DOC_NID__DOC_APROBADO=True
                ).count()
                total_listo_x_fase =( doc_aprobados / cant_doc) * 100

            listado_fases_proyectos.append([fase.FA_NID, fase.FA_CNOMBRE, fase.FA_NNUMERO_FASE, fase.PRO_FFECHAINCIO , fase.PRO_FFECHATERMINO, cant_doc, int(total_listo_x_fase)])
        
        context = {
            'fases':listado_fases_proyectos,
            'proyecto':proyecto,
            'is_profesor': es_profesor_guia or request.user.is_superuser
        }
        return render(request,'capstone/proyecto/pro_listone.html',context)
    except Exception as e:
        print(e)
        return redirect('/')

@login_required(login_url="/login/")
def fase_listone(request, FA_NID):
    try:
        fase = get_object_or_404(FASE_PROYECTO, FA_NID=FA_NID)
        proyecto = fase.PRO_NID

        es_alumno_asignado = proyecto.alumnos.filter(id=request.user.id).exists()
        es_profesor_guia = (proyecto.profesor == request.user)
        if not es_alumno_asignado and not es_profesor_guia and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para ver esta fase.')
            return redirect('pro_listall')

        tipos_doc_solicitados = FASE_TIPO_DOCUMENTO.objects.filter(FA_NID=fase)
        doc_cargados = FASE_DOCUMENTO.objects.filter(FA_NID=fase)
        
        lst_data = []
        cant_doc_solicitados = tipos_doc_solicitados.count()
        cant_doc_cargados = 0
        cant_doc_aprobados = 0
        cant_no_aprobados = 0
        cant_espera = 0

        for tipo in tipos_doc_solicitados:
            tipo_doc = tipo.TD_NID
            estado_doc = None
            doc_contenido = None
            fecha_carga = None
            doc_id = None
            doc_comentario = None
            documento_encontrado = None

            # Busca el último documento cargado para este tipo de doc en esta fase
            doc_link = doc_cargados.filter(DOC_NID__TD_NID=tipo_doc).order_by('-DOC_NID__DOC_FECHA_MODIFICACION').first()
            
            if doc_link:
                documento_encontrado = doc_link.DOC_NID
                cant_doc_cargados += 1 
                doc_contenido = documento_encontrado.DOC_CONTENIDO
                fecha_carga = documento_encontrado.DOC_FECHA_MODIFICACION
                estado_doc = documento_encontrado.DOC_APROBADO
                doc_id = documento_encontrado.DOC_NID
                doc_comentario = documento_encontrado.DOC_COMENTARIO

                if estado_doc == True:
                    cant_doc_aprobados += 1
                elif estado_doc == False:
                    cant_no_aprobados += 1
                else:
                    cant_espera += 1
            
            lst_data.append([
                tipo_doc.TD_NOMBRE, 
                doc_contenido, 
                fecha_carga, 
                estado_doc, 
                tipo_doc.TD_NID,
                doc_id,
                doc_comentario
            ])

        porcentaje_aprobados = 0
        if cant_doc_solicitados > 0:
            porcentaje_aprobados = (cant_doc_aprobados / cant_doc_solicitados) * 100
            
        cant_doc_faltantes = cant_doc_solicitados - cant_doc_cargados
        
        context = {
            'fase': fase,
            'lst_data': lst_data,
            'cant_doc_solicitados': cant_doc_solicitados,
            'cant_doc_faltantes': cant_doc_faltantes,
            'cant_doc_cargados': cant_doc_cargados,
            'cant_doc_aprobados': cant_doc_aprobados,
            'cant_no_aprobados': cant_no_aprobados,
            'cant_espera': cant_espera,
            'porcentaje_aprobados': int(porcentaje_aprobados),
            'is_profesor': es_profesor_guia or request.user.is_superuser
        }
        return render(request, 'capstone/proyecto/fa_listone.html', context)
    except Exception as e:
        print(e)
        return redirect('/')
    
@group_required('Profesor')
def fase_update(request, FA_NID):
    try:
        fase = get_object_or_404(FASE_PROYECTO, FA_NID=FA_NID)
        
        # Verificar que el usuario sea el dueño del proyecto
        if fase.PRO_NID.profesor != request.user and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para editar esta fase.')
            return redirect('pro_listone', PRO_NID=fase.PRO_NID.PRO_NID)

        if request.method == "POST":
            # Actualizar datos básicos
            fase.FA_CNOMBRE = request.POST.get('nombre_fase')
            fase.FA_CDESCRICPCION = request.POST.get('desc_fase')
            fase.PRO_FFECHAINCIO = request.POST.get('fecha_inicio')
            fase.PRO_FFECHATERMINO = request.POST.get('fecha_termino')
            fase.save()
            
            messages.success(request, 'Fase actualizada correctamente.')
            return redirect('pro_listone', PRO_NID=fase.PRO_NID.PRO_NID)

        else:
            # GET: Mostrar formulario de edición
            # Necesitamos un template simple para editar la fase
            context = {'fase': fase}
            return render(request, 'capstone/proyecto/fa_edit.html', context)

    except Exception as e:
        print(f"Error editando fase: {e}")
        messages.error(request, 'Error al editar la fase.')
        return redirect('/')

@group_required('Profesor')
def fase_delete(request, FA_NID):
    try:
        fase = get_object_or_404(FASE_PROYECTO, FA_NID=FA_NID)
        id_proyecto = fase.PRO_NID.PRO_NID
        
        # Verificar permisos
        if fase.PRO_NID.profesor != request.user and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para eliminar esta fase.')
            return redirect('pro_listone', PRO_NID=id_proyecto)
            
        # Verificar que no sea la única fase (Regla de negocio opcional pero recomendada)
        total_fases = FASE_PROYECTO.objects.filter(PRO_NID=fase.PRO_NID).count()
        if total_fases <= 1:
            messages.error(request, 'No puedes eliminar la única fase del proyecto.')
            return redirect('pro_listone', PRO_NID=id_proyecto)

        fase.delete()
        messages.success(request, 'Fase eliminada correctamente.')
        return redirect('pro_listone', PRO_NID=id_proyecto)

    except Exception as e:
        print(f"Error eliminando fase: {e}")
        messages.error(request, 'Error al eliminar la fase.')
        return redirect('/')
    
#############################
######## DOCUMENTOS #########
#############################
@login_required(login_url="/login/")
def doc_listall(request):
    try:
        # Mostramos SOLO los documentos marcados como GUÍA
        docs = DOCUMENTO.objects.filter(DOC_ES_GUIA=True).order_by('-DOC_FFECHACREACION')
        
        is_profesor = request.user.groups.filter(name__iexact='profesor').exists() or request.user.is_superuser

        context = { 
            'docs': docs,
            'is_profesor': is_profesor 
        }
        return render(request,'capstone/documento/doc_listall.html',context)
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar listado')
        return redirect('/')
    
@login_required(login_url="/login/")
@group_required('Profesor')
def create_doc_guia(request):
    try:
        if request.method == "POST":
            nombre_doc = request.POST.get('DOC_NOMBRE')
            id_tipo = request.POST.get('tipo_select')
            archivo = request.FILES.get('DOC_CONTENIDO')

            if not id_tipo or not archivo:
                messages.error(request, "Faltan datos.")
                return redirect('create_doc_guia')

            # Guardamos como GUÍA (DOC_ES_GUIA=True)
            # No lo vinculamos a ninguna fase (FASE_DOCUMENTO)
            DOCUMENTO.objects.create(
                DOC_NOMBRE=nombre_doc,
                DOC_CONTENIDO=archivo,
                TD_NID_id=id_tipo,
                DOC_APROBADO=True, 
                DOC_COMENTARIO="Documento Guía / Plantilla",
                DOC_ES_GUIA=True 
            )

            messages.success(request, 'Documento guía publicado correctamente.')
            return redirect('doc_listall')

        else:
            # GET: Solo necesitamos los tipos de documento
            tipos = TIPO_DOCUMENTO.objects.all()
            context = { 'tipos': tipos }
            return render(request, 'capstone/documento/doc_addone.html', context)

    except Exception as e:
        print(f"Error: {e}")
        return redirect('doc_listall')

@login_required(login_url="/login/")
def create_doc(request):
    try:
        if request.method == "POST":
            # 1. Obtener datos clave del formulario (Ocultos en el HTML)
            id_fase = request.POST.get('FA_NID')
            id_tipo_doc = request.POST.get('TD_NID')
            redirect_to = request.POST.get('next', '')

            # Validación
            if not id_fase or not id_tipo_doc:
                messages.error(request, 'Error: Faltan datos de Fase o Tipo.')
                return redirect(redirect_to or 'pro_listall')

            fase = get_object_or_404(FASE_PROYECTO, FA_NID=id_fase)
            tipo = get_object_or_404(TIPO_DOCUMENTO, TD_NID=id_tipo_doc)

            # 2. Buscar si YA EXISTE un documento de este tipo en esta fase (Para reemplazarlo)
            link_existente = FASE_DOCUMENTO.objects.filter(FA_NID=fase, DOC_NID__TD_NID=tipo).first()

            if link_existente:
                # --- CASO A: RE-SUBIR (Actualizar existente) ---
                doc = link_existente.DOC_NID
                form = formDOCUMENTO(request.POST, request.FILES, instance=doc)
                if form.is_valid():
                    d = form.save(commit=False)
                    d.DOC_APROBADO = None # ¡IMPORTANTE! Resetea a "En Revisión" (Gris)
                    d.DOC_COMENTARIO = "" # Limpia comentarios de rechazo viejos
                    d.save()
                    messages.success(request, 'Documento actualizado y enviado a revisión.')
                else:
                    messages.error(request, f'Error al actualizar: {form.errors}')

            else:
                # --- CASO B: NUEVO (Crear de cero) ---
                form = formDOCUMENTO(request.POST, request.FILES)
                if form.is_valid():
                    # Guardar documento
                    d = form.save(commit=False)
                    d.TD_NID = tipo # Asignar el tipo
                    d.DOC_APROBADO = None # Estado "En Revisión"
                    d.save()

                    # ¡VITAL! Crear el vínculo con la fase
                    FASE_DOCUMENTO.objects.create(FA_NID=fase, DOC_NID=d)
                    
                    messages.success(request, 'Documento cargado exitosamente.')
                else:
                    messages.error(request, f'Error al cargar: {form.errors}')

            # Redirección inteligente (vuelve a la misma fase)
            if redirect_to:
                return HttpResponseRedirect(redirect_to)
            return redirect('fase_listone', FA_NID=id_fase)

        else:
            return redirect('/')
            
    except Exception as e:
        print(f"Error en create_doc: {e}")
        messages.error(request, 'Error interno del servidor.')
        return redirect('/')

@group_required('Profesor') 
def doc_update(request, DOC_NID):
    try:
        doc = get_object_or_404(DOCUMENTO, DOC_NID=DOC_NID)
        
        # --- LÓGICA DE PERMISOS ---
        fase_doc = FASE_DOCUMENTO.objects.filter(DOC_NID=doc).first()
        
        # CASO 1: Es un documento de proyecto (alumno)
        if fase_doc:
            if fase_doc.FA_NID.PRO_NID.profesor != request.user and not request.user.is_superuser:
                messages.error(request, 'No tienes permiso para modificar este documento de alumno.')
                return redirect('pro_listall')
            redirect_target = 'fase_listone'
            redirect_args = {'FA_NID': fase_doc.FA_NID.FA_NID}
            
        # CASO 2: Es un documento Guía / Plantilla (Sin fase)
        elif doc.DOC_ES_GUIA:
            # Como ya tienes el decorador @group_required('Profesor'), ya sabemos que puede editar
            redirect_target = 'doc_listall'
            redirect_args = {}
            
        else:
            # Caso raro: documento huérfano que no es guía
            messages.error(request, 'El documento no tiene contexto válido.')
            return redirect('doc_listall')

        # --- PROCESO DE GUARDADO ---
        if request.method == "POST":
            form = formDOCUMENTO(request.POST, request.FILES, instance=doc)
            if form.is_valid():
                form.save()
                messages.success(request, 'Documento actualizado correctamente.')
                
                # Redirección dinámica según el tipo
                return redirect(redirect_target, **redirect_args)
            else:
                messages.error(request, 'Error al actualizar documento')
                # Si falla, intentamos volver a donde corresponda
                if fase_doc:
                     return redirect('fase_listone', FA_NID=fase_doc.FA_NID.FA_NID)
                return redirect('doc_listall')
                
        else:
            # GET: Cargar formulario
            form = formDOCUMENTO(instance=doc)
            # Reutilizamos el template de agregar, pero le pasamos el contexto necesario
            # Si usas selectores de tipos, asegúrate de pasarlos si el template lo exige
            tipos = TIPO_DOCUMENTO.objects.all() 
            context = { 'form': form, 'tipos': tipos } 
            return render(request, 'capstone/documento/doc_addone.html', context)
            
    except Exception as e:
        print(f"Error en doc_update: {e}")
        messages.error(request, 'Error interno al cargar formulario')
        return redirect('doc_listall')

@group_required('Profesor')
def doc_delete(request, DOC_NID):
    try:
        doc = get_object_or_404(DOCUMENTO, DOC_NID=DOC_NID)
        
        # --- LÓGICA DE PERMISOS Y REDIRECCIÓN ---
        fase_doc = FASE_DOCUMENTO.objects.filter(DOC_NID=doc).first()
        
        # CASO 1: Es documento de Proyecto
        if fase_doc:
            if fase_doc.FA_NID.PRO_NID.profesor != request.user and not request.user.is_superuser:
                messages.error(request, 'No tienes permiso para eliminar este documento.')
                return redirect('pro_listall')
            
            fase_id = fase_doc.FA_NID.FA_NID
            fase_doc.delete() # Borramos la relación primero
            doc.delete()      # Borramos el archivo
            
            messages.success(request, 'Documento eliminado del proyecto.')
            return redirect('fase_listone', FA_NID=fase_id)

        # CASO 2: Es documento Guía / Plantilla
        elif doc.DOC_ES_GUIA:
            # El decorador ya validó que es Profesor
            doc.delete()
            messages.success(request, 'Plantilla eliminada correctamente.')
            return redirect('doc_listall')
            
        else:
            # Documento huérfano desconocido
            doc.delete()
            messages.warning(request, 'Documento eliminado (sin asociación encontrada).')
            return redirect('doc_listall')

    except Exception as e:
        print(f"Error en doc_delete: {e}")
        messages.error(request, 'Error al eliminar documento')
        return redirect('doc_listall')
    
@group_required('Profesor')
def pro_delete(request, PRO_NID):
    try:
        pro = get_object_or_404(PROYECTO, PRO_NID=PRO_NID)
        if pro.profesor != request.user and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para eliminar este proyecto.')
            return redirect('pro_listall')
        pro.delete()
        messages.success(request, 'Proyecto eliminado permanentemente.')
        return redirect('pro_listall')
    except Exception as e:
        print(e)
        messages.error(request, 'Error al eliminar el proyecto.')
        return redirect('pro_listall')
    
@group_required('Profesor')
def aprobar_documento(request, DOC_NID):
    if request.method == "POST":
        doc = get_object_or_404(DOCUMENTO, DOC_NID=DOC_NID)
        doc.DOC_APROBADO = True
        doc.DOC_COMENTARIO = "¡Documento aprobado! Buen trabajo."
        doc.save()
        messages.success(request, 'Documento aprobado correctamente.')
    
    fase_doc = FASE_DOCUMENTO.objects.filter(DOC_NID=doc).first()
    return redirect('fase_listone', FA_NID=fase_doc.FA_NID.FA_NID)

@group_required('Profesor')
def rechazar_documento(request, DOC_NID):
    if request.method == "POST":
        doc = get_object_or_404(DOCUMENTO, DOC_NID=DOC_NID)
        comentario = request.POST.get('comentario_rechazo', 'Sin comentarios.')
        
        doc.DOC_APROBADO = False
        doc.DOC_COMENTARIO = comentario
        doc.save()
        messages.warning(request, 'Documento rechazado. Se ha notificado al alumno.')

    fase_doc = FASE_DOCUMENTO.objects.filter(DOC_NID=doc).first()
    return redirect('fase_listone', FA_NID=fase_doc.FA_NID.FA_NID)

login_required(login_url="/login/")
@group_required('Profesor')
def create_doc_general(request):
    try:
        if request.method == "POST":
            # 1. Obtener datos
            nombre_doc = request.POST.get('DOC_NOMBRE')
            id_fase = request.POST.get('fase_select')
            id_tipo = request.POST.get('tipo_select')
            archivo = request.FILES.get('DOC_CONTENIDO')

            # Validación básica
            if not id_fase or not id_tipo or not archivo:
                messages.error(request, "Error: Faltan datos obligatorios (Fase, Tipo o Archivo).")
                # Volvemos a cargar la página (GET) para no perderse
                return redirect('create_doc_general')

            # 2. Guardar Documento
            nuevo_doc = DOCUMENTO.objects.create(
                DOC_NOMBRE=nombre_doc,
                DOC_CONTENIDO=archivo,
                TD_NID_id=id_tipo,
                DOC_APROBADO=True, 
                DOC_COMENTARIO="Cargado por Profesor (Documento Guía)"
            )

            # 3. Vincular a Fase
            FASE_DOCUMENTO.objects.create(
                FA_NID_id=id_fase,
                DOC_NID=nuevo_doc
            )

            messages.success(request, 'Documento guía cargado correctamente.')
            return redirect('doc_listall')

        else:
            # GET: Cargar datos para los selectores
            proyectos = PROYECTO.objects.filter(profesor=request.user)
            tipos = TIPO_DOCUMENTO.objects.all()
            
            # Serializamos las fases para JavaScript (solo ID, Nombre y ID de Proyecto)
            fases_data = list(FASE_PROYECTO.objects.filter(PRO_NID__in=proyectos).values('FA_NID', 'FA_CNOMBRE', 'PRO_NID', 'FA_NNUMERO_FASE'))
            # Convertimos a JSON string
            fases_json = json.dumps(fases_data)

            context = {
                'proyectos': proyectos,
                'tipos': tipos,
                'fases_json': fases_json
            }
            return render(request, 'capstone/documento/doc_addone.html', context)

    except Exception as e:
        print(f"Error en create_doc_general: {e}")
        messages.error(request, f"Error interno: {e}")
        return redirect('doc_listall')
    


@login_required(login_url="/login/")
def descargar_archivo(request, DOC_NID):
    try:
        doc = get_object_or_404(DOCUMENTO, DOC_NID=DOC_NID)
        
        if not doc.DOC_CONTENIDO:
            raise Http404("El documento no tiene un archivo físico asociado.")

        archivo_handle = doc.DOC_CONTENIDO.open('rb')

        nombre_final = doc.DOC_NOMBRE
        
        nombre_fisico = doc.DOC_CONTENIDO.name
        ext = os.path.splitext(nombre_fisico)[1]

        if not nombre_final.lower().endswith(ext.lower()):
            nombre_final += ext

        content_type, _ = mimetypes.guess_type(nombre_fisico)
        if not content_type:
            content_type = 'application/octet-stream'

        response = FileResponse(archivo_handle, content_type=content_type)
        nombre_codificado = escape_uri_path(nombre_final)
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{nombre_codificado}"
        
        return response

    except Exception as e:
        print(f"Error al descargar: {e}")
        messages.error(request, 'Error al procesar la descarga.')
        return redirect('doc_listall')