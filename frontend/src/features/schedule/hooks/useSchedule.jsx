import { useCallback, useEffect, useState } from "react";
import { fetchCampuses, fetchHorario, fetchNoAsignadas, fetchPrograms } from "../services/scheduleApi";

export function useSchedule({ authToken, periodos, enabled }) {
  const [campuses, setCampuses] = useState([]);
  const [programs, setPrograms] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [unassigned, setUnassigned] = useState([]);
  const [campusId, setCampusIdRaw] = useState("");
  const [programId, setProgramId] = useState("");
  const [semester, setSemester] = useState("");
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

  // When campus changes, reload programs and reset dependent filters
  const setCampusId = useCallback(
    (id) => {
      setCampusIdRaw(id);
      setProgramId("");
      if (!authToken) return;
      fetchPrograms(authToken, id)
        .then((data) => {
          const items = Array.isArray(data) ? data : (data?.results ?? []);
          setPrograms(items);
        })
        .catch(() => setPrograms([]));
    },
    [authToken],
  );

  const loadHorario = useCallback(async () => {
    if (!authToken || !periodoId) return;
    setLoading(true);
    setError(null);
    try {
      const params = {
        periodoId,
        campusId: campusId || undefined,
        programId: programId || undefined,
        semester: semester || undefined,
      };
      const [horarioData, noAsignadasData] = await Promise.all([
        fetchHorario(authToken, params),
        fetchNoAsignadas(authToken, params),
      ]);
      setAssignments(horarioData?.assignments ?? []);
      setUnassigned(noAsignadasData?.unassigned ?? []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [authToken, periodoId, campusId, programId, semester]);

  useEffect(() => {
    if (!enabled) return;
    loadHorario();
  }, [enabled, loadHorario]);

  return {
    campuses,
    programs,
    assignments,
    unassigned,
    campusId,
    programId,
    semester,
    periodoId,
    loading,
    error,
    setCampusId,
    setProgramId,
    setSemester,
    setPeriodoId,
    reload: loadHorario,
  };
}
