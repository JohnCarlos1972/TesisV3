from django.db import models
from apps.core.models import Institucion, Facultad, Carrera, Asignatura

class Docente(models.Model):
    # Opciones para el estado civil
    ESTADO_CIVIL_CHOICES = [
        ('Soltero/a', 'Soltero/a'),
        ('Casado/a', 'Casado/a'),
        ('Divorciado/a', 'Divorciado/a'),
        ('Viudo/a', 'Viudo/a'),
        ('Unión Libre', 'Unión Libre'),
    ]

    nic = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    correo_electronico = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    fecha_nacimiento = models.DateField()
    estado_civil = models.CharField(max_length=20, choices=ESTADO_CIVIL_CHOICES)

    # Relaciones con la app Core
    institucion = models.ForeignKey(Institucion, on_delete=models.SET_NULL, null=True, related_name='docentes')
    facultad = models.ForeignKey(Facultad, on_delete=models.SET_NULL, null=True, related_name='docentes')
    carrera = models.ForeignKey(Carrera, on_delete=models.SET_NULL, null=True, related_name='docentes')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.SET_NULL, null=True, related_name='docentes')

    fecha_ingreso = models.DateField(auto_now_add=True)
    fecha_salida = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.nic})"

class Alumno(models.Model):
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE, related_name='alumnos')
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='alumnos')
    matricula = models.CharField(max_length=20, unique=True)
    nombre_alumno = models.CharField(max_length=100)
    correo_electronico = models.EmailField(max_length=100, unique=True, null=True, blank=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_alumno} ({self.matricula})"

class Especialidad(models.Model):
    nombre_especialidad = models.CharField(max_length=100, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_especialidad

class DocenteEspecialidad(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='especialidades')
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='docentes')
    fecha_inicio = models.DateField()
    fecha_culmino = models.DateField()
    observacion = models.TextField(null=True, blank=True)

    class Meta:
        # Aseguramos que la llave primaria compuesta se respete como restricción única
        unique_together = ('docente', 'especialidad', 'fecha_inicio', 'fecha_culmino')

    def __str__(self):
        return f"{self.docente.nombre} - {self.especialidad.nombre_especialidad}"
    

class CargaAcademica(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name='cursos_inscritos')
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name='carga_alumnos')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    periodo = models.CharField(max_length=20) # Ejemplo: "2026-I"

    class Meta:
        unique_together = ('alumno', 'docente', 'asignatura', 'periodo')

    def __str__(self):
        return f"{self.alumno.nombre_alumno} con {self.docente.nombre} en {self.asignatura.nombre}"