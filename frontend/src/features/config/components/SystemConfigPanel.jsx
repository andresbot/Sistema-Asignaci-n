import { useEffect, useRef, useState } from "react";
import { EmptyState, EmptyListIcon } from "../../../shared/components/EmptyState";
import { Modal } from "../../../shared/components/Modal";
import { RowMenu } from "../../../shared/components/RowMenu";
import { useToast } from "../../../shared/components/Toast";

const SECTION_DEFINITIONS = {
  classTypes: {
    step: 1,
    group: "Configuracion base",
    title: "Tipos de clase",
    fields: [
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "description", label: "Descripcion", type: "text", required: false },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  academicSpaceTypes: {
    step: 2,
    group: "Configuracion base",
    title: "Tipos de espacio academico",
    fields: [
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "description", label: "Descripcion", type: "text", required: false },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  campuses: {
    step: 3,
    group: "Configuracion base",
    title: "Campus",
    fields: [
      { name: "code", label: "Codigo", type: "text", required: true },
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  periods: {
    step: 4,
    group: "Configuracion base",
    title: "Periodo academico",
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
    step: 5,
    group: "Disponibilidad horaria",
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
    step: 6,
    group: "Disponibilidad horaria",
    title: "Franjas horarias",
    fields: [
      { name: "name", label: "Nombre", type: "text", required: true },
      { name: "start_time", label: "Hora inicio", type: "time", required: true },
      { name: "end_time", label: "Hora fin", type: "time", required: true },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  classrooms: {
    step: 7,
    group: "Infraestructura",
    title: "Salones",
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
  academicPrograms: {
    step: 8,
    group: "Oferta academica",
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
  subjects: {
    step: 9,
    group: "Oferta academica",
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
    step: 10,
    group: "Oferta academica",
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
    step: 11,
    group: "Oferta academica",
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
      {
        name: "requires_accessible_classroom",
        label: "Estudiantes con discapacidad",
        type: "checkbox",
        required: false,
      },
      { name: "semester", label: "Semestre", type: "number", required: true, min: 1 },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
  teacherLinkTypes: {
    step: null,
    group: "Docentes",
    title: "Tipos de vinculacion docente",
    fields: [
      { name: "name", label: "Nombre", type: "text", required: false },
      { name: "description", label: "Descripcion", type: "text", required: false },
      { name: "is_active", label: "Activo", type: "checkbox", required: false },
    ],
  },
};

const LARGE_FORM_SECTIONS = new Set(["subjectOfferings", "classrooms", "subjects"]);

function SectionFormFields({ sectionKey, sectionState, fields, configState, onFieldChange }) {
  return (
    <>
      {fields.map((field) => {
        if (field.type === "checkbox") {
          return (
            <label key={field.name} className="checkbox-row">
              <input
                type="checkbox"
                checked={Boolean(sectionState.form[field.name])}
                onChange={(e) => onFieldChange(sectionKey, field.name, e.target.checked)}
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
                  (opt) =>
                    String(opt.subject?.id ?? opt.subject_id ?? "") ===
                    String(sectionState.form.subject_id ?? ""),
                )
              : sectionKey === "subjectOfferings" &&
                  (field.name === "working_day_id" || field.name === "time_slot_id")
                ? (configState?.[field.optionsFrom]?.items ?? []).filter(
                    (opt) => opt.is_active !== false,
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
                onChange={(e) => onFieldChange(sectionKey, field.name, e.target.value)}
              >
                <option value="">Selecciona una opcion</option>
                {options.map((opt) => (
                  <option key={opt.id ?? opt.value} value={opt.id ?? opt.value}>
                    {buildOptionLabel(opt)}
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
              onChange={(e) => onFieldChange(sectionKey, field.name, e.target.value)}
            />
            {sectionState.fieldErrors?.[field.name] ? (
              <p className="error-text small">{sectionState.fieldErrors[field.name]}</p>
            ) : null}
          </label>
        );
      })}

      {sectionKey === "subjects" ? (
        <p className="hint">
          Dificultad calculada:{" "}
          {Number(sectionState.form.weekly_hours || 0) * Number(sectionState.form.capacity || 0)}
        </p>
      ) : null}
    </>
  );
}

function ConfigSectionCard({
  sectionKey,
  step,
  title,
  sectionState,
  fields,
  configState,
  onFieldChange,
  onSubmit,
  onEdit,
  onDelete,
  onCancel,
  onPublishPeriod,
  onUnpublishPeriod,
}) {
  const toast = useToast();
  const [modalOpen, setModalOpen] = useState(false);
  const wasSubmitting = useRef(false);
  const pendingModeRef = useRef("create");

  useEffect(() => {
    if (wasSubmitting.current && !sectionState.submitting && !sectionState.error) {
      setModalOpen(false);
      if (pendingModeRef.current === "create") {
        toast.success(`${title} creado correctamente.`);
      } else {
        toast.success(`${title} actualizado correctamente.`);
      }
    }
    wasSubmitting.current = sectionState.submitting;
  }, [sectionState.submitting, sectionState.error]);

  function openAdd() {
    pendingModeRef.current = "create";
    onCancel(sectionKey);
    setModalOpen(true);
  }

  function openEdit(item) {
    pendingModeRef.current = "edit";
    onEdit(sectionKey, item);
    setModalOpen(true);
  }

  function closeModal() {
    setModalOpen(false);
    onCancel(sectionKey);
  }

  async function handleDeleteClick(id) {
    const result = await onDelete(sectionKey, id);
    if (result === true) {
      toast.success(`Registro de ${title} eliminado.`);
    } else if (result === false) {
      toast.error("No fue posible eliminar el registro.");
    }
  }

  const isEditing = Boolean(sectionState.editId);
  const modalTitle = isEditing ? `Editar — ${title}` : `Agregar — ${title}`;
  const modalSize = LARGE_FORM_SECTIONS.has(sectionKey) ? "lg" : "md";

  return (
    <article className="card-block config-card">
      <div className="config-card-header">
        <h2>
          {step != null ? (
            <span className="config-step-badge">{step}</span>
          ) : null}
          {title}
        </h2>
        <button type="button" onClick={openAdd}>
          + Agregar
        </button>
      </div>

      <div className="config-items-list">
        {sectionState.loading ? <p className="hint">Cargando...</p> : null}

        {!sectionState.loading && sectionState.items.length === 0 ? (
          <EmptyState
            icon={<EmptyListIcon />}
            title="Sin registros aun"
            description={`Agrega el primero con "+ Agregar".`}
          />
        ) : null}

        {sectionState.items.map((item) => (
          <div key={item.id} className="config-item-row">
            <div>
              <strong>{item.name || item.code || `Registro ${item.id}`}</strong>
              <p className="hint small">{buildItemSummary(sectionKey, item)}</p>
            </div>
            <RowMenu
              items={[
                sectionKey === "periods"
                  ? {
                      label: item.is_schedule_published ? "Despublicar" : "Publicar horario",
                      onClick: () =>
                        item.is_schedule_published
                          ? onUnpublishPeriod(item.id)
                          : onPublishPeriod(item.id),
                    }
                  : null,
                { label: "Editar", onClick: () => openEdit(item) },
                { label: "Eliminar", onClick: () => handleDeleteClick(item.id), danger: true },
              ]}
            />
          </div>
        ))}
      </div>

      <Modal open={modalOpen} title={modalTitle} onClose={closeModal} size={modalSize}>
        <form className="form-grid" onSubmit={(e) => onSubmit(sectionKey, e)}>
          <SectionFormFields
            sectionKey={sectionKey}
            sectionState={sectionState}
            fields={fields}
            configState={configState}
            onFieldChange={onFieldChange}
          />

          {sectionState.error ? <p className="error-text">{sectionState.error}</p> : null}

          <div className="actions-inline">
            <button type="submit" disabled={sectionState.submitting}>
              {sectionState.submitting
                ? "Guardando..."
                : isEditing
                  ? "Guardar cambios"
                  : "Crear"}
            </button>
            <button type="button" className="secondary" onClick={closeModal}>
              Cancelar
            </button>
          </div>
        </form>
      </Modal>
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
    return `${item.subject?.code || item.subject_id || "Asignatura"} | ${item.identifier} | ${item.is_active ? "Activo" : "Inactivo"}`;
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
    const accessibility = item.requires_accessible_classroom
      ? "Requiere accesibilidad"
      : "Sin restriccion de accesibilidad";
    const cupo =
      item.student_count !== null && item.student_count !== undefined
        ? `Cupo ${item.student_count}`
        : "Sin cupo";
    return `${programCode} | ${subjectCode} | ${groupIdentifier} | ${workingDay} | ${timeSlot} | S${item.semester} | ${spaceType} | ${teacher} | ${cupo} | ${accessibility}`;
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
  if (option.label && option.value) return option.label;
  if (option.day_of_week && option.name) return `${option.day_of_week} - ${option.name}`;
  if (option.start_time && option.end_time) return `${option.start_time} - ${option.end_time}`;
  if (option.first_name !== undefined && option.last_name !== undefined) {
    return `${option.first_name} ${option.last_name}`.trim();
  }
  if (option.subject && option.identifier) return `${option.subject.code} - ${option.identifier}`;
  if (option.name && option.code) return `${option.code} - ${option.name}`;
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
  onPublishPeriod,
  onUnpublishPeriod,
  visibleSections,
  title = "Configuracion general del sistema",
  description,
  showImportSection = true,
}) {
  const sectionEntries = Object.entries(SECTION_DEFINITIONS).filter(([sectionKey]) => {
    if (!visibleSections || visibleSections.length === 0) return true;
    return visibleSections.includes(sectionKey);
  });

  return (
    <section className="panel-card dashboard-card system-config-panel">
      <header className="page-header">
        <h1 className="page-title">{title}</h1>
        <button className="secondary" type="button" onClick={onRefresh}>
          Recargar
        </button>
      </header>

      <div className="config-grid">
        {sectionEntries.map(([sectionKey, sectionDefinition]) => (
              <ConfigSectionCard
                key={sectionKey}
                sectionKey={sectionKey}
                step={sectionDefinition.step}
                title={sectionDefinition.title}
                sectionState={configState[sectionKey]}
                fields={sectionDefinition.fields}
                configState={configState}
                onFieldChange={onFieldChange}
                onSubmit={onSubmit}
                onEdit={onEdit}
                onDelete={onDelete}
                onCancel={onCancel}
                onPublishPeriod={onPublishPeriod}
                onUnpublishPeriod={onUnpublishPeriod}
              />
            ))}
      </div>

      {showImportSection ? (
        <article className="card-block config-card" style={{ marginTop: 16 }}>
          <h2>Importacion masiva</h2>
          <form className="form-grid" onSubmit={onImportSubmit}>
            <label>
              Tipo de dato maestro
              <select
                value={importState.selectedResourceType}
                onChange={(e) => onImportFieldChange("selectedResourceType", e.target.value)}
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
                onChange={(e) => onImportFieldChange("file", e.target.files?.[0] || null)}
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
            <div className="config-items-list" style={{ marginTop: 14 }}>
              <p className="hint">
                Total: {importState.result.total_processed} | Exitosos:{" "}
                {importState.result.successful} | Fallidos: {importState.result.failed}
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
