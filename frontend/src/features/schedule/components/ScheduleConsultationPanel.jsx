import { useEffect, useMemo, useState } from "react";

import { fetchMySchedule, listSchedulePeriods } from "../services/scheduleApi";

function formatDateLabel(item) {
  return `${item.start_date} - ${item.end_date}`;
}

function buildScheduleKey(item) {
  const day = item.working_day?.day_of_week ?? item.working_day?.name ?? "";
  const slot = item.time_slot?.start_time ?? "";
  return `${day}-${slot}-${item.id}`;
}

export function ScheduleConsultationPanel({ authToken, currentUser, onLogout }) {
  const [periods, setPeriods] = useState([]);
  const [selectedPeriodId, setSelectedPeriodId] = useState("");
  const [scheduleItems, setScheduleItems] = useState([]);
  const [loadingPeriods, setLoadingPeriods] = useState(false);
  const [loadingSchedule, setLoadingSchedule] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    const loadPeriods = async () => {
      setLoadingPeriods(true);
      setError("");

      try {
        const response = await listSchedulePeriods(authToken);
        if (!mounted) {
          return;
        }

        setPeriods(response);
        // Select the most recent published period, or fallback to the most recent period
        const publishedPeriods = response.filter((period) => period.is_schedule_published);
        const defaultPeriod = publishedPeriods[0] || response[0];
        if (defaultPeriod) {
          setSelectedPeriodId(String(defaultPeriod.id));
        }
      } catch (requestError) {
        if (mounted) {
          setError(requestError.message || "No se pudieron cargar los periodos.");
        }
      } finally {
        if (mounted) {
          setLoadingPeriods(false);
        }
      }
    };

    loadPeriods();

    return () => {
      mounted = false;
    };
  }, [authToken]);

  useEffect(() => {
    if (!selectedPeriodId) {
      setScheduleItems([]);
      return;
    }

    let mounted = true;

    const loadSchedule = async () => {
      setLoadingSchedule(true);
      setError("");

      try {
        const response = await fetchMySchedule(authToken, selectedPeriodId);
        if (mounted) {
          setScheduleItems(response);
        }
      } catch (requestError) {
        if (mounted) {
          setScheduleItems([]);
          setError(requestError.message || "No se pudo cargar el horario.");
        }
      } finally {
        if (mounted) {
          setLoadingSchedule(false);
        }
      }
    };

    loadSchedule();

    return () => {
      mounted = false;
    };
  }, [authToken, selectedPeriodId]);

  const selectedPeriod = useMemo(
    () => periods.find((period) => String(period.id) === String(selectedPeriodId)),
    [periods, selectedPeriodId],
  );

  const sortedItems = useMemo(() => {
    return [...scheduleItems].sort((left, right) => {
      const dayDiff = Number(left.working_day?.day_of_week ?? 0) - Number(right.working_day?.day_of_week ?? 0);
      if (dayDiff !== 0) {
        return dayDiff;
      }

      const leftTime = left.time_slot?.start_time || "";
      const rightTime = right.time_slot?.start_time || "";
      return leftTime.localeCompare(rightTime);
    });
  }, [scheduleItems]);

  return (
    <main className="app-shell schedule-shell">
      <section className="panel-card schedule-card">
        <header className="dashboard-header schedule-header">
          <div>
            <p className="eyebrow">Consulta de horario</p>
            <h1>Horario por periodo academico</h1>
            <p className="lead compact">
                Vista de solo lectura para {currentUser?.role || "usuario"}. Selecciona un periodo académico con horario publicado.
            </p>
          </div>

          <button className="ghost" onClick={onLogout}>
            Cerrar sesion
          </button>
        </header>

        <div className="schedule-toolbar">
          <label>
            Periodo academico
            <select
              value={selectedPeriodId}
              onChange={(event) => setSelectedPeriodId(event.target.value)}
              disabled={loadingPeriods || periods.length === 0}
            >
              <option value="">Selecciona un periodo</option>
              {periods.map((period) => (
                <option key={period.id} value={period.id}>
                  {period.code} | {formatDateLabel(period)} | {period.is_schedule_published ? "Publicado" : "Borrador"}
                </option>
              ))}
            </select>
          </label>

          <div className="schedule-status-stack">
            <span className={selectedPeriod?.is_schedule_published ? "status-pill success" : "status-pill warning"}>
              {selectedPeriod?.is_schedule_published ? "Publicado" : "Sin publicar"}
            </span>
            {selectedPeriod ? (
              <p className="hint small">
                {selectedPeriod.code} · {formatDateLabel(selectedPeriod)}
              </p>
            ) : null}
          </div>
        </div>

        {error ? <p className="error-text">{error}</p> : null}
        {loadingSchedule ? <p className="hint">Cargando horario...</p> : null}

        {!loadingSchedule && selectedPeriod && !selectedPeriod.is_schedule_published ? (
          <article className="empty-state schedule-empty">
            <h2>Horario no disponible</h2>
            <p className="hint">
              Este periodo aún no ha sido publicado. Cuando el administrador lo publique, podrás consultarlo aquí.
            </p>
          </article>
        ) : null}

        {!loadingSchedule && selectedPeriod?.is_schedule_published && sortedItems.length === 0 ? (
          <article className="empty-state schedule-empty">
            <h2>No hay registros</h2>
            <p className="hint">No se encontraron asignaciones para el periodo seleccionado.</p>
          </article>
        ) : null}

        {sortedItems.length > 0 ? (
          <div className="schedule-grid">
            {sortedItems.map((item) => (
              <article key={buildScheduleKey(item)} className="card-block schedule-item-card">
                <div className="schedule-item-topline">
                  <strong>{item.subject?.code || "Asignatura"}</strong>
                  <span className="status-pill">S{item.semester}</span>
                </div>
                <h2>{item.subject?.name || "Sin nombre"}</h2>
                <p className="hint">Grupo: {item.subject_group?.identifier || "Sin grupo"}</p>
                <p className="hint">
                  {item.working_day?.name || "Sin dia"} · {item.time_slot ? `${item.time_slot.start_time} - ${item.time_slot.end_time}` : "Sin franja"}
                </p>
                <p className="hint">Programa: {item.academic_program?.name || "Sin programa"}</p>
                <p className="hint">
                  Docente: {item.teacher ? `${item.teacher.first_name} ${item.teacher.last_name}`.trim() : "Sin docente"}
                </p>
              </article>
            ))}
          </div>
        ) : null}
      </section>
    </main>
  );
}
