from django.contrib import admin
from .models import TipoUsuario, Proyecto, Fase, ItemDocumento, DocumentoGuia # <-- Añadir DocumentoGuia

admin.site.register(TipoUsuario) 
admin.site.register(Proyecto)
admin.site.register(Fase)
admin.site.register(ItemDocumento)
admin.site.register(DocumentoGuia) # <-- Añadir esta línea