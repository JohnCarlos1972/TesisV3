from django.http import FileResponse
from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework import status
from apps.actores.models import Docente
from apps.core.models import Periodo
from apps.evaluaciones.models import Evaluacion
from .services import generar_pdf_reporte_final, procesar_evaluacion_y_generar_necesidades, generar_plan_con_ia_gemini
from .models import NecesidadCapacitacion
from django.views.generic import ListView
from .models import PlanCapacitacion
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, redirect


class GenerarPlanIAView(APIView):
    """
    Endpoint para procesar una evaluación docente, calcular sus brechas
    y generar un plan de capacitación usando Azure OpenAI.
    """
    def post(self, request, evaluacion_id):
        # Buscamos la evaluación
        try:
            evaluacion = Evaluacion.objects.get(id=evaluacion_id)
        except Evaluacion.DoesNotExist:
            return Response(
                {"error": "Evaluación no encontrada."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Ejecutamos la regla de negocio: Generar necesidades
        necesidades = procesar_evaluacion_y_generar_necesidades(evaluacion.id)

        if not necesidades:
            return Response(
                {"mensaje": "El docente no presenta necesidades formativas críticas (puntajes menores a 6)."}, 
                status=status.HTTP_200_OK
            )

        # Invocamos a la IA con las necesidades detectadas
        plan = generar_plan_con_ia_gemini(evaluacion, necesidades)

        if plan:
            return Response({
                "mensaje": "Plan generado exitosamente.",
                "plan_id": plan.id,
                "docente": evaluacion.docente.nombre,
                "diagnostico_ia": plan.diagnostico_ia,
                "recomendacion_ia": plan.recomendacion_ia,
                "cursos_sugeridos": plan.cursos_sugeridos
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Hubo un problema al generar el plan con IA. Revisa los logs o tu API Key."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MatrizNecesidadesView(ListView):
    model = NecesidadCapacitacion
    template_name = 'capacitaciones/matriz_necesidades.html'
    context_object_name = 'necesidades'

    def get_queryset(self):
        # Capturamos ambos filtros de la URL
        periodo_id = self.request.GET.get('periodo')
        docente_id = self.request.GET.get('docente')
        
        queryset = NecesidadCapacitacion.objects.select_related('docente', 'criterio').order_by('-prioridad')

        # Filtro por Periodo
        if periodo_id and periodo_id.isdigit():
            docentes_ids = Evaluacion.objects.filter(periodo_id=periodo_id).values_list('docente_id', flat=True)
            queryset = queryset.filter(docente_id__in=docentes_ids)
        
        # Filtro por Docente
        if docente_id and docente_id.isdigit():
            queryset = queryset.filter(docente_id=docente_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Enviamos listas para los selects
        context['periodos'] = Periodo.objects.all().order_by('-fecha_inicio')
        context['docentes'] = Docente.objects.all().order_by('nombre') # Para el nuevo filtro
        
        # Mantener valores seleccionados en el frontend
        periodo_id = self.request.GET.get('periodo')
        docente_id = self.request.GET.get('docente')
        context['periodo_seleccionado'] = int(periodo_id) if periodo_id and periodo_id.isdigit() else None
        context['docente_seleccionado'] = int(docente_id) if docente_id and docente_id.isdigit() else None

        # Mapeo de periodos
        evaluaciones = Evaluacion.objects.select_related('periodo').all()
        periodo_map = {ev.docente_id: ev.periodo.nombre_periodo for ev in evaluaciones}
        
        for necesidad in context['necesidades']:
            necesidad.periodo_nombre = periodo_map.get(necesidad.docente_id, "N/A")
            
        return context
    


class PlanDetalleView(DetailView):
    model = PlanCapacitacion
    template_name = 'capacitaciones/plan_detalle.html'
    context_object_name = 'plan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        docente = self.object.docente
        
        # Buscar la última evaluación del docente
        ultima_evaluacion = Evaluacion.objects.filter(docente=docente).order_by('-fecha').first()
        
        context['es_avanzada'] = False
        context['es_intensivo'] = False

        if ultima_evaluacion:
            # Regla 1: Promedio mayor a 8.5
            if ultima_evaluacion.promedio_general > 8.5:
                context['es_avanzada'] = True
            
            # Regla 2: 3 o más necesidades críticas
            necesidades = NecesidadCapacitacion.objects.filter(docente=docente, estado='Pendiente')
            if necesidades.count() >= 3:
                context['es_intensivo'] = True

            context['promedio_docente'] = ultima_evaluacion.promedio_general or 0
                
        return context

    def post(self, request, *args, **kwargs):
        plan = self.get_object()
        accion = request.POST.get('accion')
        if accion == 'aprobar':
            plan.estado_aprobacion = 'Aprobado'
        elif accion == 'rechazar':
            plan.estado_aprobacion = 'Rechazado'
        plan.save()
        return self.get(request, *args, **kwargs)
    
class ListaReportesView(ListView):
    model = PlanCapacitacion
    template_name = 'capacitaciones/reporte_list.html'
    context_object_name = 'planes'
    
    def get_queryset(self):
        # Parámetros de filtro
        periodo_id = self.request.GET.get('periodo')
        docente_id = self.request.GET.get('docente')
        
        # Queryset base (Solo Aprobados)
        queryset = PlanCapacitacion.objects.filter(
            estado_aprobacion='Aprobado'
        ).select_related('docente', 'docente__carrera').order_by('-fecha_generacion')

        # Filtro por Periodo
        if periodo_id and periodo_id.isdigit():
            docentes_con_evaluacion = Evaluacion.objects.filter(
                periodo_id=periodo_id
            ).values_list('docente_id', flat=True)
            queryset = queryset.filter(docente_id__in=docentes_con_evaluacion)
        
        # Filtro por Docente
        if docente_id and docente_id.isdigit():
            queryset = queryset.filter(docente_id=docente_id)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Datos para los selectores
        context['periodos'] = Periodo.objects.all().order_by('-fecha_inicio')
        context['docentes'] = Docente.objects.all().order_by('nombre')
        
        # Mantenemos los filtros seleccionados
        periodo_id = self.request.GET.get('periodo')
        docente_id = self.request.GET.get('docente')
        context['periodo_seleccionado'] = int(periodo_id) if periodo_id and periodo_id.isdigit() else None
        context['docente_seleccionado'] = int(docente_id) if docente_id and docente_id.isdigit() else None

        # Lógica para mostrar el periodo en la tabla
        # Buscamos todas las evaluaciones para saber a qué periodo pertenece el diagnóstico del docente
        evaluaciones = Evaluacion.objects.select_related('periodo').all()
        periodo_map = {ev.docente_id: ev.periodo.nombre_periodo for ev in evaluaciones}
        
        for plan in context['planes']:
            # Inyectamos el nombre del periodo manualmente en el objeto
            plan.periodo_nombre = periodo_map.get(plan.docente_id, "N/A")

        return context
        
  
class PlanCapacitacionListView(ListView):
    model = PlanCapacitacion
    template_name = 'capacitaciones/lista_recomendaciones.html'
    context_object_name = 'planes'

    def get_queryset(self):
        periodo_id = self.request.GET.get('periodo')
        docente_id = self.request.GET.get('docente')
        order_by = self.request.GET.get('order_by', '-fecha_generacion')
        
        queryset = PlanCapacitacion.objects.select_related('docente').all()

        # Filtro por Periodo
        if periodo_id and periodo_id.isdigit():
            docentes_con_evaluacion = Evaluacion.objects.filter(
                periodo_id=periodo_id
            ).values_list('docente_id', flat=True)
            queryset = queryset.filter(docente_id__in=docentes_con_evaluacion)
        
        # Filtro por Docente
        if docente_id and docente_id.isdigit():
            queryset = queryset.filter(docente_id=docente_id)
        
        # Lógica de Ordenamiento
        if order_by == 'docente':
            queryset = queryset.order_by('docente__nombre', 'docente__nombre')
        elif order_by == '-docente':
            queryset = queryset.order_by('-docente__nombre', '-docente__nombre')
        elif order_by == 'fecha':
            queryset = queryset.order_by('fecha_generacion')
        else:
            queryset = queryset.order_by('-fecha_generacion') # El default es -fecha

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['periodos'] = Periodo.objects.all().order_by('-fecha_inicio')
        context['docentes'] = Docente.objects.all().order_by('nombre')
        context['current_order'] = self.request.GET.get('order_by', '-fecha')

        periodo_id = self.request.GET.get('periodo')
        docente_id = self.request.GET.get('docente')
        context['periodo_seleccionado'] = int(periodo_id) if periodo_id and periodo_id.isdigit() else None
        context['docente_seleccionado'] = int(docente_id) if docente_id and docente_id.isdigit() else None
        
        # Inyectar nombre del periodo
        evaluaciones = Evaluacion.objects.select_related('periodo').all()
        periodo_map = {ev.docente_id: ev.periodo.nombre_periodo for ev in evaluaciones}
        
        for plan in context['planes']:
            plan.periodo_nombre = periodo_map.get(plan.docente_id, "N/A")

        return context
    
class CambiarEstadoPlanView(View):
    def post(self, request, pk, nuevo_estado):
        plan = get_object_or_404(PlanCapacitacion, pk=pk)
        
        # Cambiamos el estado
        if nuevo_estado in ['Aprobado', 'Rechazado', 'Pendiente']:
            plan.estado_aprobacion = nuevo_estado
            plan.save()
        
        # Capturamos los filtros actuales que vienen en el POST
        docente_id = request.POST.get('docente_filtro', '')
        periodo_id = request.POST.get('periodo_filtro', '')
        order_by = request.POST.get('order_by_filtro', '')
        
        # Construimos la URL de retorno con los filtros
        response = redirect('lista_recomendaciones')
        
        # Añadimos los parámetros a la URL de redirección
        params = []
        if docente_id: params.append(f"docente={docente_id}")
        if periodo_id: params.append(f"periodo={periodo_id}")
        if order_by: params.append(f"order_by={order_by}")
        
        if params:
            response['Location'] += "?" + "&".join(params)
            
        return response

def descargar_reporte_pdf(request, pk):
    plan = get_object_or_404(PlanCapacitacion, pk=pk)
    pdf_buffer = generar_pdf_reporte_final(plan)
    nombre_archivo = f"Reporte_{plan.docente.nic}_{plan.fecha_generacion}.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=nombre_archivo)