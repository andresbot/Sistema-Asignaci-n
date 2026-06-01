# Integración del algoritmo de asignación

Este documento indica **qué archivos del proyecto se deben tocar** para integrar el motor del algoritmo dentro del flujo de la HU10.

Resumen
- El proyecto ya incluye un adaptador de ejemplo (`engine_stub`) que permite probar la HU10 end-to-end con los archivos `.xlsx` disponibles.
- Cuando se quiera usar el motor real, el cambio ocurre únicamente en el backend, sin tocar la UI.

Punto principal de integración
- `backend/apps/core/services/schedule_execution_service.py`
  - Este archivo controla la ejecución del algoritmo, el progreso por generación, el guardado del `ScheduleExecution.result_snapshot` y la actualización de `AcademicPeriod.schedule_generated_at`.
  - Dentro de este archivo está la llamada al motor de ejemplo (`run_engine_stub(execution)`). Ese es el punto que debe reemplazarse o adaptarse para ejecutar el motor real.

Qué se toca ahí
- Si el motor está escrito como función Python, se importa y se llama esa función desde este archivo.
- Si el motor se expone como servicio REST, aquí se hace la petición HTTP y se procesa la respuesta.
- Si el motor se entrega como ejecutable, aquí se invoca con `subprocess` y se lee su salida para convertirla al formato esperado.

Archivos de apoyo
- `backend/apps/core/services/engine_stub.py`
  - Sirve como referencia de la lógica de integración.
  - Muestra cómo tomar las asignaciones, guardar `working_day`, `time_slot`, `assigned_classroom` y registrar `schedule_failure_reason` cuando no se puede asignar.

- `backend/apps/core/services/adapter_cli.py`
  - Script auxiliar para probar el flujo con `DatosBD.xlsx`.
  - Muestra cómo preparar un `input_dict` y cómo simular la llamada al motor en los modos `function`, `rest` o `exec`.

Qué debe hacer el código que reemplace al stub
- Recibir la ejecución y los datos del periodo académico.
- Ejecutar el motor y obtener al menos dos colecciones: `assignments` y `unassigned`.
- Mapear cada asignación a un `SubjectOffering` usando `{codigo, grupo}`.
- Actualizar la oferta con `working_day`, `time_slot`, `assigned_classroom` o, si no hay solución, con `schedule_failure_reason`.
- Dejar que `schedule_execution_service.py` termine de guardar el resultado y marque la ejecución como `COMPLETED` o `FAILED` según corresponda.

Pruebas locales
- Con el stub actual, la HU10 se puede probar creando una ejecución desde la UI o con la API y consultando `GET programming/schedule-executions/<id>/`.
- El backend ya tiene pruebas de integración que validan ese flujo con el stub.

Notas prácticas
- No es necesario modificar la UI ni las rutas del API.
- Toda la integración se realiza en el backend, en los archivos indicados arriba.
- Si más adelante se quiere cambiar el adaptador sin editar código, se puede agregar una carga dinámica por variable de entorno.
