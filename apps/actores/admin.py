from django.contrib import admin
from .models import Docente, Alumno, Especialidad

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('nic', 'nombre', 'correo_electronico', 'facultad', 'carrera')
    search_fields = ('nombre', 'nic')
    list_filter = ('facultad', 'carrera')

admin.site.register(Alumno)
admin.site.register(Especialidad)