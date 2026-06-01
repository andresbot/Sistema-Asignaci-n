# 📋 Historias de Usuario — Sistema de Asignación de Salones
**Universidad del Valle, Seccional Zarzal · Modelo de las 3 Cs (Scrum Manager)**

> Cada historia sigue la estructura completa: **Card** (descripción), **Conversation** (criterios de aceptación en formato Gherkin) y **Confirmation** (definición de hecho). Se incluyen estimación en puntos de historia (serie Fibonacci), prioridad MoSCoW y valor de negocio.

---

## Milestone 1 · Fundación del sistema — Autenticación y configuración

---

### HU1 · Iniciar sesión según rol

| Campo | Detalle |
|---|---|
| **ID** | HU1 |
| **Título GitHub** | HU1 · Iniciar sesión según rol |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 8 |

**Card**
> Como **administrador**, quiero iniciar sesión con mis credenciales, para acceder a las funcionalidades del sistema según mi rol.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Inicio de sesión exitoso con credenciales válidas
  Dado que el usuario tiene una cuenta activa en el sistema
  Y que ingresa un correo y contraseña correctos
  Cuando hace clic en "Iniciar sesión"
  Entonces el sistema lo redirige al panel correspondiente a su rol
  Y se muestra su nombre y rol en la interfaz

Escenario 2: Credenciales incorrectas
  Dado que el usuario ingresa una contraseña incorrecta
  Cuando hace clic en "Iniciar sesión"
  Entonces el sistema muestra un mensaje de error claro
  Y no permite el acceso al sistema

Escenario 3: Acceso restringido por rol
  Dado que un usuario con rol coordinador ha iniciado sesión
  Cuando intenta acceder a una ruta exclusiva de administrador
  Entonces el sistema le deniega el acceso
  Y lo redirige a su panel correspondiente
```

**Confirmation — Definición de hecho**
- [x] El login funciona con correo y contraseña almacenados en Supabase.
- [x] El sistema distingue y redirige correctamente según el rol (administrador / coordinador / docente / estudiante).
- [x] Las rutas están protegidas por rol en el backend Django.
- [x] Se muestran mensajes de error claros ante credenciales incorrectas.
- [x] Pruebas unitarias del endpoint de autenticación con cobertura ≥ 95 %.
- [x] Aprobada por el Product Owner.

---

### HU2 · Gestionar cuentas y roles de usuarios

| Campo | Detalle |
|---|---|
| **ID** | HU2 |
| **Título GitHub** | HU2 · Gestionar cuentas y roles de usuarios |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 5 puntos |
| **Valor de negocio** | 7 |

**Card**
> Como **administrador**, quiero crear y gestionar cuentas de usuarios con diferentes roles (administrador y coordinador), para controlar el acceso al sistema.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Crear un nuevo usuario
  Dado que el administrador está en el panel de gestión de usuarios
  Cuando completa el formulario con nombre, correo y rol
  Y hace clic en "Crear usuario"
  Entonces el sistema crea la cuenta y la lista en el panel
  Y el nuevo usuario recibe un correo de bienvenida con sus credenciales

Escenario 2: Editar el rol de un usuario existente
  Dado que el administrador selecciona un usuario de la lista
  Cuando cambia su rol y guarda los cambios
  Entonces el sistema actualiza el rol
  Y los permisos del usuario cambian de forma inmediata

Escenario 3: Desactivar una cuenta
  Dado que el administrador desactiva la cuenta de un usuario
  Cuando ese usuario intenta iniciar sesión
  Entonces el sistema le deniega el acceso con un mensaje explicativo
```

**Confirmation — Definición de hecho**
- [x] El administrador puede crear, editar y desactivar cuentas desde la interfaz React.
- [x] El sistema soporta al menos los roles: administrador, coordinador, docente, estudiante.
- [x] Los cambios de rol toman efecto sin necesidad de reiniciar sesión (o con aviso claro).
- [x] Se valida que el correo sea único en el sistema.
- [x] Pruebas unitarias del servicio de gestión de usuarios con cobertura ≥ 95 %.
- [x] Aprobada por el Product Owner.

---

### HU3 · Configurar parámetros generales del sistema

| Campo | Detalle |
|---|---|
| **ID** | HU3 |
| **Título GitHub** | HU3 · Configurar parámetros generales del sistema |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 5 puntos |
| **Valor de negocio** | 9 |

**Card**
> Como **administrador**, quiero configurar parámetros generales del sistema como períodos académicos, días laborables, franjas horarias y tipos de espacios académicos, para garantizar el correcto funcionamiento del sistema.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Registrar un período académico nuevo
  Dado que el administrador accede al módulo de configuración
  Cuando registra un nuevo período con nombre, fecha de inicio y fecha de fin
  Y hace clic en "Guardar"
  Entonces el sistema almacena el período y lo lista como activo

Escenario 2: Configurar días laborables y franjas horarias
  Dado que el administrador accede a la configuración de franjas
  Cuando define los días laborables y las franjas horarias (hora inicio, hora fin)
  Y guarda los cambios
  Entonces el sistema utiliza esas franjas como base para la programación académica

Escenario 3: Registrar tipos de espacio académico
  Dado que el administrador accede a la configuración de tipos de espacio
  Cuando agrega un nuevo tipo (ej. MG - Magistral, PR - Práctica)
  Entonces el sistema lo incluye como opción válida al registrar salones y asignaturas

Escenario 4: Intentar guardar una configuración incompleta
  Dado que el administrador deja campos obligatorios vacíos
  Cuando intenta guardar
  Entonces el sistema muestra mensajes de validación claros por campo
  Y no permite guardar hasta que todos los campos requeridos estén completos
```

**Confirmation — Definición de hecho**
- [x] El módulo permite CRUD completo de períodos académicos, días, franjas y tipos de espacio.
- [x] Los datos guardados son consumibles directamente por el servicio del algoritmo sin transformación manual.
- [x] Las validaciones impiden registros incompletos o con rangos horarios inválidos.
- [x] Pruebas unitarias del servicio de configuración con cobertura ≥ 95 %.
- [x] Aprobada por el Product Owner.

---

## Milestone 2 · Registro de datos maestros

---

### HU4 · Definir grupos por asignatura

| Campo | Detalle |
|---|---|
| **ID** | HU4 |
| **Título GitHub** | HU4 · Definir grupos por asignatura |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 7 |

**Card**
> Como **administrador**, quiero definir los grupos de cada asignatura, para organizar correctamente la programación académica.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Agregar un grupo a una asignatura
  Dado que el administrador accede a la configuración de una asignatura
  Cuando agrega un nuevo grupo con su identificador (ej. Grupo 1, Grupo A)
  Y guarda los cambios
  Entonces el grupo queda asociado a la asignatura y disponible para la programación

Escenario 2: Intentar crear un grupo duplicado
  Dado que ya existe el Grupo 1 para una asignatura
  Cuando el administrador intenta crear otro Grupo 1 para la misma asignatura
  Entonces el sistema muestra un error de duplicado
  Y no permite guardarlo
```

**Confirmation — Definición de hecho**
- [x] El administrador puede agregar, editar y eliminar grupos por asignatura.
- [x] El sistema impide grupos duplicados para la misma asignatura.
- [x] Los grupos son visibles y seleccionables en el módulo de programación académica.
- [x] Aprobada por el Product Owner.

---

### HU5 · Registrar salones disponibles

| Campo | Detalle |
|---|---|
| **ID** | HU5 |
| **Título GitHub** | HU5 · Registrar salones disponibles |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 5 puntos |
| **Valor de negocio** | 10 |

**Card**
> Como **administrador**, quiero registrar los salones disponibles con su capacidad, tipo y sede, para que el algoritmo pueda asignarlos correctamente.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Registrar un salón nuevo
  Dado que el administrador accede al módulo de salones
  Cuando ingresa el código, nombre, capacidad, tipo (MG/PR/etc.) y sede (Bolívar/Balsas)
  Y guarda el registro
  Entonces el salón queda disponible para ser asignado por el algoritmo

Escenario 2: Registrar un salón accesible para movilidad reducida
  Dado que el administrador marca la opción de accesibilidad al registrar un salón
  Cuando el algoritmo busca salones para asignaturas con estudiantes con discapacidad
  Entonces solo considera salones marcados como accesibles

Escenario 3: Intentar registrar un salón con código duplicado
  Dado que ya existe un salón con el mismo código
  Cuando el administrador intenta guardar un nuevo salón con ese código
  Entonces el sistema muestra un error y no permite el registro
```

**Confirmation — Definición de hecho**
- [x] El módulo permite CRUD completo de salones con todos sus atributos (código, nombre, capacidad, tipo, sede, accesibilidad).
- [x] Los salones registrados son consumidos correctamente por el servicio del algoritmo.
- [x] Se valida unicidad del código de salón.
- [x] Pruebas unitarias del modelo de salones con cobertura ≥ 95 %.
- [x] Aprobada por el Product Owner.

---

### HU6 · Gestionar parámetros de docentes

| Campo | Detalle |
|---|---|
| **ID** | HU6 |
| **Título GitHub** | HU6 · Gestionar parámetros de docentes |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 6 |

**Card**
> Como **administrador**, quiero agregar, editar o eliminar la configuración de parámetros de docentes como tipo de vinculación y valor por hora, para garantizar el correcto funcionamiento del sistema.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Registrar un docente nuevo
  Dado que el administrador accede al módulo de docentes
  Cuando ingresa nombre, tipo de vinculación y valor por hora
  Y guarda el registro
  Entonces el docente queda disponible para ser asignado a asignaturas

Escenario 2: Editar los datos de un docente existente
  Dado que el administrador selecciona un docente de la lista
  Cuando actualiza su tipo de vinculación o valor por hora
  Y guarda los cambios
  Entonces el sistema refleja la actualización en todos los módulos relacionados

Escenario 3: Eliminar un docente sin asignaturas activas
  Dado que un docente no tiene asignaturas asignadas en el período actual
  Cuando el administrador lo elimina
  Entonces el sistema lo remueve del registro sin afectar la programación activa
```

**Confirmation — Definición de hecho**
- [x] CRUD completo de docentes desde la interfaz React.
- [x] El sistema impide eliminar docentes con asignaturas asignadas en el período activo (o muestra advertencia).
- [x] Los datos del docente son consumibles por el algoritmo en la hoja `docentes`.
- [x] Aprobada por el Product Owner.

---

### HU7 · Gestionar configuración de asignaturas

| Campo | Detalle |
|---|---|
| **ID** | HU7 |
| **Título GitHub** | HU7 · Gestionar configuración de asignaturas |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 5 puntos |
| **Valor de negocio** | 9 |

**Card**
> Como **administrador**, quiero agregar, editar o eliminar la configuración de la asignatura como código, nombre, tipo de clases, créditos e intensidad horaria, para garantizar el correcto funcionamiento del sistema.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Registrar una asignatura nueva
  Dado que el administrador accede al módulo de asignaturas
  Cuando ingresa código, nombre, tipo de clase, créditos e intensidad horaria
  Y guarda el registro
  Entonces la asignatura queda disponible para la programación académica

Escenario 2: Editar la intensidad horaria de una asignatura
  Dado que el administrador edita una asignatura existente
  Cuando actualiza su intensidad horaria
  Entonces el sistema recalcula la dificultad de la asignatura para el algoritmo

Escenario 3: Intentar registrar una asignatura con código duplicado
  Dado que ya existe una asignatura con el mismo código
  Cuando el administrador intenta guardar otra con ese mismo código
  Entonces el sistema muestra un error y no permite el registro
```

**Confirmation — Definición de hecho**
- [x] CRUD completo de asignaturas con todos sus atributos.
- [x] El campo `dificultad` (intensidad × cupo) es calculado automáticamente y disponible para el algoritmo.
- [x] Se valida unicidad del código de asignatura.
- [x] Pruebas unitarias con cobertura ≥ 95 %.
- [x] Aprobada por el Product Owner.

---

### HU16 · Registrar información básica de asignatura

| Campo | Detalle |
|---|---|
| **ID** | HU16 |
| **Título GitHub** | HU16 · Registrar información básica de asignatura |
| **Rol** | Coordinador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 8 |

**Card**
> Como **coordinador**, quiero registrar la información básica de la asignatura (código, programa académico y semestre), para incluirla en la programación académica del período.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Registrar una asignatura en la programación del período
  Dado que el coordinador accede al módulo de programación académica
  Cuando selecciona una asignatura del catálogo y asigna programa académico y semestre
  Y guarda el registro
  Entonces la asignatura queda incluida en la programación del período activo

Escenario 2: Intentar registrar una asignatura sin semestre
  Dado que el coordinador deja el campo semestre vacío
  Cuando intenta guardar
  Entonces el sistema muestra un mensaje de validación y no permite continuar
```

**Confirmation — Definición de hecho**
- [x] El coordinador puede registrar asignaturas en la programación seleccionando del catálogo maestro.
- [x] Los campos código, programa y semestre son obligatorios y validados.
- [x] El registro queda vinculado al período académico activo.
- [x] Aprobada por el Product Owner.

---

### HU17 · Registrar docente responsable por asignatura

| Campo | Detalle |
|---|---|
| **ID** | HU17 |
| **Título GitHub** | HU17 · Registrar docente responsable por asignatura |
| **Rol** | Coordinador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 8 |

**Card**
> Como **coordinador**, quiero registrar el docente responsable de cada asignatura, para que el sistema tenga en cuenta esta información al generar el horario.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Asignar un docente a una asignatura
  Dado que el coordinador accede a la programación de una asignatura
  Cuando selecciona un docente del listado disponible
  Y guarda la asignación
  Entonces el sistema vincula el docente a esa asignatura y grupo para el período activo

Escenario 2: Cambiar el docente asignado antes de ejecutar el algoritmo
  Dado que una asignatura ya tiene docente asignado
  Cuando el coordinador lo cambia por otro
  Y el algoritmo aún no ha sido ejecutado
  Entonces el sistema actualiza la asignación sin restricciones

Escenario 3: Intentar guardar sin seleccionar docente
  Dado que el campo docente está vacío
  Cuando el coordinador intenta guardar
  Entonces el sistema muestra advertencia pero permite guardar (el campo no bloquea el flujo)
```

**Confirmation — Definición de hecho**
- [x] El coordinador puede asignar y cambiar el docente de cualquier asignatura antes de ejecutar el algoritmo.
- [x] El docente asignado se refleja en los datos enviados al servicio del algoritmo.
- [x] Aprobada por el Product Owner.

---

### HU18 · Registrar número de estudiantes por asignatura

| Campo | Detalle |
|---|---|
| **ID** | HU18 |
| **Título GitHub** | HU18 · Registrar número de estudiantes por asignatura |
| **Rol** | Coordinador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 2 puntos |
| **Valor de negocio** | 9 |

**Card**
> Como **coordinador**, quiero registrar el número de estudiantes de cada asignatura, para que el sistema pueda asignar un salón con la capacidad adecuada.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Registrar el cupo de una asignatura
  Dado que el coordinador accede a los datos de una asignatura en la programación
  Cuando ingresa el número de estudiantes matriculados
  Y guarda el dato
  Entonces el sistema almacena el cupo y lo usa como criterio mínimo de capacidad para la asignación de salón

Escenario 2: Ingresar un número de estudiantes mayor a la capacidad de todos los salones
  Dado que el coordinador registra un cupo que supera la capacidad máxima de cualquier salón disponible
  Cuando el algoritmo se ejecuta
  Entonces el sistema reporta la asignatura como no asignable con la razón correspondiente
```

**Confirmation — Definición de hecho**
- [x] El campo cupo es numérico, obligatorio y mayor que cero.
- [x] El valor es consumido por el algoritmo como restricción de capacidad mínima.
- [x] Aprobada por el Product Owner.

---

## Milestone 3 · Programación académica

---

### HU19 · Definir día y franja horaria por asignatura

| Campo | Detalle |
|---|---|
| **ID** | HU19 |
| **Título GitHub** | HU19 · Definir día y franja horaria por asignatura |
| **Rol** | Coordinador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 10 |

**Card**
> Como **coordinador**, quiero definir el día y la franja horaria de cada asignatura (hora de inicio y hora de fin), para establecer la programación académica del semestre.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Asignar día y franja horaria a una asignatura
  Dado que el coordinador accede a la programación de una asignatura
  Cuando selecciona el día de la semana y la franja horaria (inicio y fin)
  Y guarda la asignación
  Entonces el sistema almacena esos datos y los usa como restricción fija para el algoritmo

Escenario 2: Intentar asignar una franja fuera de los días laborables configurados
  Dado que el sistema tiene configurados los días laborables
  Cuando el coordinador intenta asignar un día no laborable
  Entonces el sistema lo impide y muestra un mensaje explicativo

Escenario 3: Intentar asignar una hora de fin anterior a la hora de inicio
  Dado que el coordinador ingresa una hora de fin menor a la hora de inicio
  Cuando intenta guardar
  Entonces el sistema muestra un error de validación de rango horario
```

**Confirmation — Definición de hecho**
- [x] El coordinador puede seleccionar día y franja para cada asignatura dentro de los parámetros configurados.
- [x] Las validaciones impiden franjas fuera de los días laborables o con rangos inválidos.
- [x] Los datos son consumidos correctamente por el algoritmo.
- [x] Aprobada por el Product Owner.

---

### HU20 · Indicar estudiantes con discapacidad

| Campo | Detalle |
|---|---|
| **ID** | HU20 |
| **Título GitHub** | HU20 · Indicar estudiantes con discapacidad |
| **Rol** | Coordinador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 2 puntos |
| **Valor de negocio** | 8 |

**Card**
> Como **coordinador**, quiero indicar si en la asignatura existen estudiantes con discapacidad, para que el sistema tenga en cuenta espacios accesibles en la asignación de salones.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Marcar una asignatura con necesidad de accesibilidad
  Dado que el coordinador accede a la programación de una asignatura
  Cuando activa la opción "estudiantes con discapacidad"
  Y guarda los cambios
  Entonces el algoritmo filtra y asigna únicamente salones marcados como accesibles para esa asignatura

Escenario 2: Asignatura sin necesidad de accesibilidad
  Dado que la opción de discapacidad no está activada para una asignatura
  Cuando el algoritmo se ejecuta
  Entonces puede asignar cualquier salón que cumpla capacidad y tipo, sin restricción de accesibilidad
```

**Confirmation — Definición de hecho**
- [x] El campo accesibilidad es un indicador booleano visible y editable por el coordinador.
- [x] El algoritmo respeta esta restricción en la selección de salones.
- [x] Aprobada por el Product Owner.

---

### HU21 · Indicar tipo de espacio requerido

| Campo | Detalle |
|---|---|
| **ID** | HU21 |
| **Título GitHub** | HU21 · Indicar tipo de espacio requerido |
| **Rol** | Coordinador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 2 puntos |
| **Valor de negocio** | 9 |

**Card**
> Como **coordinador**, quiero indicar el tipo de espacio requerido para la asignatura (MG, PR, etc.), para que el algoritmo asigne un salón adecuado.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Seleccionar el tipo de espacio para una asignatura
  Dado que el coordinador accede a la programación de una asignatura
  Cuando selecciona el tipo de espacio requerido (ej. MG - Magistral)
  Y guarda la selección
  Entonces el algoritmo solo considera salones de ese tipo al asignar

Escenario 2: No hay salones disponibles del tipo requerido
  Dado que el tipo de espacio seleccionado no tiene salones disponibles en la franja indicada
  Cuando el algoritmo se ejecuta
  Entonces reporta la asignatura como no asignable con la razón "sin salones del tipo requerido disponibles"
```

**Confirmation — Definición de hecho**
- [x] El tipo de espacio se selecciona desde el catálogo configurado por el administrador (HU3).
- [x] El algoritmo filtra salones por tipo antes de evaluar capacidad y disponibilidad.
- [x] Aprobada por el Product Owner.

---

### HU22 · Editar programación antes del algoritmo

| Campo | Detalle |
|---|---|
| **ID** | HU22 |
| **Título GitHub** | HU22 · Editar programación antes del algoritmo |
| **Rol** | Coordinador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 7 |

**Card**
> Como **coordinador**, quiero editar la programación académica registrada antes de ejecutar el algoritmo, para corregir posibles errores en la información.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Editar datos de una asignatura antes de ejecutar el algoritmo
  Dado que el algoritmo no ha sido ejecutado para el período activo
  Cuando el coordinador modifica el cupo, la franja, el docente o cualquier otro campo
  Y guarda los cambios
  Entonces el sistema actualiza los datos sin restricciones

Escenario 2: Intentar editar la programación después de ejecutar el algoritmo
  Dado que el algoritmo ya fue ejecutado y el horario fue generado
  Cuando el coordinador intenta editar la programación base
  Entonces el sistema muestra una advertencia indicando que el horario debe regenerarse si se realizan cambios
```

**Confirmation — Definición de hecho**
- [x] Todos los campos de la programación son editables antes de la ejecución del algoritmo.
- [x] El sistema advierte al usuario si intenta editar después de haber ejecutado el algoritmo.
- [x] Los cambios se reflejan inmediatamente en los datos que serán enviados al servicio.
- [x] Aprobada por el Product Owner.

---

### HU8 · Importar programación desde CSV o Excel

| Campo | Detalle |
|---|---|
| **ID** | HU8 |
| **Título GitHub** | HU8 · Importar programación desde CSV o Excel |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Should have |
| **Estimación** | 8 puntos |
| **Valor de negocio** | 7 |

**Card**
> Como **administrador**, quiero importar la programación académica desde archivos CSV o Excel, para agilizar el registro de la información académica.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Importar un archivo válido
  Dado que el administrador carga un archivo CSV o Excel con el formato correcto
  Cuando hace clic en "Importar"
  Entonces el sistema procesa el archivo y registra las asignaturas en la programación del período activo
  Y muestra un resumen de registros importados exitosamente

Escenario 2: Importar un archivo con errores de formato
  Dado que el archivo cargado tiene columnas faltantes o datos inválidos
  Cuando el sistema lo procesa
  Entonces muestra un reporte con las filas que fallaron y la razón de cada error
  Y solo importa las filas válidas

Escenario 3: Importar un archivo con registros duplicados
  Dado que el archivo contiene asignaturas ya registradas en el período
  Cuando el sistema detecta duplicados
  Entonces los omite y los reporta como advertencia sin detener la importación
```

**Confirmation — Definición de hecho**
- [x] El sistema acepta archivos `.csv` y `.xlsx`.
- [x] Se validan columnas obligatorias antes de procesar.
- [x] Se genera un reporte de importación (exitosos, errores, omitidos).
- [x] La importación no duplica registros existentes.
- [x] Pruebas con archivos reales del formato institucional.
- [x] Aprobada por el Product Owner.

---

### HU9 · Validar inconsistencias antes del algoritmo

| Campo | Detalle |
|---|---|
| **ID** | HU9 |
| **Título GitHub** | HU9 · Validar inconsistencias antes del algoritmo |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 5 puntos |
| **Valor de negocio** | 9 |

**Card**
> Como **administrador**, quiero validar posibles inconsistencias o conflictos en la programación académica antes de ejecutar el algoritmo, para evitar errores en la generación de horarios.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Validación exitosa sin inconsistencias
  Dado que la programación está completa y sin conflictos
  Cuando el administrador ejecuta la validación previa
  Entonces el sistema muestra un mensaje de éxito y habilita el botón de ejecutar algoritmo

Escenario 2: Validación detecta asignaturas sin franja horaria
  Dado que hay asignaturas sin día o franja asignada
  Cuando se ejecuta la validación
  Entonces el sistema lista las asignaturas con ese problema y bloquea la ejecución del algoritmo hasta corregirlas

Escenario 3: Validación detecta conflictos de docente en misma franja
  Dado que un docente tiene dos asignaturas en el mismo día y franja
  Cuando se ejecuta la validación
  Entonces el sistema alerta sobre el conflicto y lo lista claramente
```

**Confirmation — Definición de hecho**
- [x] La validación detecta: asignaturas sin franja, sin docente, sin cupo, sin tipo de espacio, y conflictos de docente en la misma franja.
- [x] El botón de ejecutar algoritmo solo se habilita si la validación pasa sin errores críticos.
- [x] El reporte de validación es claro y accionable.
- [x] Pruebas unitarias del servicio de validación con cobertura ≥ 95 %.
- [x] Aprobada por el Product Owner.

---

## Milestone 4 · Generación y gestión de horarios

---

### HU10 · Ejecutar algoritmo de asignación de salones

| Campo | Detalle |
|---|---|
| **ID** | HU10 |
| **Título GitHub** | HU10 · Ejecutar algoritmo de asignación de salones |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 13 puntos |
| **Valor de negocio** | 10 |

**Card**
> Como **administrador**, quiero ejecutar el algoritmo de asignación de salones, para generar automáticamente el horario académico.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Ejecución exitosa del algoritmo
  Dado que la programación ha pasado la validación previa sin errores críticos
  Cuando el administrador hace clic en "Ejecutar algoritmo"
  Y configura los parámetros opcionales (tamaño de población, generaciones, proporción heurística, umbral de estancamiento)
  Entonces el sistema lanza el servicio Python del algoritmo
  Y muestra el progreso generación a generación en tiempo real
  Y al finalizar presenta el horario generado y el reporte de asignaturas no asignadas

Escenario 2: El algoritmo no logra asignar algunas asignaturas
  Dado que hay asignaturas con restricciones que ningún salón puede satisfacer
  Cuando el algoritmo termina su ejecución
  Entonces el sistema presenta el mejor horario encontrado
  Y lista las asignaturas no asignadas con la razón de cada caso

Escenario 3: Error de comunicación con el servicio del algoritmo
  Dado que el servicio Python no está disponible
  Cuando el administrador intenta ejecutar el algoritmo
  Entonces el sistema muestra un mensaje de error claro
  Y no genera un horario parcial sin notificar al usuario
```

**Confirmation — Definición de hecho**
- [ ] El algoritmo se ejecuta desde la interfaz React a través del endpoint Django sin intervención técnica en el código.
- [ ] Los parámetros `poblacion_size`, `generaciones`, `proporcion_heuristica` y `estancamiento_max` son configurables desde la interfaz.
- [ ] El progreso se muestra en tiempo real (o mediante polling cada N segundos).
- [ ] El reporte de no asignadas incluye razón por asignatura.
- [ ] Tiempo de ejecución razonable para el volumen de datos de la seccional.
- [ ] Aprobada por el Product Owner.

---

### HU11 · Visualizar horario generado en plantilla gráfica

| Campo | Detalle |
|---|---|
| **ID** | HU11 |
| **Título GitHub** | HU11 · Visualizar horario generado en plantilla gráfica |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 8 puntos |
| **Valor de negocio** | 8 |

**Card**
> Como **administrador**, quiero visualizar el horario generado en plantillas gráficas, para validar fácilmente la distribución de las clases.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Visualizar el horario en formato grilla semanal
  Dado que el algoritmo ha generado el horario
  Cuando el administrador accede a la vista de horario
  Entonces el sistema muestra una grilla con días de la semana en columnas y franjas horarias en filas
  Y cada celda muestra la asignatura, docente, grupo y salón asignado

Escenario 2: Filtrar la vista por sede
  Dado que el horario incluye asignaciones en ambas sedes (Bolívar y Balsas)
  Cuando el administrador filtra por sede
  Entonces la grilla solo muestra las asignaciones de esa sede

Escenario 3: Visualizar asignaturas no asignadas
  Dado que el algoritmo no pudo asignar algunas asignaturas
  Cuando el administrador revisa el horario
  Entonces hay una sección visible con las asignaturas no asignadas y su razón
```

**Confirmation — Definición de hecho**
- [x] La plantilla gráfica muestra el horario completo en formato grilla semanal.
- [x] Es posible filtrar por sede, programa y semestre.
- [x] Las asignaturas no asignadas se muestran con su razón.
- [x] La vista es responsiva y usable desde pantallas de escritorio.
- [x] Aprobada por el Product Owner.

---

### HU13 · Modificar manualmente asignación de salón

| Campo | Detalle |
|---|---|
| **ID** | HU13 |
| **Título GitHub** | HU13 · Modificar manualmente asignación de salón |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Should have |
| **Estimación** | 8 puntos |
| **Valor de negocio** | 7 |

**Card**
> Como **administrador**, quiero modificar manualmente la asignación de un salón después de ejecutar el algoritmo, para corregir situaciones especiales que el sistema no haya contemplado.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Reasignar manualmente un salón
  Dado que el administrador identifica una asignación que desea corregir
  Cuando selecciona la asignatura en el horario y elige un salón diferente
  Entonces el sistema verifica que el nuevo salón no tenga conflictos en esa franja
  Y si está disponible, actualiza la asignación y registra el cambio en el historial

Escenario 2: Intentar asignar un salón con conflicto
  Dado que el administrador intenta asignar un salón ya ocupado en esa franja y día
  Cuando intenta guardar el cambio
  Entonces el sistema muestra una alerta de conflicto con el detalle de la asignación existente
  Y no permite guardar hasta que se resuelva el conflicto
```

**Confirmation — Definición de hecho**
- [ ] El administrador puede reasignar salones desde la vista gráfica del horario.
- [ ] El sistema valida disponibilidad antes de confirmar el cambio.
- [ ] Todo cambio manual queda registrado en el historial de trazabilidad (HU15).
- [ ] Aprobada por el Product Owner.

---

### HU23 · Visualizar horario semestral completo

| Campo | Detalle |
|---|---|
| **ID** | HU23 |
| **Título GitHub** | HU23 · Visualizar horario semestral completo |
| **Rol** | Coordinador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 5 puntos |
| **Valor de negocio** | 8 |

**Card**
> Como **coordinador**, quiero visualizar el horario semestral completo con todas las asignaciones, para verificar la programación académica generada.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Visualizar el horario completo del semestre
  Dado que el algoritmo ha generado el horario y fue publicado
  Cuando el coordinador accede a la vista de horario semestral
  Entonces el sistema muestra todas las asignaciones del período: asignatura, grupo, docente, franja, sede y salón

Escenario 2: Filtrar el horario por programa o semestre
  Dado que el coordinador quiere revisar solo un programa específico
  Cuando aplica el filtro correspondiente
  Entonces la vista muestra únicamente las asignaturas de ese programa y semestre
```

**Confirmation — Definición de hecho**
- [x] El coordinador tiene acceso de solo lectura al horario generado.
- [x] La vista incluye filtros por programa, semestre y sede.
- [x] La información mostrada coincide exactamente con el resultado del algoritmo y los ajustes manuales registrados.
- [x] Aprobada por el Product Owner.

---

### HU15 · Ver historial de cambios y trazabilidad

| Campo | Detalle |
|---|---|
| **ID** | HU15 |
| **Título GitHub** | HU15 · Ver historial de cambios y trazabilidad |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Should have |
| **Estimación** | 5 puntos |
| **Valor de negocio** | 6 |

**Card**
> Como **administrador**, quiero visualizar el historial de cambios en las asignaciones y saber qué usuario realizó cada modificación, para mantener control y trazabilidad de la información.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Ver historial de un cambio manual
  Dado que el administrador realizó una reasignación manual de salón
  Cuando accede al historial de cambios
  Entonces el sistema muestra la fecha, hora, usuario, asignatura afectada, salón anterior y salón nuevo

Escenario 2: Filtrar el historial por fecha o usuario
  Dado que el administrador quiere revisar los cambios de una fecha específica
  Cuando aplica el filtro de fecha
  Entonces el historial muestra solo los cambios de ese rango de tiempo
```

**Confirmation — Definición de hecho**
- [ ] Cada cambio manual en el horario queda registrado automáticamente con usuario, fecha/hora y detalle del cambio.
- [ ] El historial es accesible desde el panel de administración.
- [ ] Los registros del historial no pueden ser editados ni eliminados.
- [ ] Aprobada por el Product Owner.

---

## Milestone 5 · Publicación y consulta

---

### HU12 · Exportar horarios a CSV

| Campo | Detalle |
|---|---|
| **ID** | HU12 |
| **Título GitHub** | HU12 · Exportar horarios a CSV |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Should have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 6 |

**Card**
> Como **administrador**, quiero generar los horarios en formato CSV, para integrarlos con otras herramientas institucionales.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Exportar el horario completo a CSV
  Dado que el horario ha sido generado y el administrador accede a la opción de exportar
  Cuando hace clic en "Exportar CSV"
  Entonces el sistema genera y descarga un archivo CSV con todas las asignaciones del período
  Y el archivo incluye: asignatura, código, grupo, docente, día, hora inicio, hora fin, sede, salón

Escenario 2: Exportar solo las asignaturas no asignadas
  Dado que el algoritmo no pudo asignar algunas asignaturas
  Cuando el administrador exporta el reporte de no asignadas
  Entonces el archivo CSV incluye: asignatura, código, grupo y razón de no asignación
```

**Confirmation — Definición de hecho**
- [ ] El archivo exportado es compatible con Excel y herramientas de análisis institucionales.
- [ ] El nombre del archivo incluye el período académico para identificación fácil.
- [ ] Aprobada por el Product Owner.

---

### HU14 · Publicar horarios generados

| Campo | Detalle |
|---|---|
| **ID** | HU14 |
| **Título GitHub** | HU14 · Publicar horarios generados |
| **Rol** | Administrador |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 9 |

**Card**
> Como **administrador**, quiero publicar los horarios generados, para que docentes y estudiantes puedan consultarlos.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Publicar el horario del período activo
  Dado que el horario ha sido revisado y ajustado por el administrador
  Cuando hace clic en "Publicar horario"
  Entonces el sistema cambia el estado del horario a "publicado"
  Y el horario queda visible para docentes y estudiantes

Escenario 2: Despublicar un horario para hacer correcciones
  Dado que el administrador necesita hacer ajustes después de publicar
  Cuando despublica el horario
  Entonces el horario deja de ser visible para docentes y estudiantes
  Y el administrador puede realizar cambios y volver a publicar

Escenario 3: Intentar publicar un horario con asignaturas sin salón asignado
  Dado que hay asignaturas sin salón en el horario
  Cuando el administrador intenta publicar
  Entonces el sistema muestra una advertencia con las asignaturas pendientes
  Y permite publicar de igual forma si el administrador confirma
```

**Confirmation — Definición de hecho**
- [x] El horario tiene estados claramente diferenciados: borrador, publicado.
- [x] Solo los administradores pueden publicar y despublicar.
- [x] El cambio de estado es inmediato y visible para todos los usuarios con rol docente/estudiante.
- [x] Aprobada por el Product Owner.

---

### HU24 · Consultar horario por período académico

| Campo | Detalle |
|---|---|
| **ID** | HU24 |
| **Título GitHub** | HU24 · Consultar horario por período académico |
| **Rol** | Docente / Estudiante |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 9 |

**Card**
> Como **docente o estudiante**, quiero consultar mi horario por período académico, para conocer las clases que debo dictar o asistir.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Consultar el horario del período activo
  Dado que el horario ha sido publicado por el administrador
  Cuando el docente o estudiante accede a la vista de consulta y selecciona el período
  Entonces el sistema muestra las clases correspondientes a su rol y datos registrados

Escenario 2: El horario aún no ha sido publicado
  Dado que el administrador no ha publicado el horario del período seleccionado
  Cuando el usuario intenta consultarlo
  Entonces el sistema muestra un mensaje indicando que el horario no está disponible aún
```

**Confirmation — Definición de hecho**
- [x] El usuario puede seleccionar el período académico a consultar.
- [x] Solo se muestran horarios en estado "publicado".
- [x] La vista es de solo lectura para docentes y estudiantes.
- [x] Aprobada por el Product Owner.

---

### HU25 · Ver día, hora, sede y salón de cada clase

| Campo | Detalle |
|---|---|
| **ID** | HU25 |
| **Título GitHub** | HU25 · Ver día, hora, sede y salón de cada clase |
| **Rol** | Usuario general |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 2 puntos |
| **Valor de negocio** | 9 |

**Card**
> Como **usuario general**, quiero ver el día, hora, sede y salón de cada clase, para saber dónde debo presentarme.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Ver detalle completo de una clase
  Dado que el usuario consulta el horario publicado
  Cuando selecciona o visualiza una clase
  Entonces el sistema muestra: nombre de la asignatura, día, hora de inicio, hora de fin, sede (Bolívar/Balsas) y código del salón
```

**Confirmation — Definición de hecho**
- [x] Cada entrada del horario muestra todos los campos requeridos.
- [x] La información de sede y salón coincide exactamente con la asignación del algoritmo o los ajustes manuales.
- [x] Aprobada por el Product Owner.

---

### HU26 · Visualizar horario en plantilla visual

| Campo | Detalle |
|---|---|
| **ID** | HU26 |
| **Título GitHub** | HU26 · Visualizar horario en plantilla visual |
| **Rol** | Usuario general |
| **Prioridad MoSCoW** | Must have |
| **Estimación** | 5 puntos |
| **Valor de negocio** | 8 |

**Card**
> Como **usuario general**, quiero visualizar el horario en una plantilla visual, para entender fácilmente la distribución de mis clases.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Ver el horario en formato grilla semanal
  Dado que el usuario accede a la vista de horario
  Cuando el horario está publicado
  Entonces el sistema muestra una grilla con días en columnas y franjas horarias en filas
  Y cada celda muestra el nombre de la asignatura, sede y salón de forma clara y legible

Escenario 2: Grilla sin clases en una franja
  Dado que no hay clases asignadas en una franja específica
  Cuando el usuario visualiza la grilla
  Entonces esa celda aparece vacía de forma clara, sin generar confusión
```

**Confirmation — Definición de hecho**
- [x] La plantilla visual es la vista principal del horario para usuarios generales.
- [x] Es legible en pantallas de escritorio y tablet.
- [x] Aprobada por el Product Owner.

---

### HU27 · Filtrar horarios por programa, semestre o docente

| Campo | Detalle |
|---|---|
| **ID** | HU27 |
| **Título GitHub** | HU27 · Filtrar horarios por programa, semestre o docente |
| **Rol** | Usuario general |
| **Prioridad MoSCoW** | Should have |
| **Estimación** | 3 puntos |
| **Valor de negocio** | 7 |

**Card**
> Como **usuario general**, quiero filtrar los horarios por programa, semestre o docente, para encontrar rápidamente la información que necesito.

**Conversation — Criterios de aceptación**

```gherkin
Escenario 1: Filtrar por programa académico
  Dado que el usuario accede al horario publicado
  Cuando selecciona un programa académico en el filtro
  Entonces el sistema muestra únicamente las asignaturas de ese programa

Escenario 2: Filtrar por docente
  Dado que el usuario selecciona un docente en el filtro
  Cuando aplica el filtro
  Entonces el sistema muestra únicamente las asignaturas asignadas a ese docente

Escenario 3: Combinar filtros
  Dado que el usuario selecciona programa y semestre simultáneamente
  Cuando aplica los filtros
  Entonces el sistema muestra solo las asignaturas que cumplen ambos criterios
```

**Confirmation — Definición de hecho**
- [ ] Los filtros disponibles son: programa, semestre y docente.
- [ ] Los filtros pueden combinarse entre sí.
- [ ] El resultado se actualiza de forma inmediata al aplicar un filtro.
- [ ] Aprobada por el Product Owner.

---

## Resumen — Backlog priorizado

| ID | Historia | Milestone | Prioridad | Estimación | Valor |
|---|---|---|---|---|---|
| HU1 | Iniciar sesión según rol | M1 | Must have | 3 | 8 |
| HU2 | Gestionar cuentas y roles | M1 | Must have | 5 | 7 |
| HU3 | Configurar parámetros generales | M1 | Must have | 5 | 9 |
| HU5 | Registrar salones disponibles | M2 | Must have | 5 | 10 |
| HU7 | Gestionar configuración de asignaturas | M2 | Must have | 5 | 9 |
| HU9 | Validar inconsistencias antes del algoritmo | M3 | Must have | 5 | 9 |
| HU10 | Ejecutar algoritmo de asignación | M4 | Must have | 13 | 10 |
| HU19 | Definir día y franja horaria | M3 | Must have | 3 | 10 |
| HU21 | Indicar tipo de espacio requerido | M3 | Must have | 2 | 9 |
| HU14 | Publicar horarios generados | M5 | Must have | 3 | 9 |
| HU18 | Registrar número de estudiantes | M2 | Must have | 2 | 9 |
| HU4 | Definir grupos por asignatura | M2 | Must have | 3 | 7 |
| HU6 | Gestionar parámetros de docentes | M2 | Must have | 3 | 6 |
| HU16 | Registrar información básica de asignatura | M2 | Must have | 3 | 8 |
| HU17 | Registrar docente responsable | M2 | Must have | 3 | 8 |
| HU20 | Indicar estudiantes con discapacidad | M3 | Must have | 2 | 8 |
| HU22 | Editar programación antes del algoritmo | M3 | Must have | 3 | 7 |
| HU11 | Visualizar horario en plantilla gráfica | M4 | Must have | 8 | 8 |
| HU23 | Visualizar horario semestral completo | M4 | Must have | 5 | 8 |
| HU24 | Consultar horario por período | M5 | Must have | 3 | 9 |
| HU25 | Ver día, hora, sede y salón | M5 | Must have | 2 | 9 |
| HU26 | Visualizar horario en plantilla visual | M5 | Must have | 5 | 8 |
| HU8 | Importar programación desde CSV/Excel | M3 | Should have | 8 | 7 |
| HU13 | Modificar manualmente asignación de salón | M4 | Should have | 8 | 7 |
| HU15 | Ver historial de cambios y trazabilidad | M4 | Should have | 5 | 6 |
| HU12 | Exportar horarios a CSV | M5 | Should have | 3 | 6 |
| HU27 | Filtrar horarios por programa/semestre/docente | M5 | Should have | 3 | 7 |
| **Total** | | | | **114 puntos** | |

---

*Documento elaborado siguiendo el modelo de las 3 Cs de Ron Jeffries (Card, Conversation, Confirmation) y las buenas prácticas INVEST de Bill Wake · Scrum Manager® v3.01 · Universidad del Valle, Seccional Zarzal · 2026*
