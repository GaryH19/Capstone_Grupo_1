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

# --- FUNCIÓN DE SEGURIDAD  ---
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
def usuario_create(request):
    try:
        print('Creacion de usuario para el final')
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar formulario')
        return redirect('')

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
        elif request.user.groups.filter(name__iexact='profesor').exists(): # Búsqueda insensible
            proyectos = PROYECTO.objects.filter(profesor=request.user)
        elif request.user.groups.filter(name__iexact='alumno').exists(): # Búsqueda insensible
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
                proyecto = form.save(commit=False)
                proyecto.profesor = request.user 
                proyecto.save()
                form.save_m2m() # Guarda alumnos

                cant_fases = int(request.POST.get('cant_fases'))
                for i in range(1,cant_fases+1):
                    nombre_fase = request.POST.get(f'nombre_fase_{i}')
                    descripcion_fase = request.POST.get(f'descripcion_fase_{i}')
                    fecha_inicio_fase = request.POST.get(f'fecha_inicio_fase_{i}')
                    fecha_termino_fase = request.POST.get(f'fecha_termino_fase_{i}')
                    documentos_fase = request.POST.getlist(f'documentos_fase_{i}[]')

                    if nombre_fase and fecha_inicio_fase and fecha_termino_fase:
                        fase = FASE_PROYECTO.objects.create(
                            FA_CNOMBRE = nombre_fase,
                            FA_NNUMERO_FASE = i,
                            FA_CDESCRICPCION = descripcion_fase,
                            PRO_FFECHAINCIO = fecha_inicio_fase,
                            PRO_FFECHATERMINO = fecha_termino_fase,
                            PRO_NID_id = proyecto.pk
                        )
                        for id_doc in documentos_fase:
                            FASE_TIPO_DOCUMENTO.objects.create(
                                FA_NID_id = fase.pk,
                                TD_NID_id = int(id_doc),
                            )
                messages.success(request,'Proyecto creado correctamente')
                return redirect('pro_listall')
            else:
                # Si el form no es válido, recarga con los errores
                documentos = TIPO_DOCUMENTO.objects.all()
                context = { 'form':form, 'documentos':documentos }
                return render(request,'capstone/proyecto/pro_addone.html',context)
        else:
            form = formPROYECTO()
            documentos = TIPO_DOCUMENTO.objects.all()
            context = {
                'form':form,
                'documentos':documentos
            }
            return render(request,'capstone/proyecto/pro_addone.html',context)
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        return redirect('/')

@group_required('Profesor')
def pro_update(request,PRO_NID):
    try:
        pro = get_object_or_404(PROYECTO, PRO_NID = PRO_NID)
        if pro.profesor != request.user and not request.user.is_superuser:
            messages.error(request, 'No tienes permiso para editar este proyecto.')
            return redirect('pro_listall')

        if request.method == "POST":
            form = formPROYECTO(request.POST, instance=pro)
            if form.is_valid():
                form.save()
                messages.success(request,'Proyecto actualizado correctamente')
            else:
                messages.error(request, 'Error al actualizar proyecto')
            return redirect('pro_listall')
        else:
            form = formPROYECTO(instance=pro)
            context = { 'form':form }
            return render(request,'capstone/proyecto/pro_addone.html',context)
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
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

# -----------------------------------------------------------------
# --- ¡AQUÍ EMPIEZAN LAS FUNCIONES ACTUALIZADAS! ---
# -----------------------------------------------------------------

## FUNCION PARA VER DETALLE DE FASE (ACTUALIZADA) ##
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
                cant_doc_cargados += 1 # Contamos como cargado
                doc_contenido = documento_encontrado.DOC_CONTENIDO
                fecha_carga = documento_encontrado.DOC_FECHA_MODIFICACION
                estado_doc = documento_encontrado.DOC_APROBADO
                doc_id = documento_encontrado.DOC_NID
                doc_comentario = documento_encontrado.DOC_COMENTARIO

                if estado_doc == True:
                    cant_doc_aprobados += 1
                elif estado_doc == False:
                    cant_no_aprobados += 1
                else: # estado_doc is None
                    cant_espera += 1
            
            # 0: Nombre, 1: Archivo, 2: Fecha, 3: Estado, 4: ID Tipo, 5: ID Doc, 6: Comentario
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

    
#############################
######## DOCUMENTOS #########
#############################
@group_required('Profesor')
def doc_listall(request):
    try:
        docs = DOCUMENTO.objects.all()
        context = { 'docs': docs }
        return render(request,'capstone/documento/doc_listall.html',context)
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar listado')
        return redirect('/')

## FUNCION PARA CREAR/ACTUALIZAR DOCUMENTO (LÓGICA RE-SUBIR) ##
@login_required(login_url="/login/")
def create_doc(request):
    try:
        if request.method == "POST":
            redirect_to = request.POST.get('next', '')
            id_fase = request.POST.get('FA_NID')
            id_tipo_doc = request.POST.get('TD_NID')
            
            if not id_fase or not id_tipo_doc:
                messages.error(request, 'Error: No se especificó una fase o tipo de documento.')
                return redirect(redirect_to or '/')
                
            fase = get_object_or_404(FASE_PROYECTO, FA_NID=id_fase)
            proyecto = fase.PRO_NID
            tipo_doc = get_object_or_404(TIPO_DOCUMENTO, TD_NID=id_tipo_doc)

            # --- Verificación de Permisos ---
            es_alumno_asignado = proyecto.alumnos.filter(id=request.user.id).exists()
            if not es_alumno_asignado and not request.user.is_superuser:
                messages.error(request, 'No tienes permiso para subir documentos a este proyecto.')
                return redirect(redirect_to or 'pro_listall')
            
            # --- LÓGICA DE SUBIR vs RE-SUBIR ---
            # Buscamos si ya existe un documento para este TIPO en esta FASE
            link_existente = FASE_DOCUMENTO.objects.filter(FA_NID=fase, DOC_NID__TD_NID=tipo_doc).first()
            
            if link_existente:
                # --- ES UNA RE-SUBIDA (Actualizar) ---
                doc_existente = link_existente.DOC_NID
                
                # Validamos el formulario con los datos nuevos pero en la instancia existente
                form = formDOCUMENTO(request.POST, request.FILES, instance=doc_existente)
                if form.is_valid():
                    documento = form.save(commit=False)
                    documento.DOC_APROBADO = None # Resetea a "En Revisión"
                    documento.DOC_COMENTARIO = "Archivo corregido por el alumno."
                    documento.save()
                    messages.success(request,'Documento corregido y re-subido correctamente.')
                else:
                    messages.error(request, f'Error al re-subir: {form.errors}')
            
            else:
                # --- ES UNA SUBIDA NUEVA (Crear) ---
                form = formDOCUMENTO(request.POST, request.FILES)
                if form.is_valid():
                    documento = form.save()
                    # Conecta el documento a la fase
                    FASE_DOCUMENTO.objects.create(
                        FA_NID_id = id_fase,
                        DOC_NID_id = documento.pk
                    )
                    messages.success(request,'Documento agregado correctamente.')
                else:
                    messages.error(request, f'Error al subir: {form.errors}')
            
            if redirect_to:
                return HttpResponseRedirect(redirect_to)
            else:
                return redirect('pro_listall')
        else:
            messages.error(request, 'Acceso no válido')
            return redirect('/') 
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        return redirect('/')

@group_required('Profesor') 
def doc_update(request,DOC_NID):
    # Esta función ahora es solo para el admin, ya que create_doc maneja la re-subida
    try:
        doc = get_object_or_404(DOCUMENTO, DOC_NID = DOC_NID)
        fase_doc = FASE_DOCUMENTO.objects.filter(DOC_NID=doc).first()
        if not fase_doc or (fase_doc.FA_NID.PRO_NID.profesor != request.user and not request.user.is_superuser):
            messages.error(request, 'No tienes permiso para modificar este documento.')
            return redirect('pro_listall')
            
        if request.method == "POST":
            form = formDOCUMENTO(request.POST, request.FILES, instance=doc)
            if form.is_valid():
                form.save()
                messages.success(request, 'Documento actualizado por profesor.')
            else:
                messages.error(request, 'Error al actualizar documento')
            return redirect('fase_listone', FA_NID=fase_doc.FA_NID.FA_NID)
        else:
            form = formDOCUMENTO(instance=doc)
            context = { 'form':form }
            return render(request,'capstone/documento/doc_addone.html',context)
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        redirect('/')

@group_required('Profesor')
def doc_delete(request,DOC_NID):
    # Esta función ahora debería borrar el documento Y el link
    try:
        doc = get_object_or_404(DOCUMENTO, DOC_NID = DOC_NID)
        fase_doc = FASE_DOCUMENTO.objects.filter(DOC_NID=doc).first()
        if not fase_doc or (fase_doc.FA_NID.PRO_NID.profesor != request.user and not request.user.is_superuser):
            messages.error(request, 'No tienes permiso para eliminar este documento.')
            return redirect('pro_listall')
        
        # Guardamos la fase ANTES de borrar el link
        fase_id = fase_doc.FA_NID.FA_NID
        
        # Borramos el documento (el link se borra en cascada si está configurado, 
        # pero por si acaso borramos ambos)
        fase_doc.delete() 
        doc.delete()
        
        messages.success(request,'Documento eliminado permanentemente.')
        return redirect('fase_listone', FA_NID=fase_id)
    except Exception as e:
        print(e)
        messages.error(request,'Error al eliminar documento')
        return redirect('pro_listall')
    
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