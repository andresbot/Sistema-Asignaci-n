# Backlog Tecnico Ejecutable - Sprint 1

Proyecto: Sistema de Asignacion de Salones  
Sprint objetivo: Fundacion (HU1, HU2, HU3)  
Duracion: 2 semanas  
Estado base actual: backend y frontend iniciales, sin autenticacion ni CRUD funcional.

## 1. Objetivo de Sprint 1

Entregar un flujo minimo funcional con:
- Login por rol.
- Rutas protegidas en backend.
- Gestion basica de usuarios.
- Configuracion de parametros generales (periodos, franjas, tipos de espacio).

Historias objetivo:
- HU1
- HU2
- HU3

Referencias principales:
- docs/PLAN_DE_SPRINTS.md
- docs/DOCUMENTACION_MVP.md
- docs/issues_tecnicas.md
- docs/DEFINITION_OF_DONE.md

## 2. Criterio de exito del sprint

Sprint 1 se considera logrado si se cumple todo:
- Login funcional desde frontend contra endpoint backend.
- Backend protege endpoints por autenticacion y rol.
- CRUD de usuarios operativo (crear, listar, editar, desactivar).
- CRUD de parametros generales operativo.
- Pruebas minimas de autenticacion y permisos en verde.

## 3. Orden de ejecucion recomendado

1) Base tecnica backend (modelo + migraciones)
2) Auth y RBAC
3) Endpoints HU1/HU2/HU3
4) Frontend login + vistas de gestion
5) Pruebas y cierre DoD

## 4. Backlog tecnico por tickets (listo para ejecutar)

## BE-01 - Modelado base de dominio (TEC-10)
Tipo: Backend  
Prioridad: Alta  
Estimacion: 5h

Descripcion:
Crear modelos base para Sprint 1:
- Role
- UserProfile (si no extiendes User directamente)
- AcademicPeriod
- TimeSlot
- SpaceType

Criterios de aceptacion:
- Modelos definidos en apps/core/models.py o apps separadas por dominio.
- Relaciones y constraints basicos definidos (unique, FK, indexes simples).
- Admin de Django registra modelos para validacion manual.

## BE-02 - Migraciones iniciales y restricciones (TEC-11)
Tipo: Backend  
Prioridad: Alta  
Estimacion: 2h

Descripcion:
Crear y aplicar migraciones iniciales del Sprint 1.

Criterios de aceptacion:
- migrate ejecuta sin errores en SQLite local.
- Esquema consistente para usar luego en Supabase.
- No hay warning critico de migraciones pendientes.

## BE-03 - Autenticacion y sesion API (TEC-12/TEC-14)
Tipo: Backend  
Prioridad: Alta  
Estimacion: 6h

Descripcion:
Implementar autenticacion API para login, logout y endpoint me.

Criterios de aceptacion:
- Endpoint login retorna token o sesion valida.
- Endpoint me retorna usuario autenticado.
- Logout invalida sesion/token segun estrategia elegida.
- Errores de auth responden con codigos HTTP correctos.

## BE-04 - RBAC en endpoints (TEC-13)
Tipo: Backend  
Prioridad: Alta  
Estimacion: 4h

Descripcion:
Aplicar permisos por rol en endpoints de gestion.

Criterios de aceptacion:
- Usuario sin rol permitido recibe 403.
- Admin puede gestionar usuarios y parametros.
- Coordinador no puede ejecutar operaciones de admin.

## BE-05 - CRUD usuarios y roles (TEC-15)
Tipo: Backend  
Prioridad: Alta  
Estimacion: 6h

Descripcion:
Crear endpoints CRUD para usuarios (alta, listado, edicion, activacion/desactivacion).

Criterios de aceptacion:
- Validacion de email unico.
- Filtros basicos (activo/inactivo, rol).
- Respuestas paginadas o con limite controlado.

## BE-06 - CRUD parametros generales (TEC-16)
Tipo: Backend  
Prioridad: Alta  
Estimacion: 5h

Descripcion:
Crear endpoints para:
- periodos academicos
- franjas horarias
- tipos de espacio

Criterios de aceptacion:
- Crear/editar/eliminar/listar en API.
- Validaciones de negocio minimas (sin rangos invalidos, nombres duplicados).
- Datos persisten correctamente.

## FE-01 - Login UI y conexion API (TEC-17)
Tipo: Frontend  
Prioridad: Alta  
Estimacion: 4h

Descripcion:
Construir pantalla de login y conexion con endpoint backend.

Criterios de aceptacion:
- Formulario login funcional.
- Manejo de error credenciales invalidas.
- Guardado de sesion/token en cliente.
- Redireccion inicial por rol.

## FE-02 - Layout base protegido
Tipo: Frontend  
Prioridad: Alta  
Estimacion: 3h

Descripcion:
Crear estructura base de navegacion con rutas protegidas.

Criterios de aceptacion:
- Rutas privadas redirigen al login si no hay sesion.
- Menu cambia por rol.
- Estado de autenticacion consistente tras refresh.

## FE-03 - Gestion de usuarios UI
Tipo: Frontend  
Prioridad: Media/Alta  
Estimacion: 5h

Descripcion:
Vista para listar, crear y editar usuarios.

Criterios de aceptacion:
- Tabla de usuarios con acciones basicas.
- Formulario de alta/edicion con validaciones.
- Mensajes de exito/error visibles.

## FE-04 - Configuracion parametros UI
Tipo: Frontend  
Prioridad: Media/Alta  
Estimacion: 5h

Descripcion:
Pantallas para periodos, franjas y tipos de espacio.

Criterios de aceptacion:
- CRUD visual para cada catalogo.
- Validaciones cliente (campos obligatorios y formato).
- Refresco de datos despues de cada operacion.

## QA-01 - Pruebas auth + permisos (TEC-18)
Tipo: QA/Backend  
Prioridad: Alta  
Estimacion: 4h

Descripcion:
Pruebas unitarias/integracion para:
- login correcto/incorrecto
- endpoint protegido
- permisos por rol

Criterios de aceptacion:
- Suite de pruebas en verde.
- Casos negativos incluidos.
- Evidencia de ejecucion registrada.

## OPS-01 - Pipeline minimo CI (TEC-02)
Tipo: DevOps  
Prioridad: Alta  
Estimacion: 3h

Descripcion:
Configurar workflow minimo en GitHub Actions.

Criterios de aceptacion:
- Ejecuta instalacion, lint y tests en push/PR.
- Falla correctamente cuando tests rompen.
- Badge o evidencia de pipeline activo.

## 5. Plan diario (2 semanas)

Semana 1:
- Dia 1: BE-01, BE-02
- Dia 2: BE-03 (login/me)
- Dia 3: BE-03 (logout) + BE-04
- Dia 4: BE-05
- Dia 5: FE-01

Semana 2:
- Dia 6: FE-02
- Dia 7: BE-06
- Dia 8: FE-03
- Dia 9: FE-04
- Dia 10: QA-01 + OPS-01 + demo interna

## 6. Dependencias criticas

- BE-01 y BE-02 desbloquean BE-03/BE-05/BE-06.
- BE-03 desbloquea FE-01 y FE-02.
- BE-05 desbloquea FE-03.
- BE-06 desbloquea FE-04.
- QA-01 depende de BE-03/BE-04.

## 7. Checklist tecnico de cierre de Sprint 1

- [ ] Migraciones aplicadas y versionadas.
- [ ] Endpoints de auth operativos.
- [ ] RBAC aplicado en endpoints administrativos.
- [ ] Login frontend conectado al backend.
- [ ] CRUD usuarios funcionando.
- [ ] CRUD parametros funcionando.
- [ ] Pruebas basicas en verde.
- [ ] Demo de HU1-HU2-HU3 lista para review.

## 8. Comandos operativos utiles

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Pruebas backend:

```bash
cd backend
python manage.py test
```

## 9. Riesgos inmediatos y accion

Riesgo 1: Inconsistencia documental de roles y stack en algunos textos.
Accion: Tomar como fuente de verdad docs/CONTRATO_RISE_UniValle.md + docs/DOCUMENTACION_MVP.md + docs/PLAN_DE_SPRINTS.md.

Riesgo 2: Integracion futura del algoritmo puede bloquear Sprint 4.
Accion: abrir ticket tecnico de especificacion API del algoritmo en Sprint 1.

Riesgo 3: CI/CD incompleto.
Accion: completar OPS-01 esta misma iteracion para evitar deuda acumulada.

---

Documento de trabajo para ejecucion tecnica diaria del equipo dev.
