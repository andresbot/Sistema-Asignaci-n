import { useCallback, useEffect, useState } from "react";
import { fetchCampuses, fetchHorario, fetchNoAsignadas } from "../services/scheduleApi";

export function useSchedule({ authToken, periodos, enabled }) {
  const [campuses, setCampuses] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [unassigned, setUnassigned] = useState([]);
  const [campusId, setCampusId] = useState("");
  const [periodoId, setPeriodoId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const activePeriod = periodos?.find((p) => p.is_active);

  useEffect(() => {
    if (!enabled || !authToken) return;

    fetchCampuses(authToken)
      .then((data) => setCampuses(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, [enabled, authToken]);

  useEffect(() => {
    if (activePeriod && !periodoId) {
      setPeriodoId(String(activePeriod.id));
    }
  }, [activePeriod, periodoId]);

  const loadHorario = useCallback(async () => {
    if (!authToken || !periodoId) return;
    setLoading(true);
    setError(null);
    try {
      const [horarioData, noAsignadasData] = await Promise.all([
        fetchHorario(authToken, { periodoId, campusId: campusId || undefined }),
        fetchNoAsignadas(authToken, { periodoId }),
      ]);
      setAssignments(horarioData?.assignments ?? []);
      setUnassigned(noAsignadasData?.unassigned ?? []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [authToken, periodoId, campusId]);

  useEffect(() => {
    if (!enabled) return;
    loadHorario();
  }, [enabled, loadHorario]);

  return {
    campuses,
    assignments,
    unassigned,
    campusId,
    periodoId,
    loading,
    error,
    setCampusId,
    setPeriodoId,
    reload: loadHorario,
  };
}
