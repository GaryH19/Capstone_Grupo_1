from django.contrib import admin
from .models import (REGION, COMUNA, EMPRESA, TIPO_DOCUMENTO, PROYECTO, 
                     FASE_PROYECTO, FASE_TIPO_DOCUMENTO, DOCUMENTO, 
                     FASE_DOCUMENTO)
# Register your models here.
admin.site.register(REGION)
admin.site.register(COMUNA)
admin.site.register(EMPRESA)
admin.site.register(TIPO_DOCUMENTO)
admin.site.register(PROYECTO)
admin.site.register(FASE_PROYECTO)
admin.site.register(FASE_TIPO_DOCUMENTO)
admin.site.register(DOCUMENTO)
admin.site.register(FASE_DOCUMENTO)