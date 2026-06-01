import { useEffect, useMemo, useState } from "react";

import { fetchMySchedule, listSchedulePeriods } from "../services/scheduleApi";

function formatDateLabel(item) {
  return `${item.start_date} - ${item.end_date}`;
}

function ScheduleChip({ item }) {
  const teacherName = item.teacher
    ? `${item.teacher.first_name} ${item.teacher.last_name}`.trim()
    : "Sin docente";
  const dayTime =
    item.working_day && item.time_slot
      ? `${item.working_day.name} · ${item.time_slot.start_time} - ${item.time_slot.end_time}`
      : null;

  return (
    <article className="card-block schedule-item-card">
      <div className="schedule-item-topline">
        <strong>{item.subject?.code || "Asignatura"}</strong>
        <span className="status-pill">S{item.semester}</span>
      </div>
      <h2>{item.subject?.name || "Sin nombre"}</h2>
      <p className="hint">Grupo: {item.subject_group?.identifier || "Sin grupo"}</p>
      {dayTime ? <p className="hint">{dayTime}</p> : null}
      <p className="hint">Programa: {item.academic_program?.name || "Sin programa"}</p>
      <p className="hint">Docente: {teacherName}</p>
      {item.sede ? <p className="hint">Sede: {item.sede}</p> : null}
      {item.salon ? <p className="hint">Salón: {item.salon}</p> : null}
    </article>
  );
}

function WeeklyGrid({ items }) {
  const { days, slots, grid } = useMemo(() => {
    const daysMap = new Map();
    const slotsMap = new Map();
    for (const item of items) {
      const d = item.working_day;
      const s = item.time_slot;
      if (d?.id) daysMap.set(d.id, d);
      if (s?.id) slotsMap.set(s.id, s);
    }
    const days = [...daysMap.values()].sort((a, b) => a.day_of_week - b.day_of_week);
    const slots = [...slotsMap.values()].sort((a, b) =>
      (a.start_time || "").localeCompare(b.start_time || ""),
    );
    const grid = new Map();
    for (const item of items) {
      if (!item.working_day?.id || !item.time_slot?.id) continue;
      const key = `${item.time_slot.id}-${item.working_day.id}`;
      if (!grid.has(key)) grid.set(key, []);
      grid.get(key).push(item);
    }
    return { days, slots, grid };
  }, [items]);

  return (
    <div className="schedule-table-wrap">
      <table className="schedule-table">
        <thead>
          <tr>
            <th className="schedule-th-slot">Franja</th>
            {days.map((d) => (
              <th key={d.id} className="schedule-th-day">
                {d.name}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {slots.map((slot) => (
            <tr key={slot.id}>
              <td className="schedule-td-slot">
                <strong>{slot.name || `${slot.start_time} – ${slot.end_time}`}</strong>
                <span className="hint small" style={{ display: "block" }}>
                  {slot.start_time?.slice(0, 5)} – {slot.end_time?.slice(0, 5)}
                </span>
              </td>
              {days.map((day) => {
                const cell = grid.get(`${slot.id}-${day.id}`) || [];
                if (cell.length === 0) {
                  return <td key={day.id} className="schedule-cell schedule-cell--empty" />;
                }
                return (
                  <td key={day.id} className="schedule-cell">
                    {cell.map((item) => (
                      <ScheduleChip key={item.id} item={item} />
                    ))}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function ScheduleConsultationPanel({ authToken, currentUser, onLogout }) {
  const [periods, setPeriods] = useState([]);
  const [selectedPeriodId, setSelectedPeriodId] = useState(null);
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
        const publishedPeriods = response.filter((p) => p.is_schedule_published);
        publishedPeriods.sort((a, b) => (b.start_date || "").localeCompare(a.start_date || ""));
        const defaultPeriod = publishedPeriods[0] || response[0];
        if (defaultPeriod) {
          setSelectedPeriodId(defaultPeriod.id);
        }
      } catch {
        if (mounted) {
          setError("No se pudieron cargar los periodos.");
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
    () => periods.find((p) => p.id === selectedPeriodId),
    [periods, selectedPeriodId],
  );

  return (
    <main className="app-shell schedule-shell">
      <section className="panel-card schedule-card">
        <header className="dashboard-header schedule-header">
          <div>
            <p className="eyebrow">Consulta de horario</p>
            <h1>Horario por periodo academico</h1>
            <p className="lead compact">
              Vista de solo lectura para {currentUser?.role || "usuario"}. Selecciona un periodo
              académico con horario publicado.
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
              value={selectedPeriodId ?? ""}
              onChange={(e) => setSelectedPeriodId(Number(e.target.value) || null)}
              disabled={loadingPeriods || periods.length === 0}
            >
              <option value="">Selecciona un periodo</option>
              {periods.map((period) => (
                <option key={period.id} value={period.id}>
                  {period.code} | {formatDateLabel(period)} |{" "}
                  {period.is_schedule_published ? "Publicado" : "Borrador"}
                </option>
              ))}
            </select>
          </label>

          <div className="schedule-status-stack">
            <span
              className={
                selectedPeriod?.is_schedule_published ? "status-pill success" : "status-pill warning"
              }
            >
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
              Este periodo aún no ha sido publicado. Cuando el administrador lo publique, podrás
              consultarlo aquí.
            </p>
          </article>
        ) : null}

        {!loadingSchedule && selectedPeriod?.is_schedule_published && scheduleItems.length === 0 ? (
          <article className="empty-state schedule-empty">
            <h2>No hay registros</h2>
            <p className="hint">No se encontraron asignaciones para el periodo seleccionado.</p>
          </article>
        ) : null}

        {scheduleItems.length > 0 ? <WeeklyGrid items={scheduleItems} /> : null}
      </section>
    </main>
  );
}
