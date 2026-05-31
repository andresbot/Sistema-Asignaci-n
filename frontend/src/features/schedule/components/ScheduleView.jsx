import { useEffect, useMemo, useState } from "react";

import {
  createScheduleExecution,
  fetchScheduleExecution,
  fetchScheduleValidation,
  listScheduleExecutions,
} from "../services/scheduleApi";
import { useSchedule } from "../hooks/useSchedule";
import { ScheduleGrid } from "./ScheduleGrid";
import { UnassignedList } from "./UnassignedList";

const SEMESTER_OPTIONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

export function ScheduleView({ authToken, periodos, canRunExecution = false }) {
  const {
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
    reload,
  } = useSchedule({ authToken, periodos, enabled: true });
  const [executions, setExecutions] = useState([]);
  const [executionForm, setExecutionForm] = useState({
    poblacion_size: 50,
    generaciones: 200,
    proporcion_heuristica: 0.3,
    estancamiento_max: 15,
  });
  const [executionLoading, setExecutionLoading] = useState(false);
  const [executionError, setExecutionError] = useState("");
  const [executionNotice, setExecutionNotice] = useState("");
  const [validationResult, setValidationResult] = useState(null);
  const [validationLoading, setValidationLoading] = useState(false);
  const [validationError, setValidationError] = useState("");

  const refreshExecutions = async () => {
    if (!canRunExecution || !authToken || !periodoId) {
      return;
    }

    try {
      const response = await listScheduleExecutions(authToken, { periodId: periodoId });
      setExecutions(Array.isArray(response) ? response : []);
    } catch (_error) {
      setExecutions([]);
    }
  };

  useEffect(() => {
    refreshExecutions();
  }, [authToken, canRunExecution, periodoId]);

  useEffect(() => {
    setValidationResult(null);
    setValidationError("");
    setExecutionError("");
    setExecutionNotice("");
  }, [periodoId]);

  useEffect(() => {
    const lastExecution = executions[0];
    if (
      !canRunExecution ||
      !authToken ||
      !periodoId ||
      !lastExecution ||
      ["completed", "failed"].includes(lastExecution.status)
    ) {
      return;
    }

    const intervalId = window.setInterval(async () => {
      try {
        const response = await fetchScheduleExecution(authToken, lastExecution.id);
        setExecutions((previous) => [response, ...previous.slice(1)]);
      } catch (_error) {
        window.clearInterval(intervalId);
      }
    }, 2500);

    return () => window.clearInterval(intervalId);
  }, [authToken, canRunExecution, periodoId, executions]);

  const latestExecution = useMemo(() => executions[0] || null, [executions]);

  const handleValidationSubmit = async () => {
    if (!authToken || !periodoId) {
      return;
    }

    setValidationLoading(true);
    setValidationError("");

    try {
      const response = await fetchScheduleValidation(authToken, periodoId);
      setValidationResult(response);
      if (response.can_run_algorithm) {
        setExecutionNotice("La validacion no encontro inconsistencias criticas.");
        setExecutionError("");
      } else {
        setExecutionNotice("");
        setExecutionError("La programacion tiene inconsistencias y no puede ejecutarse todavia.");
      }
    } catch (requestError) {
      setValidationResult(null);
      setValidationError(requestError.message || "No se pudo validar la programacion.");
    } finally {
      setValidationLoading(false);
    }
  };

  const handleExecutionSubmit = async (event) => {
    event.preventDefault();
    if (!authToken || !periodoId) {
      return;
    }

    setExecutionLoading(true);
    setExecutionError("");
    setExecutionNotice("");

    try {
      const response = await createScheduleExecution(authToken, {
        academic_period_id: periodoId,
        ...executionForm,
      });
      setExecutions((previous) => [response, ...previous]);
      setExecutionNotice("Solicitud de ejecucion creada correctamente.");
    } catch (requestError) {
      setExecutionError(requestError.message || "No se pudo crear la solicitud de ejecucion.");
    } finally {
      setExecutionLoading(false);
    }
  };

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
          Sede
          <select value={campusId} onChange={(e) => setCampusId(e.target.value)}>
            <option value="">Todas las sedes</option>
            {campuses.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Programa
          <select
            value={programId}
            onChange={(e) => setProgramId(e.target.value)}
            disabled={programs.length === 0}
          >
            <option value="">Todos los programas</option>
            {programs.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Semestre
          <select value={semester} onChange={(e) => setSemester(e.target.value)}>
            <option value="">Todos los semestres</option>
            {SEMESTER_OPTIONS.map((s) => (
              <option key={s} value={s}>
                Semestre {s}
              </option>
            ))}
          </select>
        </label>
      </div>

      {canRunExecution ? (
        <section className="card-block">
          <header className="dashboard-header" style={{ marginBottom: 12 }}>
            <div>
              <p className="eyebrow">Ejecucion</p>
              <h2>Solicitar generacion de horario</h2>
              <p className="hint compact">
                Este panel deja lista la solicitud de ejecucion para el motor de programacion.
              </p>
            </div>
          </header>

            <div className="card-block" style={{ marginBottom: 16 }}>
              <div className="dashboard-header" style={{ marginBottom: 12 }}>
                <div>
                  <p className="eyebrow">Validacion previa</p>
                  <h2>Revisar inconsistencias antes de ejecutar</h2>
                  <p className="hint compact">
                    Verifica cupo, docente, franja horaria y conflictos antes de lanzar el algoritmo.
                  </p>
                </div>
                <button type="button" className="secondary" onClick={handleValidationSubmit} disabled={validationLoading || !periodoId}>
                  {validationLoading ? "Validando..." : "Validar programacion"}
                </button>
              </div>

              {!periodoId ? <p className="hint">Selecciona un periodo academico para validar.</p> : null}
              {validationError ? <p className="error-text">{validationError}</p> : null}

              {validationResult ? (
                <div>
                  <p className={validationResult.can_run_algorithm ? "hint" : "error-text"}>
                    {validationResult.message}
                  </p>
                  <div className="stack-grid workspace-metrics" style={{ marginTop: 12 }}>
                    <article>
                      <span>Estados</span>
                      <strong>{validationResult.status}</strong>
                    </article>
                    <article>
                      <span>Problemas</span>
                      <strong>{validationResult.summary?.issues_count || 0}</strong>
                    </article>
                    <article>
                      <span>Franja / docente</span>
                      <strong>{(validationResult.summary?.missing_slot || 0) + (validationResult.summary?.missing_teacher || 0)}</strong>
                    </article>
                    <article>
                      <span>Capacidad / espacio</span>
                      <strong>{(validationResult.summary?.missing_capacity || 0) + (validationResult.summary?.missing_space_type || 0) + (validationResult.summary?.non_assignable_capacity || 0)}</strong>
                    </article>
                  </div>

                  {validationResult.issues?.length ? (
                    <ul className="hint" style={{ marginTop: 12, marginBottom: 0, paddingLeft: 18 }}>
                      {validationResult.issues.map((issue, index) => (
                        <li key={`${issue.code}-${index}`}>
                          <strong>{issue.title}:</strong> {issue.message}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              ) : null}
            </div>

          <form className="schedule-filters" onSubmit={handleExecutionSubmit}>
            <label>
              Tamano poblacion
              <input
                type="number"
                min="1"
                value={executionForm.poblacion_size}
                onChange={(event) =>
                  setExecutionForm((previous) => ({
                    ...previous,
                    poblacion_size: Number(event.target.value),
                  }))
                }
              />
            </label>

            <label>
              Generaciones
              <input
                type="number"
                min="1"
                value={executionForm.generaciones}
                onChange={(event) =>
                  setExecutionForm((previous) => ({
                    ...previous,
                    generaciones: Number(event.target.value),
                  }))
                }
              />
            </label>

            <label>
              Proporcion heuristica
              <input
                type="number"
                min="0"
                max="1"
                step="0.05"
                value={executionForm.proporcion_heuristica}
                onChange={(event) =>
                  setExecutionForm((previous) => ({
                    ...previous,
                    proporcion_heuristica: Number(event.target.value),
                  }))
                }
              />
            </label>

            <label>
              Estancamiento maximo
              <input
                type="number"
                min="0"
                value={executionForm.estancamiento_max}
                onChange={(event) =>
                  setExecutionForm((previous) => ({
                    ...previous,
                    estancamiento_max: Number(event.target.value),
                  }))
                }
              />
            </label>

            <div style={{ alignSelf: "end" }}>
              <button type="submit" disabled={executionLoading || !periodoId || !validationResult?.can_run_algorithm}>
                {executionLoading ? "Creando solicitud..." : "Ejecutar algoritmo"}
              </button>
            </div>
          </form>

          {!validationResult?.can_run_algorithm ? (
            <p className="hint" style={{ marginTop: 8 }}>
              Debes validar la programacion y corregir las inconsistencias antes de ejecutar.
            </p>
          ) : null}

          {executionError ? <p className="error-text">{executionError}</p> : null}
          {executionNotice ? <p className="hint">{executionNotice}</p> : null}

          {latestExecution ? (
            <article className="empty-state schedule-empty" style={{ marginTop: 16 }}>
              <h3>Ultima solicitud</h3>
              <p className="hint">Estado: {latestExecution.status}</p>
              <p className="hint">Progreso: {latestExecution.progress}%</p>
              <p className="hint">
                Periodo: {latestExecution.academic_period?.code || "sin periodo"}
              </p>
              {latestExecution.result_snapshot?.total_generations ? (
                <p className="hint">
                  Generacion: {latestExecution.result_snapshot.current_generation || 0} / {latestExecution.result_snapshot.total_generations}
                </p>
              ) : null}
              {latestExecution.error_message ? (
                <p className="error-text">{latestExecution.error_message}</p>
              ) : null}
              {latestExecution.result_snapshot?.summary ? (
                <div className="stack-grid workspace-metrics" style={{ marginTop: 12 }}>
                  <article>
                    <span>Asignaciones</span>
                    <strong>{latestExecution.result_snapshot.summary.total_assignments}</strong>
                  </article>
                  <article>
                    <span>No asignadas</span>
                    <strong>{latestExecution.result_snapshot.summary.total_unassigned}</strong>
                  </article>
                </div>
              ) : null}
            </article>
          ) : null}

          {latestExecution?.result_snapshot?.unassigned?.length ? (
            <article className="card-block" style={{ marginTop: 16 }}>
              <h3>No asignadas</h3>
              <ul className="hint" style={{ margin: 0, paddingLeft: 18 }}>
                {latestExecution.result_snapshot.unassigned.map((item) => (
                  <li key={item.id}>
                    {item.asignatura?.code || "Asignatura"} - {item.grupo?.name || "Sin grupo"}: {item.razon}
                  </li>
                ))}
              </ul>
            </article>
          ) : null}
        </section>
      ) : null}

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
