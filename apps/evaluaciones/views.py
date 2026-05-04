from rest_framework.views import APIView
from rest_framework.response import Response

from apps.core.models import Asignatura, Periodo
from .services import obtener_metricas_por_carrera, obtener_ranking_necesidades
from django.shortcuts import render, redirect
from django.views import View
from .models import Evaluacion, DetalleEvaluacion, CriterioEvaluacion
from .forms import EvaluacionForm
from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.http import JsonResponse

class RegistrarEvaluacionView(View):
    template_name = 'evaluaciones/evaluacion_form.html'

    def get(self, request, docente_id=None):
        initial_data = {}
        form = EvaluacionForm()

        if docente_id:
            # Pre-cargamos el docente
            initial_data['docente'] = docente_id
            form = EvaluacionForm(initial=initial_data)
            
            # Buscamos qué asignaturas tiene este docente en su Carga Académica
            asignaturas_docente = Asignatura.objects.filter(
                cargaacademica__docente_id=docente_id
            ).distinct()
            
            # Aplicamos el filtro al campo del formulario
            form.fields['asignatura'].queryset = asignaturas_docente
        
        if not docente_id:
            form.fields['asignatura'].widget.attrs['disabled'] = True
            form.fields['asignatura'].help_text = "Seleccione un docente primero"
            
        criterios = CriterioEvaluacion.objects.filter(estado=True)
        return render(request, self.template_name, {
            'form': form, 
            'criterios': criterios,
            'docente_id': docente_id 
        })

    @transaction.atomic
    def post(self, request, docente_id=None):
        form = EvaluacionForm(request.POST)
        criterios = CriterioEvaluacion.objects.filter(estado=True)
        
        if form.is_valid():
            try:
                # Guardamos la evaluación base
                evaluacion = form.save(commit=False)
                
                # Procesamos los puntajes de cada criterio enviados desde el form
                total_puntaje = 0
                detalles_a_crear = []
                
                for criterio in criterios:
                    puntaje = request.POST.get(f'criterio_{criterio.id}')
                    if puntaje:
                        val_puntaje = float(puntaje)
                        total_puntaje += val_puntaje
                        detalles_a_crear.append(DetalleEvaluacion(
                            evaluacion=evaluacion,
                            criterio=criterio,
                            puntaje=val_puntaje
                        ))
                
                # Calcular el promedio general
                if criterios.count() > 0:
                    evaluacion.promedio_general = total_puntaje / criterios.count()
                
                evaluacion.save()
                
                # Guardamos todos los detalles en bloque
                DetalleEvaluacion.objects.bulk_create(detalles_a_crear)

                # Notificación de éxito
                messages.success(request, "¡Evaluación guardada correctamente!")
                
                return redirect('docente_list') # Redirigimos al listado si es exitoso
            
            except Exception as e:
                messages.error(request, f"Error al guardar: {str(e)}")
        else:
            # Manejo amigable de errores globales (como el duplicado)
            for error in form.non_field_errors():
                if "already exists" in str(error).lower():
                    messages.error(request, "Aviso: Este docente ya ha sido evaluado por este estudiante en el periodo seleccionado. No se permiten duplicados.")
                else:
                    messages.error(request, f"Nota: {error}")
            
            # Errores de campos específicos
            for field, errors in form.errors.items():
                if field != '__all__': 
                    nombre_campo = form.fields[field].label
                    for error in errors:
                        messages.error(request, f"Campo '{nombre_campo}': {error}")
            
        return render(request, self.template_name, {'form': form, 'criterios': criterios})

class ReporteCarreraView(APIView):
    def get(self, request, carrera_id):
        data = obtener_metricas_por_carrera(carrera_id)
        return Response(data)

class RankingNecesidadesView(APIView):
    """
    Módulo 5: Reporte de ranking de necesidades de capacitación.
    """
    def get(self, request):
        ranking = obtener_ranking_necesidades()
        return Response(ranking)
    
    
class EvaluacionesPendientesView(ListView):
    model = Evaluacion
    template_name = 'evaluaciones/evaluaciones_list.html'
    context_object_name = 'evaluaciones'
    
    def get_queryset(self):
        return Evaluacion.objects.all().order_by('-fecha')
    

class CriterioListView(ListView):
    model = CriterioEvaluacion
    template_name = 'evaluaciones/criterio_list.html'
    context_object_name = 'criterios'

class CriterioCreateView(CreateView):
    model = CriterioEvaluacion
    template_name = 'evaluaciones/criterio_form.html'
    fields = ['nombre_criterio', 'descripcion', 'peso', 'estado']
    success_url = reverse_lazy('criterio_list')

class CriterioUpdateView(UpdateView):
    model = CriterioEvaluacion
    template_name = 'evaluaciones/criterio_form.html'
    fields = ['nombre_criterio', 'descripcion', 'peso', 'estado']
    success_url = reverse_lazy('criterio_list')

class EvaluacionesConsolidadasView(ListView):
    model = Evaluacion
    template_name = 'evaluaciones/evaluaciones_list.html'
    context_object_name = 'evaluaciones_consolidadas'

    def get_queryset(self):
        # 1. Agrupamos por docente
        # 2. Calculamos el promedio de todos sus promedios
        # 3. Obtenemos la fecha de la última evaluación recibida
        # 4. Obtenemos el ID de una de sus evaluaciones para el botón de acción
        return Evaluacion.objects.values(
            'docente__id', 
            'docente__nombre_docente'
        ).annotate(
            promedio_grupal=Avg('promedio_general'),
            ultima_fecha=Max('fecha_creacion'),
            # Necesitamos un ID de evaluación para la ruta del Plan IA
            evaluacion_id=Max('id') 
        ).order_by('-promedio_grupal')
    

def api_get_asignaturas_docente(request, docente_id):
    # Obtenemos las asignaturas únicas ligadas a este docente en la carga académica
    asignaturas = Asignatura.objects.filter(
        cargaacademica__docente_id=docente_id
    ).distinct().values('id', 'nombre_asignatura')
    
    return JsonResponse(list(asignaturas), safe=False)
