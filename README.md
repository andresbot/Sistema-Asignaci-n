# Sistema de asignación de salones

[![Django](https://img.shields.io/badge/Django-%3E%3D5.1%20%3C6.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/DRF-%3E%3D3.15%20%3C4.0-A30000?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-%3E%3D3.10-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-%5E19.0.0-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-%5E6.2.0-646CFF?logo=vite&logoColor=white)](https://vite.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-Local%20Dev-003B57?logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Supabase PostgreSQL](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com/)
[![Tests](https://img.shields.io/github/actions/workflow/status/LuisCPedraza/Sistema-Asignaci-n/ci.yml?branch=main&label=Tests)](https://github.com/LuisCPedraza/Sistema-Asignaci-n/actions/workflows/ci.yml)
[![Deploy](https://img.shields.io/badge/Deploy-Pendiente-lightgrey)](https://github.com/LuisCPedraza/Sistema-Asignaci-n/deployments)

Plataforma para gestionar la asignación de salones, horarios, grupos y recursos académicos, con una interfaz web para operación por roles.

## Documentación principal

- [docs/GUIA_INSTALACION.md](docs/GUIA_INSTALACION.md): instalación y ejecución local paso a paso.
- [docs/architecture.md](docs/architecture.md): arquitectura técnica y convenciones del stack.
- [docs/CONSTITUCION_RISE.md](docs/CONSTITUCION_RISE.md): simulación académica de constitución empresarial.
- [docs/PLAN_NEGOCIO_RISE.md](docs/PLAN_NEGOCIO_RISE.md): visión de negocio y metas estratégicas.

## Contexto del proyecto

Este proyecto nace para resolver el proceso de asignación académica de forma centralizada, trazable y con operación por roles.

El enfoque actual es definir una base técnica sólida mientras se termina de ajustar el detalle funcional final.

## Objetivo del proyecto

Centralizar y optimizar el proceso de asignación académica, permitiendo:

- control de usuarios por rol,
- registro y administración de recursos (grupos, profesores, salones),
- asignación automática y manual,
- detección de conflictos en tiempo real,
- trazabilidad y reportes para toma de decisiones.

## Roles del sistema

- Administrador
- Coordinador
- Docente
- Estudiante

> Nota: "Usuario" se usa solo como término general para referirse a cualquier persona que accede al sistema; no es un rol funcional independiente.

## Alcance funcional inicial

- Autenticación y acceso según rol.
- Gestión de usuarios y parámetros generales del sistema.
- Administración de grupos, profesores, salones y disponibilidades.
- Asignación de salones automática (por reglas) y manual (interfaz visual).
- Detección de conflictos, alertas y sugerencias de ajuste.
- Consulta de horarios por rol y reportes de utilización.
- Historial de cambios para trazabilidad operativa.

## Arquitectura técnica

Se usa **MVT en Django** con frontend desacoplado en React.

En este proyecto, MVT se aplica en modo **API-first**: Django concentra modelos, vistas y lógica de negocio; React renderiza la interfaz principal; y los templates de Django quedan disponibles para usos puntuales (admin, correos o paneles internos).

- `frontend/`: React + Vite (UI y experiencia de usuario).
- `backend/`: Django (API, reglas de negocio y seguridad).
- `infra/supabase/`: integración con Supabase.
- `docs/`: decisiones técnicas y documentación de arquitectura.

Flujo base:

1. React consume la API de Django.
2. Django aplica reglas de negocio y orquesta datos.
3. Supabase provee PostgreSQL administrado (y potencial de auth/storage/realtime).

## Estructura del repositorio

```text
.
|-- backend/
|   |-- apps/
|   |   `-- core/
|   |       |-- migrations/
|   |       |-- services/
|   |       |-- apps.py
|   |       |-- models.py
|   |       |-- urls.py
|   |       `-- views.py
|   |-- config/
|   |-- .env.example
|   |-- manage.py
|   `-- requirements.txt
|-- docs/
|   |-- architecture.md
|   |-- GUIA_INSTALACION.md
|   |-- CONSTITUCION_RISE.md
|   `-- PLAN_NEGOCIO_RISE.md
|-- frontend/
|   |-- src/
|   |   |-- App.jsx
|   |   |-- main.jsx
|   |   `-- styles.css
|   |-- .env.example
|   |-- index.html
|   |-- package.json
|   `-- vite.config.js
`-- infra/
    `-- supabase/
        `-- README.md
```

## Puesta en marcha local

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Variables de entorno principales

- `VITE_API_URL`: URL base del backend.
- `DJANGO_SECRET_KEY`: clave de seguridad de Django.
- `DJANGO_DEBUG`: modo de ejecución.
- `DJANGO_ALLOWED_HOSTS`: hosts permitidos por Django.
- `DATABASE_URL`: conexión a PostgreSQL de Supabase.
- `CORS_ALLOWED_ORIGINS`: orígenes permitidos para el frontend.
- `SUPABASE_URL`: URL del proyecto Supabase.
- `SUPABASE_KEY`: clave anon o service role según el caso.

## Documento complementario

Para más detalle técnico de arquitectura revisar: [docs/architecture.md](docs/architecture.md).
