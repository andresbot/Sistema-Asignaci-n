import { coreApiRequest } from "../../../shared/api/coreApiClient";

export async function fetchCampuses(token) {
  return coreApiRequest("/master-data/campuses/", { token });
}

export async function fetchHorario(token, { periodoId, campusId } = {}) {
  const params = new URLSearchParams();
  if (periodoId) params.set("period_id", periodoId);
  if (campusId) params.set("campus_id", campusId);
  const query = params.toString() ? `?${params.toString()}` : "";
  return coreApiRequest(`/horario/${query}`, { token });
}

export async function fetchNoAsignadas(token, { periodoId } = {}) {
  const params = new URLSearchParams();
  if (periodoId) params.set("period_id", periodoId);
  const query = params.toString() ? `?${params.toString()}` : "";
  return coreApiRequest(`/horario/no-asignadas/${query}`, { token });
}
