import { useSchedule } from "../hooks/useSchedule";
import { ScheduleGrid } from "./ScheduleGrid";
import { UnassignedList } from "./UnassignedList";

export function ScheduleView({ authToken, periodos }) {
  const {
    campuses,
    assignments,
    unassigned,
    campusId,
    periodoId,
    loading,
    error,
    setCampusId,
    setPeriodoId,
    reload,
  } = useSchedule({ authToken, periodos, enabled: true });

  return (
    <section className="panel-card dashboard-card schedule-view">
      <header className="dashboard-header">
        <div>
          <p className="eyebrow">Visualizacion</p>
          <h1>Horario generado</h1>
          <p className="lead compact">
            Grilla semanal de asignaciones por franja horaria y dia.
          </p>
        </div>
        <button className="secondary" onClick={reload} disabled={loading}>
          {loading ? "Cargando..." : "Recargar"}
        </button>
      </header>

      <div className="schedule-filters">
        <label>
          Periodo academico
          <select value={periodoId} onChange={(e) => setPeriodoId(e.target.value)}>
            <option value="">Todos los periodos</option>
            {periodos?.map((p) => (
              <option key={p.id} value={p.id}>
                {p.code} &mdash; {p.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Sede (campus)
          <select value={campusId} onChange={(e) => setCampusId(e.target.value)}>
            <option value="">Todas las sedes</option>
            {campuses.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {error ? <p className="error-text">{error}</p> : null}

      {loading ? (
        <p className="hint" style={{ textAlign: "center", padding: "32px 0" }}>
          Cargando horario...
        </p>
      ) : (
        <ScheduleGrid assignments={assignments} />
      )}

      <UnassignedList unassigned={unassigned} />
    </section>
  );
}
