from django.urls import path
from .views import AlumnoCreateView, AlumnoListView, AlumnoUpdateView, DocenteListView, DocenteCreateView, DocenteUpdateView

urlpatterns = [
    # Rutas para Docentes
    path('docentes/', DocenteListView.as_view(), name='docente_list'),
    path('docentes/nuevo/', DocenteCreateView.as_view(), name='docente_create'),
    path('docentes/editar/<int:pk>/', DocenteUpdateView.as_view(), name='docente_update'),

    # Rutas para Alumnos
    path('alumnos/', AlumnoListView.as_view(), name='alumno_list'),
    path('alumnos/nuevo/', AlumnoCreateView.as_view(), name='alumno_create'),
    path('alumnos/editar/<int:pk>/', AlumnoUpdateView.as_view(), name='alumno_update'),
]