from django.urls import path
from .views import CriterioCreateView, CriterioListView, CriterioUpdateView, EvaluacionesPendientesView, ReporteCarreraView, RankingNecesidadesView, RegistrarEvaluacionView, api_get_asignaturas_docente

urlpatterns = [
    path('api/reporte-carrera/<int:carrera_id>/', ReporteCarreraView.as_view(), name='reporte_carrera'),
    path('api/ranking-necesidades/', RankingNecesidadesView.as_view(), name='ranking_necesidades'),
    path('api/asignaturas-docente/<int:docente_id>/', api_get_asignaturas_docente, name='api_get_asignaturas_docente'),

    # Evaluaciones 
    path('nueva/', RegistrarEvaluacionView.as_view(), name='evaluacion_create'),
    path('nueva/<int:docente_id>/', RegistrarEvaluacionView.as_view(), name='evaluacion_create_with_id'),
    path('lista/', EvaluacionesPendientesView.as_view(), name='evaluacion_list'),

    # Gestión de Criterios
    path('criterios/', CriterioListView.as_view(), name='criterio_list'),
    path('criterios/nuevo/', CriterioCreateView.as_view(), name='criterio_create'),
    path('criterios/editar/<int:pk>/', CriterioUpdateView.as_view(), name='criterio_update'),
]