from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from .models import Alumno, Docente

# Listado de Docentes
class DocenteListView(ListView):
    model = Docente
    template_name = 'actores/docente_list.html'
    context_object_name = 'docentes'

# Crear Docente
class DocenteCreateView(CreateView):
    model = Docente
    template_name = 'actores/docente_form.html'
    # Campos que el usuario podrá llenar al registrar un docente
    fields = ['nic', 'nombre', 'correo_electronico', 'fecha_nacimiento', 'estado_civil', 
              'institucion', 'facultad', 'carrera', 'asignatura']
    success_url = reverse_lazy('docente_list')

# Editar Docente
class DocenteUpdateView(UpdateView):
    model = Docente
    template_name = 'actores/docente_form.html'
    fields = ['nic', 'nombre', 'correo_electronico', 'fecha_nacimiento', 'estado_civil', 
              'institucion', 'facultad', 'carrera', 'asignatura']
    success_url = reverse_lazy('docente_list')

# Listado de Alumnos
class AlumnoListView(ListView):
    model = Alumno
    template_name = 'actores/alumno_list.html'
    context_object_name = 'alumnos'

# Crear Alumno
class AlumnoCreateView(CreateView):
    model = Alumno
    template_name = 'actores/alumno_form.html'
    fields = ['carrera', 'matricula', 'nombre_alumno', 'correo_electronico', 'estado', 'institucion']
    success_url = reverse_lazy('alumno_list')

# Editar Alumno
class AlumnoUpdateView(UpdateView):
    model = Alumno
    template_name = 'actores/alumno_form.html'
    fields = ['matricula', 'nombre_alumno', 'correo_electronico', 'carrera', 'estado', 'institucion']
    success_url = reverse_lazy('alumno_list')