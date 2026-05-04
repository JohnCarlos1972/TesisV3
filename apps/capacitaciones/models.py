from django.db import models
from apps.actores.models import Docente
from apps.evaluaciones.models import CriterioEvaluacion

class NecesidadCapacitacion(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Plan', 'Asignada a un Plan'),
        ('Completada', 'Completada'),
    ]

    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='necesidades')
    criterio = models.ForeignKey(CriterioEvaluacion, on_delete=models.CASCADE, related_name='necesidades')
    
    # La brecha es la diferencia entre el puntaje ideal y el obtenido
    brecha = models.DecimalField(max_digits=5, decimal_places=2) 
    
    # Prioridad = Brecha * Peso del Criterio
    prioridad = models.DecimalField(max_digits=5, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    def __str__(self):
        return f"Necesidad: {self.docente.nombre} - {self.criterio.nombre_criterio} (Prioridad: {self.prioridad})"

class PlanCapacitacion(models.Model):
    ESTADO_APROBACION_CHOICES = [
        ('Borrador', 'Borrador'),
        ('Revisión', 'En Revisión'),
        ('Aprobado', 'Aprobado'),
        ('Rechazado', 'Rechazado'),
    ]

    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='planes_capacitacion')
    fecha_generacion = models.DateField(auto_now_add=True)
    
    # Campos que se llenarán con la respuesta de la API de IA
    diagnostico_ia = models.TextField(null=True, blank=True)
    recomendacion_ia = models.TextField(null=True, blank=True)
    cursos_sugeridos = models.TextField(null=True, blank=True)
    
    estado_aprobacion = models.CharField(max_length=20, choices=ESTADO_APROBACION_CHOICES, default='Borrador')

    def __str__(self):
        return f"Plan de {self.docente.nombre} - {self.fecha_generacion}"

class HistorialCapacitacion(models.Model):
    ESTADO_CURSO_CHOICES = [
        ('En Curso', 'En Curso'),
        ('Aprobado', 'Aprobado'),
        ('Reprobado', 'Reprobado'),
        ('Desertó', 'Desertó'),
    ]

    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='historial_cursos')
    curso = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CURSO_CHOICES, default='En Curso')
    resultado = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.curso} - {self.docente.nombre} ({self.estado})"