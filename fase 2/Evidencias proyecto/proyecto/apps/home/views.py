# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import (HttpResponseRedirect, get_object_or_404,
                              redirect, render, resolve_url)
from .models import *
from .forms import *
from django.contrib import messages

@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('gradient/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
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

## FUNCION PARA CARGAR LISTADO DE EMPRESAS ##
def emp_listall(request):
    try:
        emps = EMPRESA.objects.all()
        context = {
            'emps': emps
        }
        return render(request,'capstone/empresa/emp_listall.html',context)
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar listado')
        return redirect('/')

## FUNCION PARA CREAR UNA NUEVA EMPRESA ##    
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
            context = {
                'form':form
            }
            return render(request,'capstone/empresa/emp_addone.html',context)
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        redirect('emp_listall')

## FUNCION PARA ACTUALIZAR UNA EMPRESA ##
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
            context = {
                'form':form
            }
            return render(request,'capstone/empresa/emp_addone.html',context)

    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        redirect('/')

## FUNCION PARA ACTIVAR/DESACTIVAR UNA EMPRESA ##
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

## FUNCION PARA CARGAR LISTADO DE TIPOS DE DOCUMENTOS ##
def tipodoc_listall(request):
    try:
        tipos = TIPO_DOCUMENTO.objects.all()
        context = {
            'tipos': tipos
        }
        return render(request,'capstone/tipos_documentos/tipodoc_listall.html',context)
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar listado')
        return redirect('/')
    
## FUNCION PARA CREAR NUEVO TIPO DE DOCUMENTO ##    
def create_tipo_doc(request):
    try:
        if request.method == "POST":
            nombre = request.POST.get('nombre')
            tipo_doc = TIPO_DOCUMENTO.objects.create(
                TD_NOMBRE = nombre
            )
            messages.success(request,'Tipo de documento agregado correctamente')
            return redirect('tipodoc_listall')
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        return redirect('tipodoc_listall')

## FUNCION PARA ACTUALIZAR UN TIPO DE DOCUMENTO ##
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

## FUNCION PARA ACTIVAR/DESACTIVAR UN TIPO DE DOCUMENTO##
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

## FUNCION PARA CARGAR LISTADO DE PROYECTOS ##
def pro_listall(request):
    try:
        
        listado_proyectos = []
        proyectos = PROYECTO.objects.all()
        for pro in proyectos:
            fases_proyecto = FASE_PROYECTO.objects.filter(PRO_NID__PRO_NID = pro.PRO_NID)
            total_listo_x_fase = 0
            for fase in fases_proyecto:
                doc_listos = 0
                documentos_solicitado_fase = FASE_TIPO_DOCUMENTO.objects.filter(FA_NID__FA_NID  = fase.FA_NID)
                cant_doc = len(documentos_solicitado_fase)
                documentos_fase = FASE_DOCUMENTO.objects.filter(FA_NID__FA_NID  = fase.FA_NID)
                if documentos_fase:
                    for doc in documentos_fase:
                        if doc.DOC_NID.DOC_APROBADO == True:
                            doc_listos += 1
                if doc_listos == 0:
                    total_listo_x_fase = 0
                else:
                    total_listo_x_fase =( doc_listos / cant_doc) * 100
            listado_proyectos.append([pro.PRO_NID, pro.PRO_CNOMBRE, pro.EMP_NID.EM_CNOMBRE, pro.PRO_FFECHACREACION, total_listo_x_fase])

        context = {
            'proyectos': listado_proyectos
        }
        return render(request,'capstone/proyecto/pro_listall.html',context)
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar listado')
        return redirect('/')

## FUNCION PARA CREAR NUEVO PROYECTO ##    
def create_pro(request):
    try:
        if request.method == "POST":
            form = formPROYECTO(request.POST)
            if form.is_valid():
                # PRIMERO SE CREA EL PROYECTO
                form.save()
                # DESPUES BUSCAMOS LA CANTIDAD DE FASES
                cant_fases = int(request.POST.get('cant_fases'))
                # CREAMOS UN CICLO for CON LA CANTIDAD DE FASES 
                for i in range(1,cant_fases+1):
                    # OBTENEMOS LOS DATOS DE CADA FASE
                    nombre_fase = request.POST.get(f'nombre_fase_{i}')
                    descripcion_fase = request.POST.get(f'descripcion_fase_{i}')
                    fecha_inicio_fase = request.POST.get(f'fecha_inicio_fase_{i}')
                    fecha_termino_fase = request.POST.get(f'fecha_termino_fase_{i}')
                    # BUSCAMOS LOS ids DE LOS DOCUMENTOS PARA CADA FAS
                    documentos_fase = request.POST.getlist(f'documentos_fase_{i}[]')
                    # VERIFICAMOS SI EXISTEN LOS DATOS PARA CREAR LA FASE
                    if nombre_fase and fecha_inicio_fase and fecha_termino_fase:
                        # CREAMOS LA FASE
                        fase = FASE_PROYECTO.objects.create(
                            FA_CNOMBRE = nombre_fase,
                            FA_NNUMERO_FASE = i,
                            FA_CDESCRICPCION = descripcion_fase,
                            PRO_FFECHAINCIO = fecha_inicio_fase,
                            PRO_FFECHATERMINO = fecha_termino_fase,
                            PRO_NID_id = form.instance.pk
                        )
                        # CREAMOS OTRO CICLO for PARA RECORRER EL LISTADO DE ids DE LOS DOCUMENTOS 
                        for id in documentos_fase:
                            # CREAMOS LA CONEXION DE CADA DOCUMENTO CON LA FASE 
                            documento_fase_create = FASE_TIPO_DOCUMENTO.objects.create(
                                FA_NID_id = fase.pk,
                                TD_NID_id = int(id),
                            )
            messages.success(request,'Proyecto creado correctamente')
            return redirect('pro_listall')

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

## FUNCION PARA ACTUALIZAR UN PROYECTO ##
def pro_update(request,PRO_NID):
    try:
        pro = PROYECTO.objects.get(PRO_NID = PRO_NID)
        if request.method == "POST":
            form = formPROYECTO(request.POST, instance=pro)
            if form.is_valid():
                form.save()
            else:
                messages.error(request, 'Error al actualizar proyecto')
                return redirect('pro_listall')
            return render(request,'capstone/proyecto/pro_addone.html',context)
        else:
            form = formPROYECTO(instance=pro)
            context = {
                'form':form
            }
            return render(request,'capstone/proyecto/pro_addone.html',context)

    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        return redirect('/')

## FUNCION PARA ACTIVAR/DESACTIVAR UN PROYECTO##
def pro_deactivate(request,PRO_NID):
    try:
        pro =  PROYECTO.objects.get(PRO_NID = PRO_NID)
        pro.PRO_ESTADO = not pro.PRO_ESTADO
        pro.save()
        messages.success(request,'Estado del proyecto cambiado correctamente.')
        return redirect('')

    except Exception as e:
        print(e)
        messages.error(request,'Error al cambiar estado de proyecto')
        return redirect('')

def pro_listone(request, PRO_NID):
    try:
        listado_fases_proyectos = []
        proyecto = PROYECTO.objects.get(PRO_NID = PRO_NID)
        fases_proyecto = FASE_PROYECTO.objects.filter(PRO_NID = proyecto).order_by('FA_NNUMERO_FASE')
        total_listo_x_fase = 0
        for fase in fases_proyecto:
            doc_listos = 0
            documentos_solicitado_fase = FASE_TIPO_DOCUMENTO.objects.filter(FA_NID__FA_NID  = fase.FA_NID)
            cant_doc = len(documentos_solicitado_fase)
            documentos_fase = FASE_DOCUMENTO.objects.filter(FA_NID__FA_NID  = fase.FA_NID)
            if documentos_fase:
                for doc in documentos_fase:
                    if doc.DOC_NID.DOC_APROBADO == True:
                        doc_listos += 1
            if doc_listos == 0:
                total_listo_x_fase = 0
            else:
                total_listo_x_fase =( doc_listos / cant_doc) * 100
            listado_fases_proyectos.append([fase.FA_NID, fase.FA_CNOMBRE, fase.FA_NNUMERO_FASE, fase.PRO_FFECHAINCIO , fase.PRO_FFECHATERMINO, cant_doc, total_listo_x_fase])
        context = {
            'fases':listado_fases_proyectos,
            'proyecto':proyecto
        }
        return render(request,'capstone/proyecto/pro_listone.html',context)
    
    except Exception as e:
        print(e)
#############################
######## DOCUMENTOS #########
#############################

## FUNCION PARA CARGAR LISTADO DE DOCUMENTOS ##
def doc_listall(request):
    try:
        docs = DOCUMENTO.objects.all()
        context = {
            'docs': docs
        }
        return render(request,'',context)
    except Exception as e:
        print(e)
        messages.error(request,'Error al cargar listado')
        return redirect('/')

## FUNCION PARA CREAR NUEVO DOCUMENTO ##    
def create_doc(request):
    try:
        if request.method == "POST":
            form = formDOCUMENTO(request.POST, request.FILES)
            if form.is_valid():
                form.save()
            
            messages.success(request,'Documento agregado correctamente')
            return redirect('/')

        else:
            form = formDOCUMENTO()
            context = {
                'form':form
            }
            return render(request,'',context)
    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        redirect('/')

## FUNCION PARA ACTUALIZAR UN DOCUMENTO ##
def doc_update(request,DOC_NID):
    try:
        doc = DOCUMENTO.objects.get(DOC_NID = DOC_NID)
        if request.method == "POST":
            form = formDOCUMENTO(request.POST, request.FILES, instance=doc)
            if form.is_valid():
                form.save()
            else:
                messages.error(request, 'Error al actualizar documento')
                redirect('/')
            return render(request,'')
        else:
            form = formDOCUMENTO(instance=doc)
            context = {
                'form':form
            }
            return render(request,'',context)

    except Exception as e:
        print(e)
        messages.error(request, 'Error al cargar formulario')
        redirect('/')

## FUNCION PARA ELIMINAR UN DOCUMENTO##
def doc_delete(request,DOC_NID):
    try:
        doc =  DOCUMENTO.objects.get(DOC_NID = DOC_NID)
        doc.delete()
        messages.success(request,'Documento eliminado correctamente.')
        return redirect('')

    except Exception as e:
        print(e)
        messages.error(request,'Error al eliminar documento')
        return redirect('')

