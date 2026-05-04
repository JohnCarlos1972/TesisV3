from django.db.models import Avg, Count
from apps.evaluaciones.models import Evaluacion, DetalleEvaluacion
from apps.capacitaciones.models import NecesidadCapacitacion

def obtener_metricas_por_carrera(carrera_id):
    """
    Calcula el promedio de evaluación de todos los docentes de una carrera.
    """
    return Evaluacion.objects.filter(docente__carrera_id=carrera_id).aggregate(
        promedio_carrera=Avg('promedio_general'),
        total_evaluaciones=Count('id')
    )

def obtener_ranking_necesidades():
    """
    Identifica cuáles son los criterios de evaluación donde los docentes
    tienen más debilidades (Ranking de necesidades).
    """
    return NecesidadCapacitacion.objects.values(
        'criterio__nombre_criterio'
    ).annotate(
        total_docentes_con_brecha=Count('docente'),
        prioridad_promedio=Avg('prioridad')
    ).order_by('-total_docentes_con_brecha')