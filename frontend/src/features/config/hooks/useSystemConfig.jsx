import { useEffect, useState } from "react";

import {
  createCampus,
  createAcademicProgram,
  createCatalogItemByType,
  createPeriod,
  createSubject,
  createSubjectGroup,
  createSubjectOffering,
  createSpaceType,
  createTimeSlot,
  createWorkingDay,
  deactivateCatalogItemByType,
  deleteCampus,
  deletePeriod,
  deleteSubject,
  deleteSubjectGroup,
  deleteSubjectOffering,
  deleteSpaceType,
  deleteTimeSlot,
  deleteWorkingDay,
  deleteAcademicProgram,
  importMasterData,
  listCampuses,
  listAcademicPrograms,
  listCatalogItemsByType,
  listImportTemplates,
  listPeriods,
  listSubjects,
  listSubjectGroups,
  listSubjectOfferings,
  listSpaceTypes,
  listTimeSlots,
  listWorkingDays,
  updateCatalogItemByType,
  updateCampus,
  updateAcademicProgram,
  updatePeriod,
  updateSubject,
  updateSubjectGroup,
  updateSubjectOffering,
  updateSpaceType,
  updateTimeSlot,
  updateWorkingDay,
} from "../services/configApi";

function buildCatalogResource(catalogType) {
  return {
    list: (token) => listCatalogItemsByType(token, catalogType),
    create: (token, payload) => createCatalogItemByType(token, catalogType, payload),
    update: (token, id, payload) =>
      updateCatalogItemByType(token, catalogType, id, payload),
    remove: (token, id) => deactivateCatalogItemByType(token, catalogType, id),
    defaultForm: {
      name: "",
      description: "",
      is_active: true,
    },
    fieldOrder: ["name", "description", "is_active"],
  };
}

const RESOURCE_CONFIG = {
  campuses: {
    list: listCampuses,
    create: createCampus,
    update: updateCampus,
    remove: deleteCampus,
    defaultForm: {
      code: "",
      name: "",
      is_active: true,
    },
    fieldOrder: ["code", "name", "is_active"],
  },
  academicPrograms: {
    list: listAcademicPrograms,
    create: createAcademicProgram,
    update: updateAcademicProgram,
    remove: deleteAcademicProgram,
    defaultForm: {
      code: "",
      name: "",
      campus_id: "",
      is_active: true,
    },
    fieldOrder: ["code", "name", "campus_id", "is_active"],
  },
  subjects: {
    list: listSubjects,
    create: createSubject,
    update: updateSubject,
    remove: deleteSubject,
    defaultForm: {
      code: "",
      name: "",
      class_type_id: "",
      credits: "",
      weekly_hours: "",
      capacity: "",
      is_active: true,
    },
    fieldOrder: [
      "code",
      "name",
      "class_type_id",
      "credits",
      "weekly_hours",
      "capacity",
      "is_active",
    ],
  },
  subjectGroups: {
    list: listSubjectGroups,
    create: createSubjectGroup,
    update: updateSubjectGroup,
    remove: deleteSubjectGroup,
    defaultForm: {
      subject_id: "",
      identifier: "",
      is_active: true,
    },
    fieldOrder: ["subject_id", "identifier", "is_active"],
  },
  subjectOfferings: {
    list: listSubjectOfferings,
    create: createSubjectOffering,
    update: updateSubjectOffering,
    remove: deleteSubjectOffering,
    defaultForm: {
      subject_id: "",
      subject_group_id: "",
      academic_program_id: "",
      working_day_id: "",
      time_slot_id: "",
      semester: "",
      is_active: true,
    },
    fieldOrder: [
      "subject_id",
      "subject_group_id",
      "academic_program_id",
      "working_day_id",
      "time_slot_id",
      "semester",
      "is_active",
    ],
  },
  periods: {
    list: listPeriods,
    create: createPeriod,
    update: updatePeriod,
    remove: deletePeriod,
    defaultForm: {
      code: "",
      name: "",
      start_date: "",
      end_date: "",
      is_active: true,
    },
    fieldOrder: ["code", "name", "start_date", "end_date", "is_active"],
  },
  workingDays: {
    list: listWorkingDays,
    create: createWorkingDay,
    update: updateWorkingDay,
    remove: deleteWorkingDay,
    defaultForm: {
      day_of_week: "",
      name: "",
      is_active: true,
    },
    fieldOrder: ["day_of_week", "name", "is_active"],
  },
  timeSlots: {
    list: listTimeSlots,
    create: createTimeSlot,
    update: updateTimeSlot,
    remove: deleteTimeSlot,
    defaultForm: {
      name: "",
      start_time: "",
      end_time: "",
      is_active: true,
    },
    fieldOrder: ["name", "start_time", "end_time", "is_active"],
  },
  teacherLinkTypes: buildCatalogResource("teacher_link_type"),
  classTypes: buildCatalogResource("class_type"),
  academicSpaceTypes: buildCatalogResource("academic_space_type"),
};

function normalizeText(value) {
  return String(value ?? "").trim();
}

function buildDuplicateMatcher(resourceKey, form) {
  if (resourceKey === "periods") {
    return (item) => normalizeText(item.code).toLowerCase() === normalizeText(form.code).toLowerCase();
  }

  if (resourceKey === "workingDays") {
    return (item) => Number(item.day_of_week) === Number(form.day_of_week);
  }

  if (resourceKey === "timeSlots") {
    return (item) =>
      normalizeText(item.name).toLowerCase() === normalizeText(form.name).toLowerCase() &&
      item.start_time === form.start_time &&
      item.end_time === form.end_time;
  }

  return (item) => normalizeText(item.name).toLowerCase() === normalizeText(form.name).toLowerCase();
}

function validateForm(resourceKey, resourceState) {
  const { form, items, editId } = resourceState;

  // Subjects: validate duplicate by `code` on client side
  if (resourceKey === "subjects") {
    const duplicateCode = items
      .filter((item) => item.id !== editId)
      .some((item) => normalizeText(item.code).toLowerCase() === normalizeText(form.code).toLowerCase());

    if (duplicateCode) {
      return "Ya existe una asignatura con ese codigo.";
    }
  }

  if (resourceKey === "periods") {
    if (!normalizeText(form.code)) {
      return "El codigo del periodo es obligatorio.";
    }
    if (!normalizeText(form.name)) {
      return "El nombre del periodo es obligatorio.";
    }
    if (!form.start_date || !form.end_date) {
      return "Completa las fechas de inicio y fin del periodo.";
    }
    if (form.start_date > form.end_date) {
      return "La fecha de fin debe ser mayor o igual a la fecha de inicio.";
    }
  }

  if (resourceKey === "workingDays") {
    if (!normalizeText(form.name)) {
      return "El nombre del dia laborable es obligatorio.";
    }

    const dayOfWeek = Number(form.day_of_week);
    if (!Number.isInteger(dayOfWeek) || dayOfWeek < 1 || dayOfWeek > 7) {
      return "El dia laborable debe estar entre 1 y 7.";
    }
  }

  if (resourceKey === "timeSlots") {
    if (!normalizeText(form.name)) {
      return "El nombre de la franja es obligatorio.";
    }
    if (!form.start_time || !form.end_time) {
      return "Completa la hora de inicio y fin de la franja.";
    }
    if (form.start_time >= form.end_time) {
      return "La hora de fin debe ser mayor a la hora de inicio.";
    }
  }

  if (
    resourceKey === "teacherLinkTypes" ||
    resourceKey === "classTypes" ||
    resourceKey === "academicSpaceTypes"
  ) {
    if (!normalizeText(form.name)) {
      return "El nombre del catalogo es obligatorio.";
    }
  }

  const isDuplicate = items
    .filter((item) => item.id !== editId)
    .some((item) => {
      if (resourceKey === "subjectGroups") {
        const itemSubjectId = String(item.subject?.id ?? item.subject_id ?? "");
        const formSubjectId = String(form.subject_id ?? "");
        const itemIdentifier = String(item.identifier ?? "").trim().toLowerCase();
        const formIdentifier = String(form.identifier ?? "").trim().toLowerCase();
        return itemSubjectId === formSubjectId && itemIdentifier === formIdentifier;
      }

      return buildDuplicateMatcher(resourceKey, form)(item);
    });

  if (isDuplicate) {
    if (resourceKey === "periods") {
      return "Ya existe un periodo con ese codigo.";
    }
    if (resourceKey === "workingDays") {
      return "Ya existe ese dia laborable.";
    }
    if (resourceKey === "timeSlots") {
      return "Ya existe una franja con ese nombre y horario.";
    }
    return "Ya existe un valor para este tipo de catalogo con ese nombre.";
  }

  return "";
}

function buildInitialState() {
  return {
    academicPrograms: {
      items: [],
      form: { ...RESOURCE_CONFIG.academicPrograms.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
      editWarning: null,
    },
    campuses: {
      items: [],
      form: { ...RESOURCE_CONFIG.campuses.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
    },
    subjects: {
      items: [],
      form: { ...RESOURCE_CONFIG.subjects.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
    },
    subjectGroups: {
      items: [],
      form: { ...RESOURCE_CONFIG.subjectGroups.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
    },
    subjectOfferings: {
      items: [],
      form: { ...RESOURCE_CONFIG.subjectOfferings.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
      editWarning: null,
    },
    periods: {
      items: [],
      form: { ...RESOURCE_CONFIG.periods.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
      editWarning: null,
    },
    workingDays: {
      items: [],
      form: { ...RESOURCE_CONFIG.workingDays.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
    },
    timeSlots: {
      items: [],
      form: { ...RESOURCE_CONFIG.timeSlots.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
      editWarning: null,
    },
    teacherLinkTypes: {
      items: [],
      form: { ...RESOURCE_CONFIG.teacherLinkTypes.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
    },
    classTypes: {
      items: [],
      form: { ...RESOURCE_CONFIG.classTypes.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
    },
    academicSpaceTypes: {
      items: [],
      form: { ...RESOURCE_CONFIG.academicSpaceTypes.defaultForm },
      editId: null,
      loading: false,
      submitting: false,
      error: "",
      fieldErrors: {},
      editWarning: null,
    },
  };
}

function normalizePayload(resourceKey, form) {
  if (resourceKey === "campuses") {
    return {
      ...form,
      code: normalizeText(form.code),
      name: normalizeText(form.name),
    };
  }

  if (resourceKey === "periods") {
    return {
      ...form,
      code: normalizeText(form.code),
      name: normalizeText(form.name),
    };
  }

  if (resourceKey === "workingDays") {
    return {
      ...form,
      name: normalizeText(form.name),
      day_of_week: Number(form.day_of_week),
    };
  }

  if (resourceKey === "subjectOfferings") {
    return {
      ...form,
      subject_id: Number(form.subject_id),
      subject_group_id: Number(form.subject_group_id),
      academic_program_id: Number(form.academic_program_id),
      working_day_id: Number(form.working_day_id),
      time_slot_id: Number(form.time_slot_id),
      semester: Number(form.semester),
    };
  }

  if (resourceKey === "academicPrograms") {
    return {
      ...form,
      code: normalizeText(form.code),
      name: normalizeText(form.name),
      campus_id: Number(form.campus_id),
    };
  }

  if (resourceKey === "subjectGroups") {
    return {
      ...form,
      subject_id: Number(form.subject_id),
    };
  }

  if (resourceKey === "subjects") {
    return {
      ...form,
      credits: Number(form.credits),
      weekly_hours: Number(form.weekly_hours),
      capacity: Number(form.capacity),
      class_type_item_id: form.class_type_id ? Number(form.class_type_id) : null,
    };
  }

  if (resourceKey === "timeSlots") {
    return {
      ...form,
      name: normalizeText(form.name),
    };
  }

  if (
    resourceKey === "teacherLinkTypes" ||
    resourceKey === "classTypes" ||
    resourceKey === "academicSpaceTypes"
  ) {
    return {
      ...form,
      name: normalizeText(form.name),
      description: normalizeText(form.description),
    };
  }

  return form;
}

function mapItemToForm(resourceKey, item) {
  const fields = RESOURCE_CONFIG[resourceKey].fieldOrder;
  const form = {};

  fields.forEach((fieldName) => {
    form[fieldName] = item[fieldName];
  });

  if (resourceKey === "workingDays") {
    form.day_of_week = String(item.day_of_week);
  }

  if (resourceKey === "subjectOfferings") {
    form.subject_id = String(item.subject?.id ?? item.subject_id ?? "");
    form.subject_group_id = String(item.subject_group?.id ?? item.subject_group_id ?? "");
    form.academic_program_id = String(
      item.academic_program?.id ?? item.academic_program_id ?? "",
    );
    form.working_day_id = String(item.working_day?.id ?? item.working_day_id ?? "");
    form.time_slot_id = String(item.time_slot?.id ?? item.time_slot_id ?? "");
    form.semester = String(item.semester);
  }

  if (resourceKey === "subjectGroups") {
    form.subject_id = String(item.subject?.id ?? item.subject_id ?? "");
  }

  if (resourceKey === "academicPrograms") {
    form.campus_id = String(item.campus?.id ?? item.campus_id ?? "");
  }

  if (resourceKey === "subjects") {
    form.credits = String(item.credits);
    form.weekly_hours = String(item.weekly_hours);
    form.capacity = String(item.capacity);
    form.class_type_id = String(item.class_type_item?.id ?? "");
  }

  return form;
}

export function useSystemConfig({ authToken, enabled, role }) {
  const [state, setState] = useState(buildInitialState());
  const [importState, setImportState] = useState({
    templates: [],
    selectedResourceType: "class_type",
    file: null,
    submitting: false,
    error: "",
    result: null,
  });

  const getResourceKeysForRole = (role) => {
    if (role === "coordinador") {
      return [
        "subjectOfferings",
        "subjects",
        "subjectGroups",
        "academicPrograms",
        "campuses",
        "workingDays",
        "timeSlots",
      ];
    }

    return Object.keys(RESOURCE_CONFIG);
  };

  const setResourceState = (resourceKey, updater) => {
    setState((previous) => ({
      ...previous,
      [resourceKey]: updater(previous[resourceKey]),
    }));
  };

  const resetResourceForm = (resourceKey) => {
    setResourceState(resourceKey, (resourceState) => ({
      ...resourceState,
      editId: null,
      form: { ...RESOURCE_CONFIG[resourceKey].defaultForm },
      submitting: false,
      error: "",
      fieldErrors: {},
    }));
  };

  const loadResource = async (resourceKey) => {
    if (!authToken) {
      return;
    }

    const resourceApi = RESOURCE_CONFIG[resourceKey];

    setResourceState(resourceKey, (resourceState) => ({
      ...resourceState,
      loading: true,
      error: "",
    }));

    try {
      const items = await resourceApi.list(authToken);
      setResourceState(resourceKey, (resourceState) => ({
        ...resourceState,
        items,
        loading: false,
      }));
    } catch (error) {
      setResourceState(resourceKey, (resourceState) => ({
        ...resourceState,
        loading: false,
        error: error.message || "No fue posible cargar la configuracion.",
      }));
    }
  };

  const refreshAll = async (activeRole) => {
    const keys = getResourceKeysForRole(activeRole);
    await Promise.all(keys.map((key) => loadResource(key)));
  };

  const loadImportTemplates = async () => {
    if (!authToken) {
      return;
    }

    try {
      const response = await listImportTemplates(authToken);
      const templates = response.templates || [];

      setImportState((previous) => ({
        ...previous,
        templates,
        selectedResourceType:
          templates.find((item) => item.resource_type === previous.selectedResourceType)
            ?.resource_type || templates[0]?.resource_type || previous.selectedResourceType,
      }));
    } catch (error) {
      setImportState((previous) => ({
        ...previous,
        error: error.message || "No fue posible cargar las plantillas de importacion.",
      }));
    }
  };

  useEffect(() => {
    if (!enabled) {
      return;
    }

    refreshAll(role);
    loadImportTemplates();
  }, [authToken, enabled, role]);

  const handleImportFieldChange = (field, value) => {
    setImportState((previous) => ({
      ...previous,
      [field]: value,
      error: "",
    }));
  };

  const handleImportSubmit = async (event) => {
    event.preventDefault();
    if (!authToken) {
      return;
    }

    if (!importState.file) {
      setImportState((previous) => ({
        ...previous,
        error: "Debes seleccionar un archivo CSV o XLSX.",
      }));
      return;
    }

    const fileName = (importState.file.name || "").toLowerCase();
    if (!fileName.endsWith(".csv") && !fileName.endsWith(".xlsx")) {
      setImportState((previous) => ({
        ...previous,
        error: "Solo se permiten archivos CSV y XLSX.",
      }));
      return;
    }

    setImportState((previous) => ({
      ...previous,
      submitting: true,
      error: "",
      result: null,
    }));

    try {
      const result = await importMasterData(
        authToken,
        importState.selectedResourceType,
        importState.file,
      );

      setImportState((previous) => ({
        ...previous,
        submitting: false,
        file: null,
        result,
      }));

      await refreshAll();
    } catch (error) {
      setImportState((previous) => ({
        ...previous,
        submitting: false,
        error: error.message || "No fue posible importar los datos.",
      }));
    }
  };

  const handleDownloadTemplate = () => {
    const selectedTemplate = importState.templates.find(
      (template) => template.resource_type === importState.selectedResourceType,
    );

    if (!selectedTemplate?.headers?.length) {
      setImportState((previous) => ({
        ...previous,
        error: "No hay plantilla disponible para el tipo seleccionado.",
      }));
      return;
    }

    const csvContent = `${selectedTemplate.headers.join(",")}\n`;
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.setAttribute("download", `plantilla_${selectedTemplate.resource_type}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  const handleFieldChange = (resourceKey, field, value) => {
    if (resourceKey === "subjectOfferings" && field === "subject_id") {
      setResourceState(resourceKey, (resourceState) => ({
        ...resourceState,
        form: {
          ...resourceState.form,
          subject_id: value,
          subject_group_id: "",
        },
      }));
      return;
    }

    setResourceState(resourceKey, (resourceState) => ({
      ...resourceState,
      form: {
        ...resourceState.form,
        [field]: value,
      },
    }));
  };

  const handleSelectEdit = (resourceKey, item) => {
    setResourceState(resourceKey, (resourceState) => ({
      ...resourceState,
      editId: item.id,
      form: mapItemToForm(resourceKey, item),
      error: "",
      editWarning: item.edit_warning || null,
    }));
  };

  const handleDelete = async (resourceKey, itemId) => {
    if (!authToken) {
      return;
    }

    const approved = window.confirm("Deseas eliminar este registro?");
    if (!approved) {
      return;
    }

    const resourceApi = RESOURCE_CONFIG[resourceKey];

    try {
      await resourceApi.remove(authToken, itemId);
      await loadResource(resourceKey);

      setResourceState(resourceKey, (resourceState) => {
        if (resourceState.editId !== itemId) {
          return resourceState;
        }

        return {
          ...resourceState,
          editId: null,
          form: { ...resourceApi.defaultForm },
        };
      });
    } catch (error) {
      setResourceState(resourceKey, (resourceState) => ({
        ...resourceState,
        error: error.message || "No fue posible eliminar el registro.",
      }));
    }
  };

  const handleSubmit = async (resourceKey, event) => {
    event.preventDefault();
    if (!authToken) {
      return;
    }

    const resourceApi = RESOURCE_CONFIG[resourceKey];
    const resourceStateSnapshot = state[resourceKey];

    // If there's an edit warning (e.g., schedule already generated), ask confirmation
    if (resourceStateSnapshot.editWarning) {
      const confirmed = window.confirm(
        `${resourceStateSnapshot.editWarning}\n\n¿Desea continuar y guardar los cambios?`
      );
      if (!confirmed) {
        return;
      }
    }

    const validationError = validateForm(resourceKey, resourceStateSnapshot);
    if (validationError) {
      setResourceState(resourceKey, (resourceState) => ({
        ...resourceState,
        submitting: false,
        error: validationError,
      }));
      return;
    }

    setResourceState(resourceKey, (resourceState) => ({
      ...resourceState,
      submitting: true,
      error: "",
      fieldErrors: {},
    }));

    const payload = normalizePayload(resourceKey, resourceStateSnapshot.form);

    try {
      if (resourceStateSnapshot.editId) {
        await resourceApi.update(authToken, resourceStateSnapshot.editId, payload);
      } else {
        await resourceApi.create(authToken, payload);
      }

      await loadResource(resourceKey);
      resetResourceForm(resourceKey);
    } catch (error) {
      // Backend may return a validation object as JSON string; try to parse it
      let parsed = null;
      try {
        parsed = JSON.parse(error.message);
      } catch (e) {
        parsed = null;
      }

      if (parsed && typeof parsed === "object") {
        const fieldErrors = {};
        Object.keys(parsed).forEach((k) => {
          const v = parsed[k];
          fieldErrors[k] = Array.isArray(v) ? v[0] : String(v);
        });

        setResourceState(resourceKey, (resourceState) => ({
          ...resourceState,
          submitting: false,
          fieldErrors,
        }));
      } else {
        setResourceState(resourceKey, (resourceState) => ({
          ...resourceState,
          submitting: false,
          error: error.message || "No fue posible guardar el registro.",
        }));
      }

      return;
    }

    setResourceState(resourceKey, (resourceState) => ({
      ...resourceState,
      submitting: false,
    }));
  };

  return {
    configState: state,
    importState,
    refreshAll: () => refreshAll(role),
    handleFieldChange,
    handleDownloadTemplate,
    handleImportFieldChange,
    handleImportSubmit,
    handleSelectEdit,
    handleDelete,
    handleSubmit,
    resetResourceForm,
  };
}
