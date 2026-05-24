import { coreApiRequest } from "../../../shared/api/coreApiClient";

export function listSchedulePeriods(token) {
  return coreApiRequest("/programming/periods/", { token });
}

export function fetchMySchedule(token, academicPeriodId) {
  return coreApiRequest(`/programming/my-schedule/?academic_period_id=${academicPeriodId}`, {
    token,
  });
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
