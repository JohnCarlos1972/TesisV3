from django.contrib import admin
from .models import NecesidadCapacitacion, PlanCapacitacion

@admin.register(PlanCapacitacion)
class PlanCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('docente', 'fecha_generacion', 'estado_aprobacion')
    list_filter = ('estado_aprobacion',)
    readonly_fields = ('diagnostico_ia', 'recomendacion_ia', 'cursos_sugeridos')

@admin.register(NecesidadCapacitacion)
class NecesidadAdmin(admin.ModelAdmin):
    list_display = ('docente', 'criterio', 'prioridad', 'estado')