# Evidencia de Cumplimiento - Sprint 1

## Estado general
- Cobertura backend `apps/core`: **95%**
- Pruebas ejecutadas: `43` casos en `apps.core`
- Build frontend: exitoso

## Trazabilidad criterio -> evidencia

1. Modelo inicial con usuarios, roles, periodos, dias laborables, franjas y tipos de espacio.
- Evidencia: `backend/apps/core/models.py`
- Evidencia: `backend/apps/core/migrations/0001_initial.py`
- Evidencia: `backend/apps/core/migrations/0004_workingday.py`

2. Migraciones iniciales y restricciones de base de datos.
- Evidencia: `backend/apps/core/migrations/0001_initial.py`
- Evidencia: `backend/apps/core/migrations/0002_userprofile_user.py`
- Evidencia: `backend/apps/core/migrations/0003_seed_default_roles.py`
- Evidencia: `backend/apps/core/migrations/0004_workingday.py`

3. Login entrega access/refresh + refresh/log out funcionales.
- Evidencia: `backend/apps/core/urls.py` (auth login, refresh, logout, me)
- Evidencia: `backend/apps/core/tests.py` (refresh valido, refresh revocado, logout con y sin refresh)

4. RBAC en endpoints protegidos con respuesta 403 consistente.
- Evidencia: `backend/apps/core/permissions.py`
- Evidencia: `backend/apps/core/views.py`
- Evidencia: `backend/apps/core/tests.py`

5. CRUD usuarios/roles con validaciones en capa services.
- Evidencia: `backend/apps/core/views.py`
- Evidencia: `backend/apps/core/services/user_service.py`
- Evidencia: `backend/apps/core/tests.py`

6. CRUD parametros generales (periodos, dias, franjas, tipos) con validaciones.
- Evidencia: `backend/apps/core/views.py`
- Evidencia: `backend/apps/core/services/config_service.py`
- Evidencia: `backend/apps/core/tests.py`

7. Frontend login + usuarios + configuracion conectados al backend y respetando rol.
- Evidencia: `frontend/src/App.jsx`
- Evidencia: `frontend/src/features/auth/services/authApi.jsx`
- Evidencia: `frontend/src/features/users/services/usersApi.jsx`
- Evidencia: `frontend/src/features/config/services/configApi.jsx`

8. Gate de cobertura en integracion continua.
- Evidencia: `.github/workflows/ci.yml` (`coverage report --fail-under=95`)

## Comandos de verificacion recomendados

Backend pruebas + cobertura:

```bash
cd backend
python -m coverage run --source=apps/core --omit='*/migrations/*,*/admin.py,*/apps.py,*/__init__.py' manage.py test apps.core --noinput
python -m coverage report -m --fail-under=95
```

Frontend build:

```bash
cd frontend
npm run build
```
