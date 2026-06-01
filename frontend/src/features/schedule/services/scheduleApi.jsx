import { coreApiRequest } from "../../../shared/api/coreApiClient";

export function listSchedulePeriods(token) {
  return coreApiRequest("/programming/periods/", { token });
}

export function fetchMySchedule(token, academicPeriodId) {
  return coreApiRequest(`/programming/my-schedule/?academic_period_id=${academicPeriodId}`, {
    token,
  });
}

export function listScheduleExecutions(token, { periodId, status } = {}) {
  const params = new URLSearchParams();
  if (periodId) params.set("period_id", periodId);
  if (status) params.set("status", status);
  const query = params.toString() ? `?${params.toString()}` : "";
  return coreApiRequest(`/programming/schedule-executions/${query}`, { token });
}

export function createScheduleExecution(token, payload) {
  return coreApiRequest("/programming/schedule-executions/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function fetchScheduleExecution(token, id) {
  return coreApiRequest(`/programming/schedule-executions/${id}/`, { token });
}

export function fetchScheduleValidation(token, periodId) {
  const params = new URLSearchParams();
  if (periodId) params.set("period_id", periodId);
  const query = params.toString() ? `?${params.toString()}` : "";
  return coreApiRequest(`/programming/schedule-validation/${query}`, { token });
}

export async function fetchCampuses(token) {
  return coreApiRequest("/master-data/campuses/", { token });
}

export async function fetchPrograms(token, campusId) {
  const query = campusId ? `?campus_id=${campusId}` : "";
  return coreApiRequest(`/master-data/programs/${query}`, { token });
}

export async function fetchHorario(token, { periodoId, campusId, programId, semester } = {}) {
  const params = new URLSearchParams();
  if (periodoId) params.set("period_id", periodoId);
  if (campusId) params.set("campus_id", campusId);
  if (programId) params.set("program_id", programId);
  if (semester) params.set("semester", semester);
  const query = params.toString() ? `?${params.toString()}` : "";
  return coreApiRequest(`/horario/${query}`, { token });
}

export async function fetchNoAsignadas(token, { periodoId, campusId, programId, semester } = {}) {
  const params = new URLSearchParams();
  if (periodoId) params.set("period_id", periodoId);
  if (campusId) params.set("campus_id", campusId);
  if (programId) params.set("program_id", programId);
  if (semester) params.set("semester", semester);
  const query = params.toString() ? `?${params.toString()}` : "";
  return coreApiRequest(`/horario/no-asignadas/${query}`, { token });
}
