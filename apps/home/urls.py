from django.urls import path, re_path
from apps.home import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import login_required

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    ## EMPRESAS ##
    path('emp_listall', login_required(views.emp_listall), name='emp_listall'),
    path('create_emp', login_required(views.create_emp), name='create_emp'),
    path('emp_update/<int:EMP_NID>', login_required(views.emp_update), name='emp_update'),
    path('emp_deactivate/<int:EMP_NID>', login_required(views.emp_deactivate), name='emp_deactivate'),


    ## TIPO DOCUMENTOS ##
    path('tipodoc_listall', login_required(views.tipodoc_listall), name='tipodoc_listall'),
    path('create_tipo_doc', login_required(views.create_tipo_doc), name='create_tipo_doc'),
    path('tipodoc_update/<int:TD_NID>', login_required(views.tipodoc_update), name='tipodoc_update'),
    path('tipodoc_deactivate/<int:TD_NID>', login_required(views.tipodoc_deactivate), name='tipodoc_deactivate'),

    ## PROYECTOS ##
    path('pro_listall', login_required(views.pro_listall), name='pro_listall'),
    path('create_pro', login_required(views.create_pro), name='create_pro'),
    path('pro_update/<int:PRO_NID>', login_required(views.pro_update), name='pro_update'),
    path('pro_listone/<int:PRO_NID>', login_required(views.pro_listone), name='pro_listone'),
    path('fase_listone/<int:FA_NID>', login_required(views.fase_listone), name='fase_listone'),
    path('pro_deactivate/<int:PRO_NID>', login_required(views.pro_deactivate), name='pro_deactivate'),
    path('pro_delete/<int:PRO_NID>', login_required(views.pro_delete), name='pro_delete'),
    
    ## DOCUMENTOS ##
    path('documento/crear', login_required(views.create_doc), name='create_doc'),
    path('documento/editar/<int:DOC_NID>/', login_required(views.doc_update), name='doc_update'),
    path('documento/eliminar/<int:DOC_NID>/', login_required(views.doc_delete), name='doc_delete'),
    
    # --- URLS DE APROBACIÓN AÑADIDAS ---
    path('documento/aprobar/<int:DOC_NID>/', login_required(views.aprobar_documento), name='aprobar_documento'),
    path('documento/rechazar/<int:DOC_NID>/', login_required(views.rechazar_documento), name='rechazar_documento'),
    # ------------------------------------

    # Matches any html file
    re_path(r'^.*\.*', views.pages, name='pages'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)