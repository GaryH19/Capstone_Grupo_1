from django.db import models
from django.contrib.auth.models import User

User.add_to_class('rut', models.CharField('Rut',max_length=12, null= True, unique=True, blank=True))
User.add_to_class('telefono', models.CharField('Telefono',max_length=12, null= True, unique=True, blank=True))
# Create your models here.

class REGION(models.Model):
    RE_NID = models.BigAutoField(("ID"), primary_key=True)
    RE_CNOMBRE =models.CharField(("Nombre"),max_length=128)
    RE_CCODIGO =models.CharField(("Código"),max_length=64)

    class Meta:
            db_table = "REGION"

    def __str__(self):
        return self.RE_CNOMBRE

class COMUNA(models.Model):
    COM_NID = models.BigAutoField(("ID"), primary_key=True)
    RE_NID = models.ForeignKey(REGION,verbose_name="Id Region",on_delete=models.PROTECT)#campo obligatorio
    COM_CNOMBRE = models.CharField(("Nombre"),max_length=128)
    COM_CCODIGO = models.CharField(("Código"),max_length=64)

    class Meta:
        db_table = "COMUNA"

    def __str__(self):
        return self.COM_CNOMBRE

class EMPRESA(models.Model):
    EMP_NID = models.BigAutoField(("ID"), primary_key=True)
    EM_CNOMBRE = models.CharField(("Nombre"),max_length=128)
    EM_RUT = models.CharField('Rut empresa',max_length=12, null= True, unique=True, blank=True)
    COM_NID = models.ForeignKey(COMUNA,verbose_name="Id Comuna",on_delete=models.PROTECT)
    EMP_ESTADO = models.BooleanField(default=True)

    class Meta:
        db_table = "EMPRESA"

    def __str__(self):
        return self.EM_CNOMBRE
    
class TIPO_DOCUMENTO(models.Model):
    TD_NID = models.BigAutoField(("ID"), primary_key=True)
    TD_NOMBRE = models.CharField(("Nombre"),max_length=128)
    TD_ESTADO = models.BooleanField(default=True)

    class Meta:
        db_table = "TIPO_DOCUMENTO"

    def __str__(self):
        return self.TD_NOMBRE
    
class PROYECTO(models.Model):
    PRO_NID = models.BigAutoField(("ID"), primary_key=True)
    PRO_CNOMBRE =models.CharField(("Nombre"),max_length=128)
    PRO_FFECHACREACION = models.DateTimeField(auto_now_add=True)
    EMP_NID = models.ForeignKey(EMPRESA,verbose_name="Id Empresa",on_delete=models.PROTECT)
    PRO_ESTADO = models.BooleanField(default=True)
    profesor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Profesor Guía",
        related_name="proyectos_creados",
        # Limita las opciones en el admin a usuarios del grupo "Profesor"
        limit_choices_to={'groups__name': "Profesor"}, 
        null=True, blank=True
    )
    alumnos = models.ManyToManyField(
        User,
        verbose_name="Alumnos Asignados",
        related_name="proyectos_asignados",
        # Limita las opciones a usuarios del grupo "Alumno"
        limit_choices_to={'groups__name': "Alumno"},
        blank=True
    )
    class Meta:
        db_table = "PROYECTO"

    def __str__(self):
        return self.PRO_CNOMBRE
    
class FASE_PROYECTO(models.Model):
    FA_NID = models.BigAutoField(("ID"), primary_key=True)
    FA_CNOMBRE =models.CharField(("Nombre"),max_length=128)
    FA_NNUMERO_FASE =models.IntegerField(("Numero Fase"),blank=True, null=True)
    FA_CDESCRICPCION =models.CharField(("Descripcion"),max_length=1028)
    PRO_FFECHAINCIO = models.DateTimeField()
    PRO_FFECHATERMINO = models.DateTimeField()
    # Usar CASCADE aquí es útil para que al borrar el proyecto, se borren las fases
    PRO_NID = models.ForeignKey(PROYECTO,verbose_name="Id Proyecto",on_delete=models.CASCADE)
    FA_COMPLETADO = models.BooleanField(default=False)

    class Meta:
        db_table = "FASE_PROYECTO"

    def __str__(self):
        return self.FA_CNOMBRE
 
#ESTAS TABLA SERA PARA SABER CUALES SON LOS DOCUMENTOS SOLICITADOS POR CADA FASE
class FASE_TIPO_DOCUMENTO(models.Model):
    FTD_NID = models.BigAutoField(("ID"), primary_key=True)
    # Usar CASCADE aquí es útil para que al borrar la fase, se borren los requerimientos
    FA_NID = models.ForeignKey(FASE_PROYECTO,verbose_name="Id Fase proyecto",on_delete=models.CASCADE)
    TD_NID = models.ForeignKey(TIPO_DOCUMENTO,verbose_name="Id Tipo Documento",on_delete=models.PROTECT)

    class Meta:
        db_table = "FASE_TIPO_DOCUMENTO"

    def __str__(self):
        return self.FA_NID.FA_CNOMBRE + ' ' + self.TD_NID.TD_NOMBRE
    
class DOCUMENTO(models.Model):
    DOC_NID = models.BigAutoField(("ID"), primary_key=True)
    TD_NID = models.ForeignKey(TIPO_DOCUMENTO,verbose_name="Id Tipo Documento",on_delete=models.PROTECT,blank=True, null=True)
    DOC_NOMBRE = models.CharField(("Nombre"),max_length=128)
    DOC_CONTENIDO = models.FileField(upload_to='documentos/', blank=True, null=True)
    DOC_APROBADO = models.BooleanField(blank=True, null=True, default=None) 
    DOC_COMENTARIO = models.TextField(("Comentario de Revisión"), blank=True, null=True)
    DOC_FFECHACREACION = models.DateTimeField(auto_now_add=True)
    DOC_FECHA_MODIFICACION = models.DateTimeField(auto_now=True)
    DOC_ES_GUIA = models.BooleanField(default=False)
    
    class Meta:
        db_table = "DOCUMENTO"

    def __str__(self):
        return self.DOC_NOMBRE
 
#ESTAS TABLA SERA PARA CONECTAR LOS DOCUMENTOS CON LAS FASES
class FASE_DOCUMENTO(models.Model):
    FTD_NID = models.BigAutoField(("ID"), primary_key=True)
    # Usar CASCADE aquí es útil para que al borrar la fase, se borren los links a documentos
    FA_NID = models.ForeignKey(FASE_PROYECTO,verbose_name="Id Fase proyecto",on_delete=models.CASCADE)
    DOC_NID = models.ForeignKey(DOCUMENTO,verbose_name="Documento",on_delete=models.PROTECT)

    class Meta:
        db_table = "FASE_DOCUMENTO"

    def __str__(self):
        return self.FA_NID.FA_CNOMBRE + ' ' + self.DOC_NID.DOC_NOMBRE