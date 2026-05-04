import {
  coreApiMultipartRequest,
  coreApiRequest,
} from "../../../shared/api/coreApiClient";

export function listPeriods(token) {
  return coreApiRequest("/config/periods/", { token });
}

export function createPeriod(token, payload) {
  return coreApiRequest("/config/periods/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updatePeriod(token, id, payload) {
  return coreApiRequest(`/config/periods/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deletePeriod(token, id) {
  return coreApiRequest(`/config/periods/${id}/`, {
    method: "DELETE",
    token,
  });
}

export function listWorkingDays(token) {
  return coreApiRequest("/config/working-days/", { token });
}

export function createWorkingDay(token, payload) {
  return coreApiRequest("/config/working-days/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateWorkingDay(token, id, payload) {
  return coreApiRequest(`/config/working-days/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deleteWorkingDay(token, id) {
  return coreApiRequest(`/config/working-days/${id}/`, {
    method: "DELETE",
    token,
  });
}

export function listTimeSlots(token) {
  return coreApiRequest("/config/time-slots/", { token });
}

export function createTimeSlot(token, payload) {
  return coreApiRequest("/config/time-slots/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateTimeSlot(token, id, payload) {
  return coreApiRequest(`/config/time-slots/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deleteTimeSlot(token, id) {
  return coreApiRequest(`/config/time-slots/${id}/`, {
    method: "DELETE",
    token,
  });
}

export function listSpaceTypes(token) {
  return coreApiRequest("/config/space-types/", { token });
}

export function createSpaceType(token, payload) {
  return coreApiRequest("/config/space-types/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateSpaceType(token, id, payload) {
  return coreApiRequest(`/config/space-types/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deleteSpaceType(token, id) {
  return coreApiRequest(`/config/space-types/${id}/`, {
    method: "DELETE",
    token,
  });
}

export function listCampuses(token) {
  return coreApiRequest("/master-data/campuses/", { token });
}

export function createCampus(token, payload) {
  return coreApiRequest("/master-data/campuses/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateCampus(token, id, payload) {
  return coreApiRequest(`/master-data/campuses/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deleteCampus(token, id) {
  return coreApiRequest(`/master-data/campuses/${id}/`, {
    method: "DELETE",
    token,
  });
}

export function listAcademicPrograms(token) {
  return coreApiRequest("/master-data/programs/", { token });
}

export function createAcademicProgram(token, payload) {
  return coreApiRequest("/master-data/programs/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateAcademicProgram(token, id, payload) {
  return coreApiRequest(`/master-data/programs/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deleteAcademicProgram(token, id) {
  return coreApiRequest(`/master-data/programs/${id}/`, {
    method: "DELETE",
    token,
  });
}

export function listCatalogItemsByType(token, catalogType, onlyActive = false) {
  const query = onlyActive ? "?is_active=true" : "";
  return coreApiRequest(`/catalogs/${catalogType}/${query}`, { token });
}

export function createCatalogItemByType(token, catalogType, payload) {
  return coreApiRequest(`/catalogs/${catalogType}/`, {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateCatalogItemByType(token, catalogType, id, payload) {
  return coreApiRequest(`/catalogs/${catalogType}/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deactivateCatalogItemByType(token, catalogType, id) {
  return coreApiRequest(`/catalogs/${catalogType}/${id}/`, {
    method: "DELETE",
    token,
  });
}

export function listImportTemplates(token) {
  return coreApiRequest("/imports/master-data/", { token });
}

export function importMasterData(token, resourceType, file) {
  const formData = new FormData();
  formData.append("resource_type", resourceType);
  formData.append("file", file);

  return coreApiMultipartRequest("/imports/master-data/", {
    method: "POST",
    token,
    formData,
  });
}

export function listSubjects(token) {
  return coreApiRequest("/programming/subjects/", { token });
}

export function createSubject(token, payload) {
  return coreApiRequest("/programming/subjects/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateSubject(token, id, payload) {
  return coreApiRequest(`/programming/subjects/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deleteSubject(token, id) {
  return coreApiRequest(`/programming/subjects/${id}/`, {
    method: "DELETE",
    token,
  });
}

export function listSubjectGroups(token) {
  return coreApiRequest("/programming/subject-groups/", { token });
}

export function createSubjectGroup(token, payload) {
  return coreApiRequest("/programming/subject-groups/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateSubjectGroup(token, id, payload) {
  return coreApiRequest(`/programming/subject-groups/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deleteSubjectGroup(token, id) {
  return coreApiRequest(`/programming/subject-groups/${id}/`, {
    method: "DELETE",
    token,
  });
}

export function listSubjectOfferings(token) {
  return coreApiRequest("/programming/subject-offerings/", { token });
}

export function createSubjectOffering(token, payload) {
  return coreApiRequest("/programming/subject-offerings/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateSubjectOffering(token, id, payload) {
  return coreApiRequest(`/programming/subject-offerings/${id}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deleteSubjectOffering(token, id) {
  return coreApiRequest(`/programming/subject-offerings/${id}/`, {
    method: "DELETE",
    token,
  });
}
