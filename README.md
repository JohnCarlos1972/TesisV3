# Proyecto Django API test

## Estructura del proyecto

```
proyecto/
├── configuracion/                # Configuración principal del proyecto
│   ├── settings.py               # Ajustes de BD, Apps e Integraciones (IA)
│   └── urls.py                   # Enrutador principal del sistema
├── apps/                         # Directorio de aplicaciones del negocio
│   ├── core/                     # Utilidades del Sistema
│   │   ├── models.py             # Definición de tablas de la BD
│   │   ├── views.py              # Definición del home
│   │   └── management/           # 
│   │       └── commands/         # Comandos / Scripts 
│   │           └── poblar_db.py  # Script para poblar la base de datos
│   ├── actores/                  # Módulo 1: Instituciones, Carreras, Docentes y Alumnos
│   │   ├── models.py             # Definición de tablas de la BD
│   │   ├── views.py              # Lógica de los CRUDs
│   │   └── urls.py               # Rutas de este módulo
│   ├── evaluaciones/             # Módulo 2: Criterios y Encuestas
│   │   ├── models.py             # Criterios, Pesos y Respuestas
│   │   ├── forms.py              # Lógica de validación y estructura de la encuesta
│   │   └── services.py           # Lógica de cálculo de resultados
│   └── capacitaciones/           # Módulo 3 y 4: Matriz e Inteligencia Artificial
│       ├── models.py             # Necesidades y Planes de Capacitación
│       ├── services.py           # Conexión con Gemini/Azure (Cerebro de la IA)
│       └── views.py              # Lógica de generación y aprobación de planes
├── templates/                    # Archivos HTML (Interfaz de Usuario)
│   ├── base.html                 # Estructura visual común (Navbar/Footer)
│   ├── actores/                  # Formularios y listados de docentes/alumnos
│   └── capacitaciones/           # Matriz de necesidades y visualización del Plan IA
├── env/                          # Entorno virtual
└── manage.py                     # Utilidad de comandos de Django
```



## Comandos para iniciar un proyecto desde cero

``` sh

# Crea el entorno virtual
python3 -m venv env

# Iniciar el entorno virtual
source env/bin/activate

# Instalar Django
pip install django

# Iniciar la estructura del proyecto
django-admin startproject configuracion .

# Instalar Django REST Framework
pip install djangorestframework

# Crea una app de ejemplo: 
python manage.py startapp peliculas apps/peliculas

# Detecta cambios en tus modelos y crea el archivo de instrucciones
python manage.py makemigrations evaluaciones

# Ejecuta esas instrucciones en la base de datos
python manage.py migrate

# Ejecuta el script para poblar la base de datos
python manage.py poblar_bd

# inicia el servidor de desarrollo local
python manage.py runserver
```

## Comandos para desplegar en Cloud Run

```bash
# Antes de ejecutar los comandos, cambiar el numero de version (v6) en los comandos

# Construye la imagen de Docker
docker build --no-cache -t django-app:v7 .

# Le agrega una etiqueta a la imagen de docker para poder subir a la nube
docker tag django-app:v7 us-central1-docker.pkg.dev/firm-pentameter-462919-t8/django-repo/django-app:v7

# Sube a la nube la imagen de Docker
docker push us-central1-docker.pkg.dev/firm-pentameter-462919-t8/django-repo/django-app:v7

# Despliega la imagen de Docker en Cloud Run
gcloud run deploy django-test-service   --image us-central1-docker.pkg.dev/firm-pentameter-462919-t8/django-repo/django-app:v7   --region us-central1   --allow-unauthenticated
```