from django import forms
from .models import Evaluacion, CriterioEvaluacion, DetalleEvaluacion
from apps.actores.models import Docente, Alumno
from apps.core.models import Periodo

class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = Evaluacion
        fields = ['docente', 'asignatura', 'periodo', 'evaluador', 'observacion_general']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadimos clases de Bootstrap
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})