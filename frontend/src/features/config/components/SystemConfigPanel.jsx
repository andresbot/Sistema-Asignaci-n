const SECTION_DEFINITIONS = {
  academicPrograms: {
    title: "Programas academicos",
    fields: [
      { name: "code", label: "Codigo", type: "text", required: true },
      { name: "name", label: "Nombre", type: "text", required: true },
      {
        name: "campus_id",
        label: "Campus",
        type: "select",
        required: true,
        optionsFrom: "campuses",
      },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  campuses: {
    title: "Campus",
    fields: [
      { name: "code", label: "Codigo", type: "text", required: true },
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  subjects: {
    title: "Catalogo de asignaturas",
    fields: [
      { name: "code", label: "Codigo", type: "text", required: true },
      { name: "name", label: "Nombre", type: "text", required: true },
      {
        name: "class_type_id",
        label: "Tipo de clase",
        type: "select",
        required: true,
        optionsFrom: "classTypes",
      },
      { name: "credits", label: "Creditos", type: "number", required: true, min: 1 },
      {
        name: "weekly_hours",
        label: "Intensidad horaria",
        type: "number",
        required: true,
        min: 1,
      },
      { name: "capacity", label: "Cupo", type: "number", required: true, min: 1 },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  subjectGroups: {
    title: "Grupos por asignatura",
    fields: [
      {
        name: "subject_id",
        label: "Asignatura",
        type: "select",
        required: true,
        optionsFrom: "subjects",
      },
      { name: "identifier", label: "Identificador", type: "text", required: true },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  subjectOfferings: {
    title: "Programacion de asignaturas",
    fields: [
      {
        name: "subject_id",
        label: "Asignatura",
        type: "select",
        required: true,
        optionsFrom: "subjects",
      },
      {
        name: "subject_group_id",
        label: "Grupo",
        type: "select",
        required: true,
        optionsFrom: "subjectGroups",
      },
      {
        name: "academic_program_id",
        label: "Programa academico",
        type: "select",
        required: true,
        optionsFrom: "academicPrograms",
      },
      {
        name: "working_day_id",
        label: "Dia laborable",
        type: "select",
        required: true,
        optionsFrom: "workingDays",
      },
      {
        name: "time_slot_id",
        label: "Franja horaria",
        type: "select",
        required: true,
        optionsFrom: "timeSlots",
      },
      {
        name: "required_space_type_id",
        label: "Tipo de espacio requerido",
        type: "select",
        required: false,
        optionsFrom: "academicSpaceTypes",
      },
      {
        name: "teacher_id",
        label: "Docente responsable",
        type: "select",
        required: false,
        optionsFrom: "teachers",
      },
      { name: "student_count", label: "Cupo matriculado", type: "number", required: false, min: 0 },
      { name: "semester", label: "Semestre", type: "number", required: true, min: 1 },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  periods: {
    title: "Periodos academicos",
    fields: [
      { name: "code", label: "Codigo", type: "text", required: true },
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "start_date", label: "Fecha inicio", type: "date", required: true },
      { name: "end_date", label: "Fecha fin", type: "date", required: true },
      { name: "is_schedule_published", label: "Horario publicado", type: "checkbox", required: false },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  workingDays: {
    title: "Dias laborables",
    fields: [
      {
        name: "day_of_week",
        label: "Dia (1-7)",
        type: "number",
        min: 1,
        max: 7,
        required: true,
      },
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  timeSlots: {
    title: "Franjas horarias",
    fields: [
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "start_time", label: "Hora inicio", type: "time", required: true },
      { name: "end_time", label: "Hora fin", type: "time", required: true },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  teacherLinkTypes: {
    title: "Tipos de vinculacion docente",
    fields: [
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "description", label: "Descripcion", type: "text", required: false },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  classTypes: {
    title: "Tipos de clase",
    fields: [
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "description", label: "Descripcion", type: "text", required: false },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  academicSpaceTypes: {
    title: "Tipos de espacio academico",
    fields: [
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "description", label: "Descripcion", type: "text", required: false },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  classrooms: {
    title: "Salones disponibles",
    fields: [
      { name: "code", label: "Codigo", type: "text", required: true },
      { name: "name", label: "Nombre", type: "text", required: true },
      {
        name: "campus_id",
        label: "Campus",
        type: "select",
        required: true,
        optionsFrom: "campuses",
      },
      {
        name: "space_type_id",
        label: "Tipo de espacio",
        type: "select",
        required: true,
        optionsFrom: "academicSpaceTypes",
      },
      { name: "capacity", label: "Capacidad", type: "number", required: true, min: 1 },
      { name: "is_accessible", label: "Accesible", type: "checkbox", required: false },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
};

function ConfigSectionCard({
  sectionKey,
  title,
  sectionState,
  fields,
  configState,
  onFieldChange,
  onSubmit,
  onEdit,
  onDelete,
  onCancel,
}) {
  return (
    <article className="card-block config-card">
      <h2>{title}</h2>

      <form className="form-grid" onSubmit={(event) => onSubmit(sectionKey, event)}>
        {fields.map((field) => {
          if (field.type === "checkbox") {
            return (
              <label key={field.name} className="checkbox-row">
                <input
                  type="checkbox"
                  checked={Boolean(sectionState.form[field.name])}
                  onChange={(event) =>
                    onFieldChange(sectionKey, field.name, event.target.checked)
                  }
                />
                {field.label}
              </label>
            );
          }

            if (field.type === "select") {
            const fixedOptions = field.options ?? null;
            const options =
              sectionKey === "subjectOfferings" && field.name === "subject_group_id"
                ? (configState?.[field.optionsFrom]?.items ?? []).filter(
                    (option) =>
                      String(option.subject?.id ?? option.subject_id ?? "") ===
                      String(sectionState.form.subject_id ?? ""),
                  )
                : sectionKey === "subjectOfferings" &&
                    (field.name === "working_day_id" || field.name === "time_slot_id")
                  ? (configState?.[field.optionsFrom]?.items ?? []).filter(
                      (option) => option.is_active !== false,
                    )
                : fixedOptions
                  ? fixedOptions
                  : configState?.[field.optionsFrom]?.items ?? [];

              return (
              <label key={field.name}>
                {field.label}
                <select
                  className={sectionState.fieldErrors?.[field.name] ? "input-error" : ""}
                  value={sectionState.form[field.name] ?? ""}
                  required={field.required}
                  onChange={(event) =>
                    onFieldChange(sectionKey, field.name, event.target.value)
                  }
                >
                  <option value="">Selecciona una opcion</option>
                  {options.map((option) => (
                    <option
                      key={option.id ?? option.value}
                      value={option.id ?? option.value}
                    >
                      {buildOptionLabel(option)}
                    </option>
                  ))}
                </select>
                {sectionState.fieldErrors?.[field.name] ? (
                  <p className="error-text small">{sectionState.fieldErrors[field.name]}</p>
                ) : null}
              </label>
            );
          }

          return (
            <label key={field.name}>
              {field.label}
              <input
                className={sectionState.fieldErrors?.[field.name] ? "input-error" : ""}
                type={field.type}
                value={sectionState.form[field.name] ?? ""}
                required={field.required}
                min={field.min}
                max={field.max}
                onChange={(event) =>
                  onFieldChange(sectionKey, field.name, event.target.value)
                }
              />
              {sectionState.fieldErrors?.[field.name] ? (
                <p className="error-text small">{sectionState.fieldErrors[field.name]}</p>
              ) : null}
            </label>
          );
        })}

        {sectionKey === "subjects" ? (
          <div>
            <p className="hint">Dificultad calculada: {Number(sectionState.form.weekly_hours || 0) * Number(sectionState.form.capacity || 0)}</p>
          </div>
        ) : null}

        {sectionState.error ? <p className="error-text">{sectionState.error}</p> : null}

        <div className="actions-inline">
          <button type="submit" disabled={sectionState.submitting}>
            {sectionState.submitting
              ? "Guardando..."
              : sectionState.editId
                ? "Guardar cambios"
                : "Crear"}
          </button>

          {sectionState.editId ? (
            <button type="button" className="secondary" onClick={() => onCancel(sectionKey)}>
              Cancelar
            </button>
          ) : null}
        </div>
      </form>

      <div className="config-items-list">
        {sectionState.loading ? <p className="hint">Cargando...</p> : null}
        {sectionState.items.map((item) => (
          <div key={item.id} className="config-item-row">
            <div>
              <strong>{item.name || item.code || `Registro ${item.id}`}</strong>
              <p className="hint small">{buildItemSummary(sectionKey, item)}</p>
            </div>
            <div className="actions-inline compact">
              <button className="secondary" type="button" onClick={() => onEdit(sectionKey, item)}>
                Editar
              </button>
              <button className="danger" type="button" onClick={() => onDelete(sectionKey, item.id)}>
                Eliminar
              </button>
            </div>
          </div>
        ))}
      </div>
    </article>
  );
}

function buildItemSummary(sectionKey, item) {
  if (sectionKey === "academicPrograms") {
    return `${item.code || "Sin codigo"} | ${item.campus?.name || item.campus_id || "Sin campus"}`;
  }

  if (sectionKey === "campuses") {
    return item.name || "Sin nombre";
  }

  if (sectionKey === "subjects") {
    const classTypeLabel = item.class_type_item?.name || item.class_type || "Tipo";
    return `${classTypeLabel} | Creditos ${item.credits} | Intensidad ${item.weekly_hours} | Cupo ${item.capacity} | Dificultad ${item.difficulty}`;
  }

  if (sectionKey === "subjectGroups") {
    const subjectCode = item.subject?.code || item.subject_id || "Asignatura";

    return `${subjectCode} | ${item.identifier} | ${item.is_active ? "Activo" : "Inactivo"}`;
  }

  if (sectionKey === "subjectOfferings") {
    const subjectCode = item.subject?.code || item.subject_id || "Asignatura";
    const groupIdentifier = item.subject_group?.identifier || item.subject_group_id || "Grupo";
    const programCode = item.academic_program?.code || item.academic_program_id || "Programa";
    const workingDay = item.working_day?.name || item.working_day_id || "Dia";
    const timeSlot = item.time_slot
      ? `${item.time_slot.start_time} - ${item.time_slot.end_time}`
      : item.time_slot_id || "Franja";
    const spaceType = item.required_space_type?.name || "Sin tipo de espacio";
    const teacher = item.teacher
      ? `${item.teacher.first_name} ${item.teacher.last_name}`.trim()
      : "Sin docente";

    const cupo = item.student_count !== null && item.student_count !== undefined ? `Cupo ${item.student_count}` : "Sin cupo";
    return `${programCode} | ${subjectCode} | ${groupIdentifier} | ${workingDay} | ${timeSlot} | S${item.semester} | ${spaceType} | ${teacher} | ${cupo}`;
  }

  if (sectionKey === "periods") {
    const publishState = item.is_schedule_published ? "Publicado" : "Borrador";
    return `${item.code} | ${item.start_date} a ${item.end_date} | ${publishState}`;
  }

  if (sectionKey === "workingDays") {
    return `Dia ${item.day_of_week} | ${item.is_active ? "Activo" : "Inactivo"}`;
  }

  if (sectionKey === "timeSlots") {
    return `${item.start_time} - ${item.end_time}`;
  }

  if (
    sectionKey === "teacherLinkTypes" ||
    sectionKey === "classTypes" ||
    sectionKey === "academicSpaceTypes"
  ) {
    return item.description || "Sin descripcion";
  }

  if (sectionKey === "classrooms") {
    const campus = item.campus?.name || item.campus_id || "Sin campus";
    const spaceType = item.space_type?.name || item.space_type_id || "Sin tipo";
    const accessible = item.is_accessible ? "Accesible" : "No accesible";
    return `${campus} | ${spaceType} | Cap. ${item.capacity} | ${accessible}`;
  }

  return "";
}

function buildOptionLabel(option) {
  if (option.label && option.value) {
    return option.label;
  }

  if (option.day_of_week && option.name) {
    return `${option.day_of_week} - ${option.name}`;
  }

  if (option.start_time && option.end_time) {
    return `${option.start_time} - ${option.end_time}`;
  }

  if (option.first_name !== undefined && option.last_name !== undefined) {
    return `${option.first_name} ${option.last_name}`.trim();
  }

  if (option.subject && option.identifier) {
    return `${option.subject.code} - ${option.identifier}`;
  }

  if (option.name && option.code) {
    return `${option.code} - ${option.name}`;
  }

  return option.code || option.name || `Registro ${option.id}`;
}

export function SystemConfigPanel({
  configState,
  importState,
  onRefresh,
  onDownloadTemplate,
  onImportFieldChange,
  onImportSubmit,
  onFieldChange,
  onSubmit,
  onEdit,
  onDelete,
  onCancel,
  visibleSections,
  title = "Configuracion general del sistema",
  description,
  showImportSection = true,
}) {
  const sectionEntries = Object.entries(SECTION_DEFINITIONS).filter(([sectionKey]) => {
    if (!visibleSections || visibleSections.length === 0) {
      return true;
    }

    return visibleSections.includes(sectionKey);
  });

  return (
    <section className="card-block system-config-panel">
      <header className="dashboard-header config-header">
        <div>
          <p className="eyebrow"></p>
          <h2>{title}</h2>
          {description ? <p className="lead compact">{description}</p> : null}
        </div>
        <button className="secondary" onClick={onRefresh}>
          Recargar configuracion
        </button>
      </header>

      <div className="config-grid">
        {sectionEntries.map(([sectionKey, sectionDefinition]) => (
          <ConfigSectionCard
            key={sectionKey}
            sectionKey={sectionKey}
            title={sectionDefinition.title}
            sectionState={configState[sectionKey]}
            fields={sectionDefinition.fields}
            configState={configState}
            onFieldChange={onFieldChange}
            onSubmit={onSubmit}
            onEdit={onEdit}
            onDelete={onDelete}
            onCancel={onCancel}
          />
        ))}
      </div>

      {showImportSection ? (
        <article className="card-block config-card">
          <h2>Importacion masiva</h2>

          <form className="form-grid" onSubmit={onImportSubmit}>
            <label>
              Tipo de dato maestro
              <select
                value={importState.selectedResourceType}
                onChange={(event) =>
                  onImportFieldChange("selectedResourceType", event.target.value)
                }
              >
                {importState.templates.map((template) => (
                  <option key={template.resource_type} value={template.resource_type}>
                    {template.resource_type}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Archivo CSV/XLSX
              <input
                type="file"
                accept=".csv,.xlsx"
                onChange={(event) =>
                  onImportFieldChange("file", event.target.files?.[0] || null)
                }
              />
            </label>

            {importState.error ? <p className="error-text">{importState.error}</p> : null}

            <div className="actions-inline">
              <button type="button" className="secondary" onClick={onDownloadTemplate}>
                Descargar plantilla CSV
              </button>
              <button type="submit" disabled={importState.submitting}>
                {importState.submitting ? "Importando..." : "Importar"}
              </button>
            </div>
          </form>

          {importState.result ? (
            <div className="config-items-list">
              <p className="hint">
                Total: {importState.result.total_processed} | Exitosos: {importState.result.successful} |
                Fallidos: {importState.result.failed}
              </p>

              {importState.result.rows.map((row) => (
                <div key={`${row.row}-${row.status}-${row.message}`} className="config-item-row">
                  <div>
                    <strong>Fila {row.row}</strong>
                    <p className="hint small">
                      {row.status === "success" ? "OK" : "Error"}: {row.message}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : null}
        </article>
      ) : null}
    </section>
  );
}
