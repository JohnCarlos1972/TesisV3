from django.urls import path
from .views import CambiarEstadoPlanView, GenerarPlanIAView, ListaReportesView, MatrizNecesidadesView, PlanDetalleView, PlanCapacitacionListView, descargar_reporte_pdf

urlpatterns = [
    # Frontend: Matriz de necesidades
    path('matriz/', MatrizNecesidadesView.as_view(), name='matriz_necesidades'),
    path('plan/<int:pk>/', PlanDetalleView.as_view(), name='plan_detalle'),
    path('reportes/', ListaReportesView.as_view(), name='lista_reportes'),
    path('reporte-pdf/<int:pk>/', descargar_reporte_pdf, name='descargar_pdf'),
    path('recomendaciones/', PlanCapacitacionListView.as_view(), name='lista_recomendaciones'),
    path('recomendaciones/cambiar-estado/<int:pk>/<str:nuevo_estado>/', CambiarEstadoPlanView.as_view(), name='cambiar_estado_plan'),
    
    # API: Lógica de IA
    path('api/generar-plan/<int:evaluacion_id>/', GenerarPlanIAView.as_view(), name='generar_plan_ia'),
]