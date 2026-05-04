from django.db import models

class Institucion(models.Model):
    nombre_institucion = models.CharField(max_length=150, unique=True)
    ruc = models.CharField(max_length=20, unique=True)
    direccion = models.TextField(blank=True, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_institucion

class Facultad(models.Model):
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE, related_name='facultades')
    nombre_facultad = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_facultad} - {self.institucion.nombre_institucion}"

class Carrera(models.Model):
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE, related_name='carreras')
    facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE, related_name='carreras')
    nombre_carrera = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_carrera

class Asignatura(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='asignaturas')
    nombre_asignatura = models.CharField(max_length=100)
    codigo_asignatura = models.CharField(max_length=20, unique=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.codigo_asignatura} - {self.nombre_asignatura}"

class Periodo(models.Model):
    institucion = models.ForeignKey(Institucion, on_delete=models.CASCADE, related_name='periodos')
    nombre_periodo = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_periodo