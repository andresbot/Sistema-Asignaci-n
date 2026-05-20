import { coreApiRequest } from "../../../shared/api/coreApiClient";

export function listSchedulePeriods(token) {
  return coreApiRequest("/programming/periods/", { token });
}

export function fetchMySchedule(token, academicPeriodId) {
  return coreApiRequest(`/programming/my-schedule/?academic_period_id=${academicPeriodId}`, {
    token,
  });
}
