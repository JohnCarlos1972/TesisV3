import random

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from apps.core.models import Institucion, Facultad, Carrera, Asignatura, Periodo
from apps.actores.models import CargaAcademica, Docente, Alumno
from apps.evaluaciones.models import CriterioEvaluacion, Evaluacion, DetalleEvaluacion


class Command(BaseCommand):
    help = 'Puebla la base de datos con información de prueba'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando la población de la base de datos...')

        # ==============================================
        # INSTITUCIONES
        # ==============================================
        institucion, _ = Institucion.objects.get_or_create(
            ruc='1760001230001',
            defaults={
                'nombre_institucion': 'Universidad Tecnológica de Innovación (UTI)',
                'direccion': 'Sede Central - Campus Norte',
                'estado': True
            }
        )
        self.stdout.write(f'✓ Institución creada: {institucion.nombre_institucion}')

        # ==============================================
        # FACULTADES
        # ==============================================
        nombres_facultades = [
            'Ingeniería', 'Ciencias Médicas', 'Derecho', 'Administración', 'Arquitectura',
            'Psicología', 'Artes', 'Educación', 'Comunicación', 'Economía',
            'Gastronomía', 'Turismo', 'Veterinaria', 'Agronomía', 'Idiomas',
            'Diseño', 'Música', 'Ciencias Químicas', 'Física', 'Filosofía'
        ]
        
        facultades = {}
        for nombre in nombres_facultades:
            facultad, _ = Facultad.objects.get_or_create(
                institucion=institucion,
                nombre_facultad=nombre
            )
            facultades[nombre] = facultad
        
        self.stdout.write(f'✓ {len(facultades)} facultades creadas')

        # ==============================================
        # CARRERAS
        # ==============================================
        carreras_data = [
            ('Software', 'Ingeniería'), ('Ciberseguridad', 'Ingeniería'),
            ('Enfermería', 'Ciencias Médicas'), ('Odontología', 'Ciencias Médicas'),
            ('Leyes', 'Derecho'), ('Marketing', 'Administración'),
            ('Contabilidad', 'Administración'), ('Urbanismo', 'Arquitectura'),
            ('Psicología Clínica', 'Psicología'), ('Pintura', 'Artes'),
            ('Docencia', 'Educación'), ('Periodismo', 'Comunicación'),
            ('Finanzas', 'Economía'), ('Artes Culinarias', 'Gastronomía'),
            ('Hotelería', 'Turismo'), ('Zootecnia', 'Veterinaria'),
            ('Suelos', 'Agronomía'), ('Inglés', 'Idiomas'),
            ('Diseño Gráfico', 'Diseño'), ('Telecomunicaciones', 'Ingeniería')
        ]
        
        carreras = {}
        for nombre_carrera, nombre_facultad in carreras_data:
            carrera, _ = Carrera.objects.get_or_create(
                institucion=institucion,
                facultad=facultades[nombre_facultad],
                nombre_carrera=nombre_carrera
            )
            carreras[nombre_carrera] = carrera
        
        self.stdout.write(f'✓ {len(carreras)} carreras creadas')

        # ==============================================
        # ASIGNATURAS
        # ==============================================
        asignaturas_data = [
            ('Software', 'Programación Java', 'SOFT01'),
            ('Software', 'Estructuras de Datos', 'SOFT02'),
            ('Ciberseguridad', 'Ethical Hacking', 'CIB01'),
            ('Enfermería', 'Primeros Auxilios', 'ENF01'),
            ('Leyes', 'Derecho Civil', 'DER01'),
            ('Marketing', 'Neuromarketing', 'MAR01'),
            ('Contabilidad', 'Costos I', 'CON01'),
            ('Urbanismo', 'Maquetación', 'ARQ01'),
            ('Psicología Clínica', 'Psicología Infantil', 'PSI01'),
            ('Pintura', 'Historia del Arte', 'ART01'),
            ('Docencia', 'Didáctica', 'EDU01'),
            ('Periodismo', 'Redacción', 'COM01'),
            ('Finanzas', 'Bolsa de Valores', 'ECO01'),
            ('Artes Culinarias', 'Cocina Nacional', 'GAS01'),
            ('Hotelería', 'Servicio al Cliente', 'TUR01'),
            ('Zootecnia', 'Nutrición Animal', 'VET01'),
            ('Suelos', 'Hidroponía', 'AGR01'),
            ('Inglés', 'Fonética', 'IDM01'),
            ('Diseño Gráfico', 'Ilustración Digital', 'DIS01'),
            ('Telecomunicaciones', 'Antenas', 'TEL01')
        ]
        
        asignaturas = {}
        for carrera_nombre, nombre_asignatura, codigo in asignaturas_data:
            asignatura, _ = Asignatura.objects.get_or_create(
                carrera=carreras[carrera_nombre],
                nombre_asignatura=nombre_asignatura,
                codigo_asignatura=codigo
            )
            asignaturas[codigo] = asignatura
        
        self.stdout.write(f'✓ {len(asignaturas)} asignaturas creadas')

        # ==============================================
        # PERIODOS ACADÉMICOS
        # ==============================================
        periodos_data = [
            ('2020-I', '2020-01-01', '2020-06-01'),
            ('2020-II', '2020-07-01', '2020-12-01'),
            ('2021-I', '2021-01-01', '2021-06-01'),
            ('2021-II', '2021-07-01', '2021-12-01'),
            ('2022-I', '2022-01-01', '2022-06-01'),
            ('2022-II', '2022-07-01', '2022-12-01'),
            ('2023-I', '2023-01-01', '2023-06-01'),
            ('2023-II', '2023-07-01', '2023-12-01'),
            ('2024-I', '2024-01-01', '2024-06-01'),
            ('2024-II', '2024-07-01', '2024-12-01'),
            ('2025-I', '2025-01-01', '2025-06-01'),
            ('2025-II', '2025-07-01', '2025-12-01'),
            ('2026-I', '2026-01-01', '2026-06-01'),
            ('2026-II', '2026-07-01', '2026-12-01'),
            ('Extendido 1', '2023-01-01', '2023-12-01'),
            ('Invierno', '2024-12-01', '2025-02-01'),
            ('Verano', '2024-06-01', '2024-08-01'),
            ('Nivelación A', '2025-01-01', '2025-03-01'),
            ('Maestría Cohorte 1', '2024-01-01', '2025-01-01'),
            ('Doctorado A', '2023-01-01', '2026-01-01')
        ]
        
        periodos = {}
        for nombre, fecha_ini, fecha_fin in periodos_data:
            periodo, _ = Periodo.objects.get_or_create(
                institucion=institucion,
                nombre_periodo=nombre,
                defaults={
                    'fecha_inicio': fecha_ini,
                    'fecha_fin': fecha_fin
                }
            )
            periodos[nombre] = periodo
        
        self.stdout.write(f'✓ {len(periodos)} períodos creados')

        # ==============================================
        # DOCENTES
        # ==============================================
        
        lista_carreras = list(carreras.values())
        lista_asignaturas = list(asignaturas.values())
        lista_facultades = list(facultades.values())
        
        docentes_data = [
            ('101', 'Carlos Ruiz', 'cruiz@uti.edu', '1980-05-12', 'Casado/a', 0, 0, 0),
            ('102', 'Elena Paz', 'epaz@uti.edu', '1985-03-22', 'Soltero/a', 0, 1, 2),
            ('103', 'Mario Sol', 'msol@uti.edu', '1978-09-30', 'Casado/a', 1, 2, 3),
            ('104', 'Ana Luz', 'aluz@uti.edu', '1982-11-15', 'Divorciado/a', 2, 4, 4),
            ('105', 'Pedro Gil', 'pgil@uti.edu', '1975-01-10', 'Casado/a', 3, 5, 5),
            ('106', 'Luis Mar', 'lmar@uti.edu', '1990-06-05', 'Soltero/a', 3, 6, 6),
            ('107', 'Rosa Flor', 'rflor@uti.edu', '1988-08-18', 'Casado/a', 4, 7, 7),
            ('108', 'Ines Bar', 'ibar@uti.edu', '1983-12-25', 'Soltero/a', 5, 8, 8),
            ('109', 'Raul Via', 'rvia@uti.edu', '1979-04-14', 'Viudo/a', 6, 9, 9),
            ('110', 'Sonia Rey', 'srey@uti.edu', '1981-10-20', 'Casado/a', 7, 10, 10),
            ('111', 'Hugo Oro', 'horo@uti.edu', '1986-07-07', 'Soltero/a', 8, 11, 11),
            ('112', 'Olga San', 'osan@uti.edu', '1972-02-28', 'Casado/a', 9, 12, 12),
            ('113', 'Ivan Ron', 'iron@uti.edu', '1987-05-19', 'Divorciado/a', 10, 13, 13),
            ('114', 'Nora Tan', 'ntan@uti.edu', '1984-03-03', 'Soltero/a', 11, 14, 14),
            ('115', 'Paco Man', 'pman@uti.edu', '1976-08-21', 'Casado/a', 12, 15, 15),
            ('116', 'Lola Pan', 'lpan@uti.edu', '1989-11-30', 'Soltero/a', 13, 16, 16),
            ('117', 'Vera Nil', 'vnil@uti.edu', '1980-01-01', 'Casado/a', 14, 17, 17),
            ('118', 'Beto Jil', 'bjil@uti.edu', '1992-04-12', 'Soltero/a', 15, 18, 18),
            ('119', 'Sara Pol', 'spol@uti.edu', '1983-09-09', 'Casado/a', 0, 19, 19),
            ('120', 'Dany Sol', 'dsol@uti.edu', '1991-10-10', 'Soltero/a', 0, 0, 1)
        ]
        
        docentes = {}
        for nic, nombre, email, fecha_nac, ec, idx_fac, idx_carr, idx_asig in docentes_data:
            docente, _ = Docente.objects.get_or_create(
                nic=nic,
                defaults={
                    'nombre': nombre,
                    'correo_electronico': email,
                    'fecha_nacimiento': fecha_nac,
                    'estado_civil': ec,
                    'institucion': institucion,
                    'facultad': lista_facultades[idx_fac],
                    'carrera': lista_carreras[idx_carr],
                    'asignatura': lista_asignaturas[idx_asig]
                }
            )
            docentes[nic] = docente
        
        self.stdout.write(f'✓ {len(docentes)} docentes creados')

        # ==============================================
        # ALUMNOS
        # ==============================================
        alumnos_data = [
            ('MAT-001', 'Juan Estudiante', 0),
            ('MAT-002', 'Maria Alumna', 0),
            ('MAT-003', 'Luis Aprendiz', 1),
            ('MAT-004', 'Ana Novata', 2),
            ('MAT-005', 'Pedro Tesista', 4),
            ('MAT-006', 'Jorge Becado', 5),
            ('MAT-007', 'Marta Delegada', 6),
            ('MAT-008', 'Elena Ayudante', 7),
            ('MAT-009', 'Raul Monitor', 8),
            ('MAT-010', 'Sonia C.', 9),
            ('MAT-011', 'Hugo B.', 10),
            ('MAT-012', 'Ines R.', 11),
            ('MAT-013', 'Ivan M.', 12),
            ('MAT-014', 'Nora F.', 13),
            ('MAT-015', 'Paco G.', 14),
            ('MAT-016', 'Lola H.', 15),
            ('MAT-017', 'Vera K.', 16),
            ('MAT-018', 'Beto L.', 17),
            ('MAT-019', 'Sara O.', 18),
            ('MAT-020', 'Dany P.', 19)
        ]
        
        alumnos = {}
        for matricula, nombre, idx_carrera in alumnos_data:
            alumno, _ = Alumno.objects.get_or_create(
                matricula=matricula,
                defaults={
                    'institucion': institucion,
                    'carrera': lista_carreras[idx_carrera],
                    'nombre_alumno': nombre,
                    'correo_electronico': f'{nombre.lower().replace(" ", ".")}@uti.edu'
                }
            )
            alumnos[matricula] = alumno
        
        self.stdout.write(f'✓ {len(alumnos)} alumnos creados')

        # ==============================================
        # CARGA ACADÉMICA
        # ==============================================
        periodo_referencia = periodos['2026-I']
        lista_alumnos = list(alumnos.values())
        lista_docentes = list(docentes.values())
        lista_asignaturas = list(asignaturas.values())
        
        cargas = []
        for alu in lista_alumnos:
            # Cada alumno toma 2 asignaturas aleatorias
            mats = random.sample(lista_asignaturas, 2)
            for mat in mats:
                # Seleccionamos un docente aleatorio
                doc = random.choice(lista_docentes)
                
                carga, _ = CargaAcademica.objects.get_or_create(
                    alumno=alu,
                    docente=doc,
                    asignatura=mat,
                    periodo=periodo_referencia.nombre_periodo # Ahora sí existe
                )
                cargas.append(carga)
        
        self.stdout.write(f'✓ {len(cargas)} registros de carga académica creados')

        # ==============================================
        # CRITERIOS DE EVALUACIÓN
        # ==============================================
        criterios_data = [
            ('Dominio Científico', 'Nivel de profundidad y actualización de los conocimientos técnicos.', '0.10'),
            ('Planificación Curricular', 'Capacidad para organizar los contenidos según el sílabo aprobado.', '0.05'),
            ('Metodología Activa', 'Uso de técnicas que fomentan la participación del estudiante.', '0.08'),
            ('Recursos Tecnológicos', 'Manejo de plataformas virtuales, simuladores y software especializado.', '0.05'),
            ('Puntualidad de Inicio', 'Cumplimiento del horario de inicio de las sesiones de clase.', '0.04'),
            ('Respeto y Ética', 'Trato profesional y empático hacia los estudiantes y colegas.', '0.05'),
            ('Claridad Expositiva', 'Habilidad para explicar conceptos complejos de forma sencilla.', '0.08'),
            ('Evaluación Continua', 'Implementación de rúbricas y procesos de retroalimentación oportunos.', '0.07'),
            ('Fomento a la Investigación', 'Motivación a los alumnos para realizar trabajos de indagación.', '0.05'),
            ('Gestión de Tutorías', 'Disponibilidad y calidad en el apoyo académico fuera de clase.', '0.05'),
            ('Innovación Pedagógica', 'Implementación de nuevas estrategias de enseñanza-aprendizaje.', '0.05'),
            ('Comunicación Asertiva', 'Capacidad de escucha y respuesta clara ante dudas estudiantiles.', '0.05'),
            ('Uso de Bibliografía', 'Promoción del uso de bases de datos científicas y libros actualizados.', '0.04'),
            ('Cumplimiento Administrativo', 'Entrega de actas, notas e informes en los plazos institucionales.', '0.05'),
            ('Liderazgo en el Aula', 'Capacidad para gestionar el grupo y resolver conflictos internos.', '0.05'),
            ('Vinculación Práctica', 'Relación de la teoría con casos reales del campo profesional.', '0.05'),
            ('Fomento al Debate', 'Generación de espacios de pensamiento crítico y opinión.', '0.04'),
            ('Evaluación Justa', 'Coherencia entre lo enseñado y la dificultad de los exámenes.', '0.05'),
            ('Actualización Profesional', 'Participación demostrada en cursos de formación docente.', '0.03'),
            ('Vocación de Servicio', 'Compromiso con el éxito académico y profesional del alumno.', '0.02')
        ]
        
        criterios = []
        for nombre, desc, peso in criterios_data:
            criterio, _ = CriterioEvaluacion.objects.get_or_create(
                nombre_criterio=nombre,
                defaults={
                    'descripcion': desc,
                    'peso': Decimal(peso),
                    'estado': True
                }
            )
            criterios.append(criterio)
        
        self.stdout.write(f'✓ {len(criterios)} criterios de evaluación creados')

        # ==============================================
        # EVALUACIONES
        # ==============================================
        
        periodo_referencia = periodos['2026-I']
        
        evaluaciones_data = [
            (1, 9.50, 'Excelente docente, sus clases de Java son muy prácticas y claras.'),
            (2, 8.80, 'Explica muy bien los conceptos de red, aunque a veces falta tiempo.'),
            (3, 7.50, 'El dominio de la materia es alto, pero la metodología es algo monótona.'),
            (4, 9.20, 'Muy puntual y siempre está dispuesta a resolver dudas individuales.'),
            (5, 8.20, 'Las clases son interesantes, pero el material didáctico podría mejorar.'),
            (6, 9.80, 'Involucra mucho a los estudiantes en debates actuales de la carrera.'),
            (7, 7.00, 'Sus exámenes son mucho más difíciles que lo explicado en clase.'),
            (8, 8.50, 'Usa muy bien el aula virtual y sube las notas siempre a tiempo.'),
            (9, 9.10, 'Se nota su experiencia profesional en los ejemplos que nos da.'),
            (10, 8.90, 'Promueve mucho el trabajo en equipo y el liderazgo en el aula.'),
            (11, 9.30, 'Excelente trato humano y profesional, muy respetuoso.'),
            (12, 7.90, 'Las clases son teóricas, faltaría un poco más de aplicación real.'),
            (13, 8.40, 'Organiza muy bien el tiempo de la clase para cubrir todo el sílabo.'),
            (14, 9.60, 'Innova mucho con herramientas digitales nuevas cada semana.'),
            (15, 8.10, 'Maneja muy bien el grupo, aunque las tutorías son en horarios difíciles.'),
            (16, 8.70, 'Sus explicaciones son claras y siempre recomienda libros actualizados.'),
            (17, 9.40, 'Muestra mucha vocación y paciencia con los alumnos que tienen dudas.'),
            (18, 7.20, 'Llega un poco tarde a veces, pero recupera el tiempo con buena clase.'),
            (19, 8.60, 'Fomenta el pensamiento crítico y no solo la memorización de conceptos.'),
            (20, 9.90, 'El mejor profesor del ciclo, domina la materia de forma excepcional.')
        ]
        
        lista_docentes = list(docentes.values())
        lista_alumnos = list(alumnos.values())
        
        evaluaciones = []
        for i, (docente_idx, promedio, observacion) in enumerate(evaluaciones_data):
            # Obtener objetos relacionados para esta iteración
            docente_obj = lista_docentes[docente_idx - 1]
            alumno_obj = lista_alumnos[i]
            asignatura_obj = docente_obj.asignatura # Usamos la asignatura que el docente tiene asignada

            # CREAR CARGA ACADÉMICA
            CargaAcademica.objects.get_or_create(
                alumno=alumno_obj,
                docente=docente_obj,
                asignatura=asignatura_obj,
                periodo=periodo_referencia.nombre_periodo
            )

            # CREAR EVALUACIÓN
            evaluacion, created = Evaluacion.objects.get_or_create(
                docente=docente_obj,
                periodo=periodo_referencia,
                evaluador=alumno_obj,
                asignatura=asignatura_obj, 
                defaults={
                    'promedio_general': Decimal(str(promedio)),
                    'observacion_general': observacion
                }
            )
            evaluaciones.append(evaluacion)
            
            # Solo crear detalles para la primera evaluación
            if created and i == 0:
                detalles_puntajes = [
                    10.00, 9.00, 9.50, 10.00, 8.50, 10.00, 9.50, 9.00, 8.00, 10.00,
                    9.50, 9.00, 10.00, 10.00, 9.00, 9.50, 9.00, 10.00, 8.50, 10.00
                ]
                observaciones_detalle = [
                    'Demuestra un conocimiento profundo de Java y Spring Boot.',
                    'El sílabo se sigue con mucha precisión semana a semana.',
                    'Utiliza ejercicios prácticos que facilitan el aprendizaje.',
                    'El uso del repositorio GitHub para la clase es excelente.',
                    'Generalmente puntual, solo hubo un retraso por tráfico.',
                    'Trato muy cordial y profesional con todos los compañeros.',
                    'Explica los algoritmos de búsqueda de forma muy sencilla.',
                    'Las rúbricas de los proyectos son claras desde el inicio.',
                    'Nos motiva a leer artículos de Medium y StackOverflow.',
                    'Atendió mis dudas en la tutoría del jueves de forma clara.',
                    'Implementó juegos de lógica para aprender estructuras.',
                    'Responde los correos electrónicos en menos de 24 horas.',
                    'La bibliografía de la biblioteca virtual es muy acertada.',
                    'Subió las notas del primer parcial al sistema de inmediato.',
                    'Maneja el orden del aula sin ser autoritario.',
                    'Siempre relaciona el código con problemas reales de empresas.',
                    'Genera debates interesantes sobre ética en la IA.',
                    'La dificultad del examen fue acorde a lo avanzado en clase.',
                    'Se nota que toma cursos constantes de nuevas tecnologías.',
                    'Se nota que le apasiona enseñar programación.'
                ]
                
                for j, criterio in enumerate(criterios):
                    DetalleEvaluacion.objects.create(
                        evaluacion=evaluacion,
                        criterio=criterio,
                        puntaje=Decimal(str(detalles_puntajes[j])),
                        observacion=observaciones_detalle[j]
                    )
                self.stdout.write(f'  → Creados {len(criterios)} detalles para evaluación #{i+1}')
        
        self.stdout.write(f'✓ {len(evaluaciones)} evaluaciones creadas')

        # ==============================================
        # RESUMEN FINAL
        # ==============================================
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('¡BASE DE DATOS POBLADA EXITOSAMENTE!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Resumen de datos creados:')
        self.stdout.write(f'   • 1 Institución')
        self.stdout.write(f'   • {len(facultades)} Facultades')
        self.stdout.write(f'   • {len(carreras)} Carreras')
        self.stdout.write(f'   • {len(asignaturas)} Asignaturas')
        self.stdout.write(f'   • {len(periodos)} Períodos académicos')
        self.stdout.write(f'   • {len(docentes)} Docentes')
        self.stdout.write(f'   • {len(alumnos)} Alumnos')
        self.stdout.write(f'   • {len(cargas)} CargaAcademica')
        self.stdout.write(f'   • {len(criterios)} Criterios de evaluación')
        self.stdout.write(f'   • {len(evaluaciones)} Evaluaciones')
        self.stdout.write(self.style.SUCCESS('='*60))