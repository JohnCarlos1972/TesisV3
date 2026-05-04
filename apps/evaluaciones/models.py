from django.db import models
from apps.core.models import Asignatura, Periodo
from apps.actores.models import Docente, Alumno

class CriterioEvaluacion(models.Model):
    nombre_criterio = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2) # Ejemplo: 0.10 para el 10%
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_criterio} (Peso: {self.peso})"

class Evaluacion(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='evaluaciones')
    periodo = models.ForeignKey(Periodo, on_delete=models.SET_NULL, null=True, related_name='evaluaciones')
    # El alumno es quien funge como evaluador
    evaluador = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='evaluaciones_realizadas')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    
    fecha = models.DateField(auto_now_add=True)
    promedio_general = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observacion_general = models.TextField(null=True, blank=True)

    class Meta:
        # Restricción vital: Un alumno evalúa una sola vez a un docente por periodo
        unique_together = ('docente', 'periodo', 'evaluador')

    def __str__(self):
        nombre_periodo = self.periodo.nombre_periodo if self.periodo else 'Sin Periodo'
        return f"Evaluación de {self.docente.nombre} - {nombre_periodo}"

class DetalleEvaluacion(models.Model):
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='detalles')
    criterio = models.ForeignKey(CriterioEvaluacion, on_delete=models.CASCADE, related_name='detalles')
    puntaje = models.DecimalField(max_digits=5, decimal_places=2)
    observacion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Detalle {self.id} - {self.criterio.nombre_criterio}: {self.puntaje}"