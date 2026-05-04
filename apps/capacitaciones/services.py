import re

import google.generativeai as genai
from openai import AzureOpenAI
from django.conf import settings
from decimal import Decimal
from apps.evaluaciones.models import Evaluacion
from apps.capacitaciones.models import NecesidadCapacitacion, PlanCapacitacion
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def obtener_contexto_historico(docente, evaluacion_actual_id):
    # Buscamos la evaluación anterior a la actual
    penultima_evaluacion = Evaluacion.objects.filter(
        docente=docente
    ).exclude(
        id=evaluacion_actual_id
    ).order_by('-fecha').first() # El primero después de excluir la actual es la penúltima
    
    if penultima_evaluacion:
        return f"""
        CONTEXTO HISTÓRICO (Evaluación Anterior):
        - Fecha: {penultima_evaluacion.fecha}
        - Promedio Anterior: {penultima_evaluacion.promedio_general}
        """
    return "CONTEXTO HISTÓRICO: No existen evaluaciones previas para este docente."


def procesar_evaluacion_y_generar_necesidades(evaluacion_id):
    """
    Toma una evaluación, analiza sus detalles y genera las necesidades
    de capacitación basadas en las reglas de negocio del sistema.
    """
    try:
        evaluacion = Evaluacion.objects.get(id=evaluacion_id)
    except Evaluacion.DoesNotExist:
        return []

    detalles = evaluacion.detalles.all()
    necesidades_generadas = []

    for detalle in detalles:
        # Regla 1: Si un criterio es menor a 6/10, se marca como necesidad formativa 
        if detalle.puntaje < Decimal('6.00'):
            # Regla 2: Calcular brecha (Puntaje ideal de 10 menos el puntaje obtenido) 
            brecha = Decimal('10.00') - detalle.puntaje
            
            # Regla 3: Prioridad = Puntaje de brecha × Peso del criterio 
            prioridad = brecha * detalle.criterio.peso

            # Creamos o actualizamos la necesidad para este docente y criterio
            necesidad, created = NecesidadCapacitacion.objects.update_or_create(
                docente=evaluacion.docente,
                criterio=detalle.criterio,
                defaults={
                    'brecha': brecha,
                    'prioridad': prioridad,
                    'estado': 'Pendiente'
                }
            )
            necesidades_generadas.append(necesidad)
            
    return necesidades_generadas



def generar_plan_con_ia_azure(evaluacion, necesidades):
    """
    Usa Azure OpenAI para analizar evaluación y generar plan aplicando reglas de negocio.
    """
    docente = evaluacion.docente
    promedio = evaluacion.promedio_general
    cantidad_necesidades = len(necesidades) if necesidades else 0

    # EVALUAMOS LAS REGLAS DE NEGOCIO
    reglas_negocio_prompt = ""
    
    if promedio > 8.5:
        reglas_negocio_prompt += (
            "REGLA DE EXCELENCIA: Promedio sobresaliente de "
            f"{promedio}/10. Omitir cursos básicos. Sugerir formación AVANZADA y liderazgo.\n"
        )
        
    if cantidad_necesidades >= 3:
        reglas_negocio_prompt += (
            "REGLA DE PLAN INTENSIVO: Múltiples áreas críticas "
            f"({cantidad_necesidades}). Estructurar plan a corto plazo (1-3 meses).\n"
        )

    try:
        client = AzureOpenAI(
            api_key=getattr(settings, 'AZURE_OPENAI_KEY', ''),
            api_version="2023-05-15", 
            azure_endpoint=getattr(settings, 'AZURE_OPENAI_ENDPOINT', '')
        )
        deployment_name = getattr(settings, 'AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-35-turbo')
    except Exception as e:
        print(f"Error al configurar Azure OpenAI: {e}")
        return None

    texto_necesidades = "\n".join(
        [f"- {n.criterio.nombre_criterio}: Puntaje {(10 - n.brecha):.2f}/10 (Brecha: {n.brecha:.2f})" 
         for n in necesidades]
    ) if necesidades else "Ninguna debilidad crítica."

    # Inyectamos las reglas en el mensaje del sistema para Azure
    mensajes = [
        {"role": "system", "content": f"Eres un coordinador académico experto analizando evaluaciones docentes. {reglas_negocio_prompt}"},
        {"role": "user", "content": f"""
        Analiza el siguiente resumen de desempeño del docente {docente.nombre}.
        
        Entrada de resultados (Áreas críticas detectadas):
        {texto_necesidades}
        
        Genera una respuesta estructurada con los siguientes 3 apartados exactamente:
        
        DIAGNÓSTICO:
        (Breve diagnóstico del docente)
        
        RECOMENDACIÓN:
        (Observaciones pedagógicas y qué priorizar)
        
        CURSOS SUGERIDOS:
        (Lista 3 cursos o talleres específicos)
        """}
    ]

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=mensajes,
            temperature=0.7,
            max_tokens=800
        )
        texto_ia = response.choices[0].message.content
        
        diagnostico, recomendacion, cursos = "", "", ""
        if "DIAGNÓSTICO:" in texto_ia:
            partes = texto_ia.split("RECOMENDACIÓN:")
            diagnostico = partes[0].replace("DIAGNÓSTICO:", "").strip()
            if len(partes) > 1:
                subpartes = partes[1].split("CURSOS SUGERIDOS:")
                recomendacion = subpartes[0].strip()
                if len(subpartes) > 1:
                    cursos = subpartes[1].strip()

        plan = PlanCapacitacion.objects.create(
            docente=docente,
            diagnostico_ia=diagnostico,
            recomendacion_ia=recomendacion,
            cursos_sugeridos=cursos,
            estado_aprobacion='Borrador'
        )
        return plan

    except Exception as e:
        print(f"Error al conectar con Azure OpenAI: {e}")
        return None


def generar_plan_con_ia_gemini(evaluacion, necesidades):
    """
    Usa Gemini para analizar evaluación y generar plan aplicando reglas de negocio.
    """
    docente = evaluacion.docente
    promedio = evaluacion.promedio_general
    asignatura = evaluacion.asignatura.nombre_asignatura
    contexto_historico = obtener_contexto_historico(docente, evaluacion.id)
    cantidad_necesidades = len(necesidades) if necesidades else 0

    # EVALUAMOS LAS REGLAS DE NEGOCIO
    reglas_negocio_prompt = ""
    
    if promedio > 8.5:
        reglas_negocio_prompt += (
            "REGLA DE EXCELENCIA APLICADA: El docente tiene un promedio sobresaliente "
            f"({promedio}/10). Por favor, omite cursos básicos. Enfoca la RECOMENDACIÓN "
            "y los CURSOS SUGERIDOS en formación AVANZADA, liderazgo académico, "
            "investigación o programas para convertirse en mentor de otros docentes.\n\n"
        )
        
    if cantidad_necesidades >= 3:
        reglas_negocio_prompt += (
            "REGLA DE PLAN INTENSIVO APLICADA: El docente presenta múltiples áreas "
            f"críticas ({cantidad_necesidades} debilidades detectadas). Estructura el plan "
            "como un 'Plan Intensivo de Recuperación Pedagógica' con acciones a corto "
            "plazo (1 a 3 meses) y seguimiento estricto.\n\n"
        )

    # Configuramos la API de Gemini
    genai.configure(api_key=getattr(settings, 'GEMINI_API_KEY', ''))
    model = genai.GenerativeModel('gemini-2.5-flash')

    texto_necesidades_actuales = "\n".join(
        [f"- {n.criterio.nombre_criterio}: Puntaje {(10 - n.brecha):.2f}/10 (Brecha: {n.brecha:.2f})" 
        for n in necesidades]
    ) if necesidades else "No presenta debilidades críticas."

    # Inyectamos las reglas en el prompt
    prompt = f"""
    Analiza el desempeño de {docente.nombre} en la cátedra de {asignatura} considerando su evolución:

    {contexto_historico}

    CONTEXTO:
    - Materia: {asignatura}
    - Promedio Actual: {evaluacion.promedio_general}

    EVALUACIÓN ACTUAL:
    {texto_necesidades_actuales}

    ESTRICTAMENTE DEBES SEGUIR ESTE FORMATO DE EJEMPLO:

    DIAGNÓSTICO:
    El docente presenta debilidades en X y Y áreas...

    RECOMENDACIÓN:
    Se sugiere fortalecer la metodología Z...

    CURSOS SUGERIDOS:
    - Taller de pedagogía avanzada
    - Diplomado en TIC
    - Seminario de ética

    INSTRUCCIÓN: Si el promedio actual es menor al anterior, la recomendación debe ser de carácter 'Urgente/Recuperativo'. 
    Si hay mejora, felicita el progreso pero identifica qué falta para la excelencia.

    INSTRUCCIÓN FINAL: No incluyas saludos, introducciones ni conclusiones. Empieza directamente con la palabra 'DIAGNÓSTICO:'.
    """

    try:
        response = model.generate_content(prompt)
        texto_ia = response.text
        
        diagnostico, recomendacion, cursos = "", "", ""
        diagnostico_match = re.search(r'DIAGNÓSTICO:(.*?)(?=RECOMENDACIÓN:|CURSOS SUGERIDOS:|$)', texto_ia, re.S | re.I)
        recomendacion_match = re.search(r'RECOMENDACIÓN:(.*?)(?=CURSOS SUGERIDOS:|$)', texto_ia, re.S | re.I)
        cursos_match = re.search(r'CURSOS SUGERIDOS:(.*?)$', texto_ia, re.S | re.I)

        diagnostico = diagnostico_match.group(1).strip() if diagnostico_match else texto_ia
        recomendacion = recomendacion_match.group(1).strip() if recomendacion_match else "Revisar diagnóstico para recomendaciones."
        cursos = cursos_match.group(1).strip() if cursos_match else "Consultar con coordinación académica."

        # Si después de intentar separar, los campos quedaron vacíos, usamos el texto completo
        if not recomendacion or recomendacion == "":
            recomendacion = "Ver detalles en el diagnóstico superior."

        # Limpiar asteriscos de las respuestas
        diagnostico = diagnostico.replace("*", "")
        recomendacion = recomendacion.replace("*", "")
        cursos = cursos.replace("*", "")

        plan = PlanCapacitacion.objects.create(
            docente=docente,
            diagnostico_ia=diagnostico,
            recomendacion_ia=recomendacion,
            cursos_sugeridos=cursos,
            estado_aprobacion='Borrador'
        )
        return plan

    except Exception as e:
        print(f"Error al conectar con la API de Gemini: {e}")
        return None

def generar_pdf_reporte_final(plan):
    """Genera un archivo PDF con el plan de capacitación aprobado."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Estilos personalizados
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], alignment=1, spaceAfter=20)
    section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], color=colors.navy, spaceBefore=15)

    # Contenido del PDF basándonos en el documento ejecutivo
    story.append(Paragraph("REPORTE EJECUTIVO DE CAPACITACIÓN DOCENTE", title_style))
    story.append(Paragraph(f"Institución: Universidad Tecnológica de Innovación (UTI)", styles['Normal']))
    story.append(Spacer(1, 12))

    # Información del Docente
    datos_docente = [
        ["Docente:", plan.docente.nombre],
        ["Carrera:", plan.docente.carrera.nombre_carrera],
        ["Facultad:", plan.docente.facultad.nombre_facultad],
        ["Fecha de Emisión:", plan.fecha_generacion.strftime('%d/%m/%Y')]
    ]
    t = Table(datos_docente, colWidths=[100, 350])
    t.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke)]))
    story.append(t)

    # Diagnóstico de la IA 
    story.append(Paragraph("1. Diagnóstico de Desempeño (IA)", section_style))
    story.append(Paragraph(plan.diagnostico_ia or "No disponible", styles['Normal']))

    # Recomendaciones
    story.append(Paragraph("2. Recomendaciones Pedagógicas", section_style))
    story.append(Paragraph(plan.recomendacion_ia or "No disponible", styles['Normal']))

    # Plan de Cursos
    story.append(Paragraph("3. Cursos Sugeridos", section_style))
    story.append(Paragraph(plan.cursos_sugeridos or "No disponible", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer


